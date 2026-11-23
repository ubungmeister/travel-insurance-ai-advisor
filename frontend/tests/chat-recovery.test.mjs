import assert from 'node:assert/strict'
import { after, test } from 'node:test'
import { createElement, useEffect } from 'react'
import TestRenderer, { act } from 'react-test-renderer'
import { renderToStaticMarkup } from 'react-dom/server'
import { createServer } from 'vite'
import { MemoryRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider, notifyManager } from '@tanstack/react-query'

// Flush query notifications inside React act rather than requiring arbitrary
// delays for React Query's default setTimeout-based notification scheduler.
notifyManager.setScheduler(queueMicrotask)

const server = await createServer({
  configFile: false,
  server: { middlewareMode: true, hmr: false },
  esbuild: { jsx: 'automatic' },
  plugins: [
    {
      name: 'stub-auth-session',
      enforce: 'pre',
      load(id) {
        if (id.replaceAll('\\', '/').endsWith('/src/lib/supabase.ts')) {
          return `export const supabase = { auth: { getSession: async () => ({ data: { session: { user: { id: 'alice' }, access_token: 'test' } } }) } }`
        }
      },
    },
  ],
})
after(() => server.close())

test('application theme uses a light palette', async () => {
  const { appTheme } = await server.ssrLoadModule('/src/app/theme.ts')
  assert.equal(appTheme.palette.mode, 'light')
})

const policy = {
  policy_id: 3,
  policy_number: 'P-3',
  plan_name: 'Travel plan',
  plan_version: 2,
  territory: 'EUROPE',
  trip_purpose: 'VACATION',
  sport_category: 'RECREATIONAL',
  start_date: '2026-11-19',
  end_date: '2026-11-29',
  status: 'ISSUED',
}
const detail = { conversation_id: 7, selected_policy: policy, messages: [] }
const requestId = 'c11bfdd9-7ab4-426e-8675-89d96360c9ef'

for (const [status, action] of [
  [404, 'restore'],
  [409, 'discard'],
  [422, 'restore'],
]) {
  test(`HTTP ${status} is recoverable after refresh without resending`, async (t) => {
    const page = await mount(t, 'new')
    const posts = []
    globalThis.fetch.mock.mockImplementation(async (url, options) => {
      if (options.method === 'POST') {
        posts.push(JSON.parse(options.body))
        return posts.length === 1
          ? Response.json({}, { status })
          : Response.json({ conversation_id: 7, messages: [] })
      }
      return Response.json(
        new URL(url).pathname.endsWith('/policies')
          ? [policy, { policy_id: 4 }]
          : [],
      )
    })
    await page.remount()
    act(() => page.state.selectPolicy(3))
    act(() => page.state.editDraft('Rejected text'))
    await act(async () => {
      await page.state.send()
    })
    act(() => page.state.editDraft('Newer draft'))
    await page.remount()
    assert.equal(page.state.rejected, true)
    await act(async () => {
      await page.state.retry()
    })
    assert.equal(posts.length, 1)
    if (action === 'restore') {
      act(() => page.state.resolveRejected('restore'))
      assert.equal(page.state.draft, 'Newer draft')
      assert.equal(page.state.recovery.message, 'Rejected text')
      act(() => page.state.editDraft(''))
      act(() => page.state.resolveRejected('restore'))
      assert.equal(page.state.draft, 'Rejected text')
    } else {
      act(() => page.state.resolveRejected('discard'))
      assert.equal(page.state.draft, 'Newer draft')
    }
    assert.equal(page.state.recovery, undefined)
    act(() => page.state.selectPolicy(4))
    await act(async () => {
      await page.state.send()
    })
    assert.equal(posts[1].policy_id, 4)
    assert.notEqual(posts[1].request_id, posts[0].request_id)
  })
}

test('explicit logout purges other tabs and missed events on same-account sign-in', async () => {
  const {
    broadcastDraftLogout,
    listenForDraftLogout,
    readDraft,
    syncDraftAccount,
    updateDraft,
  } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  const shared = storage()
  const [initiator, listening, suspended, otherAccount] = Array.from(
    { length: 4 },
    storage,
  )
  const events = new EventTarget()
  for (const tab of [initiator, listening, suspended, otherAccount]) {
    const account = tab === otherAccount ? 'bob' : 'alice'
    syncDraftAccount(account, tab, shared)
    updateDraft(account, 'new', () => ({ text: `${account} draft` }), tab)
  }
  // Reauthentication on the same account, without an explicit logout, preserves it.
  syncDraftAccount('alice', suspended, shared)
  assert.equal(readDraft('alice', 'new', suspended).text, 'alice draft')
  let heard = 0
  const stop = listenForDraftLogout(() => heard++, listening, shared, events)
  const stopOther = listenForDraftLogout(
    () => assert.fail('unrelated account purged'),
    otherAccount,
    shared,
    events,
  )
  const set = shared.setItem
  shared.setItem = (key, value) => {
    set(key, value)
    events.dispatchEvent(
      Object.assign(new Event('storage'), { key, storageArea: shared }),
    )
  }
  broadcastDraftLogout('alice', initiator, shared)
  assert.equal(heard, 1)
  assert.equal(readDraft('alice', 'new', initiator).text, '')
  assert.equal(readDraft('alice', 'new', listening).text, '')
  syncDraftAccount('alice', suspended, shared)
  assert.equal(readDraft('alice', 'new', suspended).text, '')
  assert.equal(readDraft('bob', 'new', otherAccount).text, 'bob draft')
  stop()
  stopOther()
})

test('confirmed send refreshes the activity and ordering of an older chat', async (t) => {
  const page = await mount(t, '7')
  const previous = { ...detail, last_activity_at: '2026-11-19T13:00:00Z' }
  const updated = { ...previous, last_activity_at: '2026-11-20T13:00:00Z' }
  const other = {
    ...detail,
    conversation_id: 8,
    last_activity_at: '2026-11-19T15:00:00Z',
  }
  let sent = false
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') {
      sent = true
      return Response.json({ conversation_id: 7, messages: [] })
    }
    return Response.json(
      new URL(url).pathname.endsWith('/7')
        ? detail
        : sent
          ? [updated, other]
          : [other, previous],
    )
  })
  await page.remount()
  assert.deepEqual(page.state.history, [other, previous])
  act(() => page.state.editDraft('Move up'))
  await act(async () => {
    await page.state.send()
  })
  assert.deepEqual(page.state.history, [updated, other])
})

function storage() {
  const data = new Map()
  return {
    get length() {
      return data.size
    },
    key: (index) => [...data.keys()][index] ?? null,
    getItem: (key) => data.get(key) ?? null,
    setItem: (key, value) => data.set(key, value),
    removeItem: (key) => data.delete(key),
  }
}

const historyEntries = [
  {
    conversation_id: 7,
    selected_policy: policy,
    created_at: '2026-11-19T13:00:00Z',
    last_activity_at: '2026-11-20T13:00:00Z',
  },
  {
    conversation_id: 8,
    selected_policy: null,
    created_at: '2026-11-19T13:00:00Z',
    last_activity_at: '2026-11-19T13:00:00Z',
  },
]

function renderView(t, view) {
  let renderer
  act(() => {
    renderer = TestRenderer.create(view)
  })
  t.after(() => act(() => renderer.unmount()))
  return renderer
}

function viewText(node) {
  if (typeof node === 'string') return node
  if (node.type === 'style') return ''
  return node.children.map(viewText).join('')
}

test('conversation history has one empty list and still offers New chat', async (t) => {
  const { ConversationHistory } = await server.ssrLoadModule(
    '/src/components/chat/ConversationHistory.tsx',
  )
  const { root } = renderView(
    t,
    createElement(ConversationHistory, {
      history: [],
      disabled: false,
      onSelect() {},
      onNew() {},
    }),
  )
  const nav = root.findByType('nav')
  assert.equal(nav.props['aria-label'], 'Conversation history')
  assert.equal(nav.findByType('ul').findAllByType('li').length, 0)
  assert.match(viewText(nav), /No conversations yet/i)
  const newChat = nav.findByType('button')
  assert.equal(viewText(newChat), 'New chat')
  assert.ok(!newChat.props.disabled)
})

test('conversation history marks only the active row and shows saved metadata', async (t) => {
  const { ConversationHistory } = await server.ssrLoadModule(
    '/src/components/chat/ConversationHistory.tsx',
  )
  const { root } = renderView(
    t,
    createElement(ConversationHistory, {
      history: historyEntries,
      conversationId: 8,
      disabled: false,
      onSelect() {},
      onNew() {},
    }),
  )
  const rows = root.findByType('ul').findAllByType('button')
  assert.equal(rows.length, 2)
  assert.match(viewText(rows[0]), /#7.*P-3/)
  assert.match(viewText(rows[1]), /#8/)
  assert.deepEqual(
    rows.map((row) => row.props['aria-current']),
    [undefined, 'page'],
  )
  const activity = rows[0].findByType('time')
  assert.equal(activity.props.dateTime, '2026-11-20T13:00:00Z')
  assert.match(viewText(activity), /2026/)
  assert.doesNotMatch(viewText(activity), /T13:00/)
})

test('conversation history forwards row and New chat actions and disables both when requested', async (t) => {
  const { ConversationHistory } = await server.ssrLoadModule(
    '/src/components/chat/ConversationHistory.tsx',
  )
  const selections = []
  let newChats = 0
  const view = (disabled) => createElement(ConversationHistory, {
    history: historyEntries,
    disabled,
    onSelect: (id) => selections.push(id),
    onNew: () => newChats++,
  })
  const renderer = renderView(t, view(false))
  const rows = renderer.root.findByType('ul').findAllByType('button')
  const newChat = renderer.root
    .findAllByType('button')
    .find((button) => viewText(button) === 'New chat')
  act(() => rows[1].props.onClick())
  act(() => newChat.props.onClick())
  assert.deepEqual(selections, [8])
  assert.equal(newChats, 1)
  act(() => renderer.update(view(true)))
  assert.ok(
    renderer.root.findAllByType('button').every((button) => button.props.disabled),
  )
})

test('chat history adapter navigates to the exact saved and new chat routes', async (t) => {
  const { ChatHistory } = await server.ssrLoadModule(
    '/src/components/chat/ChatHistory.tsx',
  )
  const { ChatSessionContext } = await server.ssrLoadModule(
    '/src/hooks/conversation/chat-session-context.ts',
  )
  const paths = []
  const { root } = renderView(
    t,
    createElement(
      ChatSessionContext.Provider,
      {
        value: {
          history: historyEntries,
          conversation: detail,
          navigate: (path) => paths.push(path),
        },
      },
      createElement(ChatHistory),
    ),
  )
  const [active, next] = root.findByType('ul').findAllByType('button')
  assert.equal(active.props['aria-current'], 'page')
  act(() => next.props.onClick())
  const newChat = root
    .findAllByType('button')
    .find((button) => viewText(button) === 'New chat')
  act(() => newChat.props.onClick())
  assert.deepEqual(paths, ['/chat/8', '/chat/new'])
})

async function policyPanelView() {
  const { ChatPolicyPanel } = await server.ssrLoadModule(
    '/src/components/chat/ChatPolicyPanel.tsx',
  )
  const { ChatSessionContext } = await server.ssrLoadModule(
    '/src/hooks/conversation/chat-session-context.ts',
  )
  return (state) =>
    createElement(
      ChatSessionContext.Provider,
      {
        value: {
          target: 'new',
          policies: [],
          loading: false,
          loadError: false,
          sending: false,
          ...state,
        },
      },
      createElement(ChatPolicyPanel),
    )
}

test('chat policy panel explains the no-policy state without offering a choice', async (t) => {
  const view = await policyPanelView()
  const { root } = renderView(t, view({}))
  const section = root.findByType('section')
  assert.equal(section.props['aria-label'], 'Chat policy')
  assert.equal(viewText(section.findByType('h2')), 'Chat policy')
  assert.match(viewText(section), /No policies linked/)
  assert.equal(section.findAllByType('button').length, 0)
})

test('chat policy panel shows one selected policy without a redundant chooser', async (t) => {
  const view = await policyPanelView()
  const { root } = renderView(t, view({ policies: [policy], policyId: 3 }))
  const section = root.findByType('section')
  assert.equal(section.props['aria-label'], 'Selected policy')
  assert.equal(viewText(section.findByType('h2')), 'Selected policy')
  assert.match(viewText(section), /P-3.*Travel plan.*EUROPE/)
  assert.match(viewText(section), /2026-11-19.*2026-11-29.*ISSUED/)
  assert.equal(root.findAllByType('button').length, 0)
})

test('chat policy panel forwards a choice, reflects selection and respects send and recovery locks', async (t) => {
  const view = await policyPanelView()
  const selections = []
  const state = {
    policies: [policy, { ...policy, policy_id: 4, policy_number: 'P-4' }],
    selectPolicy: (id) => selections.push(id),
  }
  const renderer = renderView(t, view(state))
  const choices = () => {
    const list = renderer.root.findByType('ul')
    assert.equal(list.props['aria-label'], 'Available policies')
    return list.findAllByType('button')
  }
  assert.deepEqual(choices().map(viewText), ['Choose P-3', 'Choose P-4'])
  assert.deepEqual(
    choices().map((button) => button.props['aria-pressed']),
    [false, false],
  )
  act(() => choices()[1].props.onClick())
  assert.deepEqual(selections, [4])
  act(() => renderer.update(view({ ...state, policyId: 4 })))
  assert.deepEqual(
    choices().map((button) => button.props['aria-pressed']),
    [false, true],
  )
  for (const locked of [
    { sending: true },
    { recovery: { request_id: requestId, policy_id: 4, message: 'Pending' } },
  ]) {
    act(() => renderer.update(view({ ...state, policyId: 4, ...locked })))
    assert.ok(choices().every((button) => button.props.disabled))
  }
})

async function mount(t, route) {
  const { useChatSessionController } = await server.ssrLoadModule(
    '/src/hooks/conversation/use-chat-session-controller.ts',
  )
  const tab = storage()
  t.mock.method(globalThis, 'fetch', async () => {
    throw new Error('Unexpected request')
  })
  let state
  let renderer
  const paths = []
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  const render = (target) => createElement(QueryClientProvider, { client }, createElement(Probe, { target }))
  const navigate = (path) => paths.push(path)
  function Probe({ target }) {
    const current = useChatSessionController('alice', target, navigate, tab)
    useEffect(() => {
      state = current
    })
    return null
  }
  async function remount(target = route) {
    await act(async () => {
      renderer?.unmount()
      renderer = TestRenderer.create(render(target))
    })
  }
  t.after(() => {
    act(() => renderer?.unmount())
    client.clear()
  })
  return {
    tab,
    client,
    paths,
    remount,
    unmount: () => {
      renderer?.unmount()
      renderer = undefined
    },
    get state() {
      return state
    },
  }
}

test('server reads populate account-scoped caches and confirmed sends reset mutation variables', async (t) => {
  const page = await mount(t, '7')
  let resolveSend
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') return new Promise((resolve) => { resolveSend = resolve })
    return Response.json(new URL(url).pathname.endsWith('/7') ? detail : [detail])
  })
  await page.remount()
  assert.deepEqual(page.client.getQueryData(['chat', 'alice', 'conversation', 7]), detail)
  assert.deepEqual(page.client.getQueryData(['chat', 'alice', 'history']), [detail])
  assert.equal(page.client.getQueryData(['chat', 'bob', 'conversation', 7]), undefined)
  act(() => page.state.editDraft('Do not retain in mutation observer'))
  let send
  await act(async () => { send = page.state.send() })
  const mutation = page.client.getMutationCache().getAll()[0]
  let detached = false
  const unsubscribe = page.client.getMutationCache().subscribe((event) => {
    if (event.type === 'observerRemoved' && event.mutation === mutation) detached = true
  })
  try {
    assert.ok(mutation)
    assert.equal(mutation.options.networkMode, 'always')
    assert.equal(mutation.options.retry, false)
    assert.equal(mutation.options.gcTime, 0)
    assert.equal(mutation.state.variables.message, 'Do not retain in mutation observer')
  } finally {
    // Settle the mocked transport even on assertion failure: real fetch rejects
    // on abort, whereas this deliberately controlled promise otherwise cannot.
    await act(async () => {
      resolveSend?.(Response.json({ conversation_id: 7, messages: [] }))
      await send
    })
    unsubscribe()
  }
  assert.equal(detached, true)
  assert.equal(page.state.recovery, undefined)
  assert.equal(page.state.sending, false)
})

test('discarding a rejected request clears its send warning as well as recovery', async (t) => {
  const page = await mount(t, '7')
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') return Response.json({}, { status: 422 })
    return Response.json(new URL(url).pathname.endsWith('/7') ? detail : [detail])
  })
  await page.remount()
  act(() => page.state.editDraft('Rejected'))
  await act(async () => { await page.state.send() })
  const mutation = page.client.getMutationCache().getAll()[0]
  assert.equal(mutation.state.variables.message, 'Rejected')
  let detached = false
  const unsubscribe = page.client.getMutationCache().subscribe((event) => {
    if (event.type === 'observerRemoved' && event.mutation === mutation) detached = true
  })
  act(() => page.state.resolveRejected('discard'))
  unsubscribe()
  assert.equal(detached, true)
  assert.equal(page.state.recovery, undefined)
  assert.equal(page.state.sendError, '')
})

test('confirmed retry reloads exact detail when its initial read failed', async (t) => {
  const page = await mount(t, '7')
  const { updateDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  updateDraft('alice', '7', () => ({ text: '', pending: {
    request_id: requestId, conversation_id: 7, message: 'Saved earlier',
  } }), page.tab)
  const turn = [{ id: 8, role: 'USER', content: 'Saved earlier' }, { id: 9, role: 'ASSISTANT', content: '(mocked) Saved' }]
  let reads = 0
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') return Response.json({ conversation_id: 7, messages: turn })
    if (new URL(url).pathname.endsWith('/7')) {
      reads++
      return reads === 1 ? Response.json({}, { status: 503 }) : Response.json({ ...detail, messages: turn })
    }
    return Response.json([detail])
  })
  await page.remount()
  assert.equal(page.state.loadError, true)
  assert.equal(page.state.conversation, null)
  await act(async () => { await page.state.retry() })
  assert.equal(reads, 2)
  assert.deepEqual(page.state.conversation.messages, turn)
  assert.equal(page.state.loadError, false)
  assert.equal(page.state.recovery, undefined)
})

test('extracted recovery view distinguishes retry from rejection and protects newer typing', async () => {
  const { PendingSendRecovery } = await server.ssrLoadModule('/src/components/chat/PendingSendRecovery.tsx')
  const { ChatSessionContext } = await server.ssrLoadModule('/src/hooks/conversation/chat-session-context.ts')
  const request = { request_id: requestId, policy_id: 3, message: 'Original' }
  const actions = []
  const state = { recovery: request, rejected: true, draft: 'Newer text', sending: false, loading: false, unavailable: false,
    retry: async () => actions.push('retry'), resolveRejected: (action) => actions.push(action) }
  const view = (value) => createElement(ChatSessionContext.Provider, { value }, createElement(PendingSendRecovery))
  let renderer
  act(() => { renderer = TestRenderer.create(view(state)) })
  try {
    const buttons = renderer.root.findAllByType('button')
    assert.deepEqual(buttons.map((button) => button.children.join('')), ['Restore rejected text', 'Discard rejected send'])
    assert.equal(buttons[0].props.disabled, true)
    act(() => buttons[1].props.onClick())
    assert.deepEqual(actions, ['discard'])
    act(() => renderer.update(view({ ...state, rejected: false })))
    assert.equal(renderer.root.findByType('button').children.join(''), 'Retry pending message')
  } finally {
    act(() => renderer.unmount())
  }
})

test('cached detail is hidden if exact conversation refetch returns 404', async (t) => {
  const page = await mount(t, '7')
  page.client.setQueryData(['chat', 'alice', 'conversation', 7], detail)
  globalThis.fetch.mock.mockImplementation(async (url) => new URL(url).pathname.endsWith('/7')
    ? Response.json({}, { status: 404 }) : Response.json([detail]))
  await page.remount()
  assert.equal(page.state.unavailable, true)
  assert.equal(page.state.conversation, null)
  assert.deepEqual(page.paths, [])
})

test('cached new-chat policies are not associated with an unavailable saved chat', async (t) => {
  const page = await mount(t, '7')
  page.client.setQueryData(['chat', 'alice', 'policies'], [policy])
  globalThis.fetch.mock.mockImplementation(async (url) => new URL(url).pathname.endsWith('/7')
    ? Response.json({}, { status: 404 }) : Response.json([detail]))
  await page.remount()
  assert.equal(page.state.unavailable, true)
  assert.equal(page.state.policyId, undefined)
  assert.deepEqual(page.state.policies, [])
})

test('failed history refetch cannot unconfirm a successful send', async (t) => {
  const page = await mount(t, '7')
  let sent = false
  const turn = [{ id: 3, role: 'USER', content: 'Saved' }, { id: 4, role: 'ASSISTANT', content: '(mocked) Saved' }]
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') {
      sent = true
      return Response.json({ conversation_id: 7, messages: turn })
    }
    if (new URL(url).pathname.endsWith('/7')) return Response.json(detail)
    return sent ? Response.json({}, { status: 503 }) : Response.json([detail])
  })
  await page.remount()
  act(() => page.state.editDraft('Saved'))
  await act(async () => { await page.state.send() })
  assert.deepEqual(page.state.conversation.messages, turn)
  assert.equal(page.state.recovery, undefined)
  assert.equal(page.state.sendError, '')
})

test('offline retry never queues or replaces a restored request', async (t) => {
  const page = await mount(t, '7')
  const { updateDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  const pending = { request_id: requestId, conversation_id: 7, message: 'Original' }
  updateDraft('alice', '7', () => ({ text: 'New typing', pending }), page.tab)
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  Object.defineProperty(globalThis, 'navigator', { configurable: true, value: { onLine: false } })
  t.after(() => {
    if (descriptor) Object.defineProperty(globalThis, 'navigator', descriptor)
    else delete globalThis.navigator
  })
  let posts = 0
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') posts++
    return Response.json(new URL(url).pathname.endsWith('/7') ? detail : [detail])
  })
  await page.remount()
  await act(async () => { await page.state.retry() })
  assert.equal(posts, 0)
  assert.equal(page.client.getMutationCache().getAll().length, 0)
  assert.deepEqual(page.state.recovery, pending)
})

test('account cleanup aborts sends and blocks late cache and recovery callbacks', async (t) => {
  const page = await mount(t, '7')
  let release
  let signal
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') {
      signal = options.signal
      return new Promise((resolve) => { release = resolve })
    }
    return Response.json(new URL(url).pathname.endsWith('/7') ? detail : [detail])
  })
  await page.remount()
  act(() => page.state.editDraft('Still awaiting confirmation'))
  let request
  await act(async () => { request = page.state.send() })
  const { resetChatServerState } = await server.ssrLoadModule('/src/lib/chat-account-boundary.ts')
  act(() => {
    resetChatServerState(page.client)
    page.unmount()
  })
  assert.equal(signal.aborted, true)
  await act(async () => {
    release(Response.json({ conversation_id: 7, messages: [] }))
    await request
  })
  assert.equal(page.client.getQueryCache().getAll().length, 0)
  assert.equal(page.client.getMutationCache().getAll().length, 0)
  assert.equal(page.paths.length, 0)
  // Cache cleanup alone must not delete tab recovery needed for reauthentication.
  const { readDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  assert.equal(readDraft('alice', '7', page.tab).pending.message, 'Still awaiting confirmation')
})

test('exact URL loads its transcript, never falls back when unavailable', async (t) => {
  const page = await mount(t, '7')
  const calls = []
  let unavailable = false
  globalThis.fetch.mock.mockImplementation(async (url) => {
    const path = new URL(url).pathname
    calls.push(path)
    if (path.endsWith('/7'))
      return unavailable
        ? Response.json({}, { status: 404 })
        : Response.json(detail)
    return Response.json([{ ...detail, conversation_id: 9 }])
  })
  await page.remount()
  assert.equal(page.state.conversation.conversation_id, 7)
  unavailable = true
  await page.remount()
  assert.equal(page.state.unavailable, true)
  assert.equal(page.state.conversation, null)
  assert.deepEqual(page.paths, [])
  assert.ok(!calls.some((path) => path.endsWith('/9')))
})

test('new draft restores policy and text without writing to backend', async (t) => {
  const page = await mount(t, 'new')
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    assert.notEqual(options.method, 'POST')
    return Response.json(
      new URL(url).pathname.endsWith('/policies')
        ? [policy, { policy_id: 4 }]
        : [],
    )
  })
  await page.remount()
  assert.equal(page.state.policyId, undefined)
  act(() => page.state.selectPolicy(3))
  act(() => page.state.editDraft('Unsent'))
  await page.remount()
  assert.equal(page.state.policyId, 3)
  assert.equal(page.state.draft, 'Unsent')
  assert.equal(page.state.recovery, undefined)
})

test('lost first response survives refresh; manual retry reuses exact payload and keeps newer draft', async (t) => {
  const page = await mount(t, 'new')
  const posts = []
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    const path = new URL(url).pathname
    if (path.endsWith('/chat')) {
      posts.push(JSON.parse(options.body))
      if (posts.length === 1) throw new TypeError('response lost after commit')
      return Response.json({ conversation_id: 7, messages: [] })
    }
    if (path.endsWith('/policies')) return Response.json([policy])
    return Response.json([])
  })
  await page.remount()
  act(() => page.state.editDraft('  exact message  '))
  await act(async () => {
    await page.state.send()
  })
  act(() => page.state.editDraft('Newer draft'))
  await page.remount()
  assert.equal(posts.length, 1)
  assert.equal(page.state.draft, 'Newer draft')
  assert.equal(page.state.recovery.message, '  exact message  ')
  await act(async () => {
    await page.state.retry()
  })
  assert.deepEqual(posts[0], posts[1])
  assert.match(posts[0].request_id, /^[\da-f-]{36}$/)
  assert.deepEqual(page.paths, ['/chat/7'])
  const { readDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  assert.equal(readDraft('alice', 'new', page.tab).pending, undefined)
  assert.equal(readDraft('alice', '7', page.tab).text, 'Newer draft')
})

test('confirmation clears only the matching recovery record; account change clears prior drafts', async () => {
  const {
    readDraft,
    updateDraft,
    confirmSend,
    syncDraftAccount,
    clearChatDrafts,
  } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  const tab = storage()
  syncDraftAccount('alice', tab)
  const pending = { request_id: requestId, policy_id: 3, message: 'exact' }
  updateDraft('alice', 'new', () => ({ text: 'keep', pending }), tab)
  assert.equal(confirmSend('alice', 'new', 'different', 7, tab), false)
  assert.deepEqual(readDraft('alice', 'new', tab).pending, pending)
  syncDraftAccount('alice', tab)
  assert.equal(readDraft('alice', 'new', tab).text, 'keep')
  syncDraftAccount('bob', tab)
  assert.equal(readDraft('alice', 'new', tab).pending, undefined)
  assert.equal(readDraft('alice', 'new', tab).text, '')
  updateDraft('bob', '7', () => ({ text: 'Bob draft' }), tab)
  clearChatDrafts(tab)
  assert.equal(readDraft('bob', '7', tab).text, '')
})

test('home selects latest saved URL or a new draft using reads only', async (t) => {
  const page = await mount(t, undefined)
  let history = [detail]
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    assert.equal(new URL(url).pathname, '/api/v1/conversations')
    assert.notEqual(options.method, 'POST')
    return Response.json(history)
  })
  await page.remount()
  history = []
  await page.remount()
  assert.deepEqual(page.paths, ['/chat/7', '/chat/new'])
})

test('offline first Send retains the draft and does not create a pending request', async (t) => {
  const page = await mount(t, 'new')
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, 'navigator')
  Object.defineProperty(globalThis, 'navigator', {
    configurable: true,
    value: { onLine: false },
  })
  t.after(() => {
    if (descriptor) Object.defineProperty(globalThis, 'navigator', descriptor)
    else delete globalThis.navigator
  })
  let posts = 0
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') posts++
    return Response.json(
      new URL(url).pathname.endsWith('/policies') ? [policy] : [],
    )
  })
  await page.remount()
  act(() => page.state.editDraft('Keep offline'))
  await act(async () => {
    await page.state.send()
  })
  assert.equal(posts, 0)
  assert.equal(page.state.recovery, undefined)
  assert.equal(page.state.draft, 'Keep offline')
  assert.match(page.state.sendError, /offline.*Nothing was sent/)
})

test('saved chat retry deduplicates replayed IDs and retains a draft typed during send', async (t) => {
  const page = await mount(t, '7')
  const messages = [
    { id: 2, role: 'USER', content: 'First' },
    { id: 3, role: 'ASSISTANT', content: '(mocked) First' },
  ]
  const { updateDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  updateDraft(
    'alice',
    '7',
    () => ({
      text: '',
      pending: { request_id: requestId, conversation_id: 7, message: 'First' },
    }),
    page.tab,
  )
  let reply
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') {
      assert.equal(JSON.parse(options.body).request_id, requestId)
      return new Promise((resolve) => {
        reply = resolve
      })
    }
    return Response.json(
      new URL(url).pathname.endsWith('/7') ? { ...detail, messages } : [detail],
    )
  })
  await page.remount()
  assert.equal(reply, undefined)
  let retry
  await act(async () => {
    retry = page.state.retry()
  })
  act(() => page.state.editDraft('Typed during send'))
  await act(async () => {
    reply(Response.json({ conversation_id: 7, messages }))
    await retry
  })
  assert.deepEqual(page.state.conversation.messages, messages)
  assert.equal(page.state.draft, 'Typed during send')
  assert.equal(page.state.recovery, undefined)
})

test('empty policy account never posts or creates recovery', async (t) => {
  const page = await mount(t, 'new')
  let posts = 0
  globalThis.fetch.mock.mockImplementation(async (_url, options) => {
    if (options.method === 'POST') posts++
    return Response.json([])
  })
  await page.remount()
  act(() => page.state.editDraft('No policy selected'))
  await act(async () => {
    await page.state.send()
  })
  assert.equal(posts, 0)
  assert.deepEqual(page.state.policies, [])
  assert.equal(page.state.recovery, undefined)
})

test('messages render oldest first and escape user text', async () => {
  const { ChatTranscript } = await server.ssrLoadModule(
    '/src/components/chat/ChatTranscript.tsx',
  )
  const html = renderToStaticMarkup(
    createElement(ChatTranscript, {
      messages: [
        { id: 2, role: 'USER', content: '<script>someone typed this</script>' },
        { id: 3, role: 'ASSISTANT', content: '(mocked) response' },
      ],
    }),
  )
  assert.match(html, /&lt;script&gt;/)
  assert.doesNotMatch(html, /<script>/)
  assert.ok(
    html.indexOf('someone typed this') < html.indexOf('(mocked) response'),
  )
})

test('rendering chat messages does not log the session or transcript', async (t) => {
  const { ChatSessionContext } = await server.ssrLoadModule(
    '/src/hooks/conversation/chat-session-context.ts',
  )
  const { ChatMessages } = await server.ssrLoadModule(
    '/src/components/chat/ChatMessages.tsx',
  )
  const logged = []
  t.mock.method(console, 'log', (...args) => logged.push(args))
  const session = {
    draft: 'private draft',
    conversation: {
      ...detail,
      messages: [{ id: 2, role: 'USER', content: 'private message' }],
    },
  }
  let renderer
  act(() => {
    renderer = TestRenderer.create(
      createElement(
        ChatSessionContext.Provider,
        { value: session },
        createElement(ChatMessages),
      ),
    )
  })
  assert.match(JSON.stringify(renderer.toJSON()), /private message/)
  assert.deepEqual(logged, [])
  act(() => renderer.unmount())
})

async function contextFixture(t) {
  const { ChatSessionProvider } = await server.ssrLoadModule('/src/components/chat/ChatSessionProvider.tsx')
  const { useChatSessionContext } = await server.ssrLoadModule('/src/hooks/conversation/use-chat-session-context.ts')
  const tab = storage()
  const descriptor = Object.getOwnPropertyDescriptor(globalThis, 'sessionStorage')
  Object.defineProperty(globalThis, 'sessionStorage', { configurable: true, value: tab })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  t.mock.method(globalThis, 'fetch', async (url, options) => {
    if (options.method === 'POST') return Response.json({}, { status: 422 })
    const path = new URL(url).pathname
    if (path.endsWith('/policies')) return Response.json([policy, { policy_id: 4, policy_number: 'P-4' }])
    return Response.json(path.endsWith('/7') ? detail : [])
  })
  const states = {}
  const paths = []
  function Consumer({ name }) {
    const value = useChatSessionContext()
    useEffect(() => { states[name] = value })
    return null
  }
  let renderer
  function tree(props = {}, children = ['one', 'two', 'three'].map((name) => createElement(Consumer, { name, key: name }))) {
    return createElement(QueryClientProvider, { client },
      createElement(MemoryRouter, null,
        createElement(ChatSessionProvider, { accountId: 'alice', target: 'new', navigate: (path) => paths.push(path), ...props }, children)))
  }
  async function render(props, children) {
    await act(async () => {
      if (renderer) renderer.update(tree(props, children))
      else renderer = TestRenderer.create(tree(props, children))
    })
  }
  t.after(() => {
    act(() => renderer?.unmount())
    client.clear()
    if (descriptor) Object.defineProperty(globalThis, 'sessionStorage', descriptor)
    else delete globalThis.sessionStorage
  })
  return { states, paths, tab, client, render, get root() { return renderer.root } }
}

test('chat consumers share one session and its draft instead of owning separate hooks', async (t) => {
  const fixture = await contextFixture(t)
  await fixture.render()
  assert.equal(fixture.states.one, fixture.states.two)
  assert.equal(fixture.states.one, fixture.states.three)
  act(() => fixture.states.one.selectPolicy(3))
  act(() => fixture.states.two.editDraft('Shared draft'))
  assert.equal(fixture.states.three.draft, 'Shared draft')
  assert.equal(fixture.states.three.policyId, 3)
  assert.equal(fixture.client.getMutationCache().getAll().length, 0)
})

test('provider scopes the controller by route, logout epoch and account', async (t) => {
  const fixture = await contextFixture(t)
  await fixture.render()
  act(() => fixture.states.one.editDraft('New chat draft'))
  await fixture.render({ target: '7' })
  assert.equal(fixture.states.one.draft, '')
  assert.equal(fixture.states.one.conversation.conversation_id, 7)
  await fixture.render({ target: 'new' })
  assert.equal(fixture.states.one.draft, 'New chat draft')
  const { clearChatDrafts } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  clearChatDrafts(fixture.tab)
  await fixture.render({ target: 'new', draftEpoch: 1 })
  assert.equal(fixture.states.one.draft, '')
  act(() => fixture.states.one.editDraft('Alice memory'))
  await fixture.render({ accountId: 'bob', target: 'new' })
  assert.equal(fixture.states.one.draft, '')
  assert.equal(fixture.states.one.recovery, undefined)
})

test('provider route change aborts a send and leaves its original recovery intact', async (t) => {
  const fixture = await contextFixture(t)
  let response
  let signal
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') {
      signal = options.signal
      return new Promise((resolve) => { response = resolve })
    }
    const path = new URL(url).pathname
    return Response.json(path.endsWith('/policies') ? [policy] : path.endsWith('/7') ? detail : [])
  })
  await fixture.render()
  act(() => fixture.states.one.editDraft('Uncertain first turn'))
  let send
  await act(async () => { send = fixture.states.one.send() })
  try {
    await fixture.render({ target: '7' })
    assert.equal(signal.aborted, true)
  } finally {
    // Always settle the fake transport; real fetch rejects on this abort.
    await act(async () => {
      response?.(Response.json({ conversation_id: 7, messages: [] }))
      await send
    })
  }
  const { readDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  assert.equal(readDraft('alice', 'new', fixture.tab).pending.message, 'Uncertain first turn')
  assert.deepEqual(fixture.paths, [])
  assert.equal(fixture.states.one.conversation.conversation_id, 7)
  assert.deepEqual(fixture.client.getQueryData(['chat', 'alice', 'conversation', 7]).messages, [])
})

test('chat layout keeps history in the sidebar and the transcript above the policy and composer', async (t) => {
  const fixture = await contextFixture(t)
  const { ChatSession } = await server.ssrLoadModule(
    '/src/components/chat/ChatSession.tsx',
  )
  const { updateDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  updateDraft('alice', '7', () => ({
    text: '',
    pending: {
      request_id: requestId,
      conversation_id: 7,
      message: 'Awaiting confirmation',
    },
  }), fixture.tab)
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') return Response.json({}, { status: 503 })
    if (new URL(url).pathname.endsWith('/7')) {
      return Response.json({
        ...detail,
        messages: [{ id: 1, role: 'USER', content: 'Saved message' }],
      })
    }
    return Response.json(historyEntries)
  })
  await fixture.render({ target: '7' }, createElement(ChatSession))

  const [sidebar] = fixture.root.findAllByType('aside')
  assert.ok(sidebar?.props['aria-label'], 'history needs a labeled sidebar')
  const history = sidebar.findByType('nav')
  assert.match(viewText(history), /Conversation #7/)

  const main = fixture.root.findByType('main')
  assert.equal(main.findAllByType('nav').length, 0)
  const transcript = main.findByType('ol')
  assert.match(viewText(transcript), /Saved message/)
  assert.deepEqual(
    main
      .findAll((node) => ['ol', 'section', 'form'].includes(node.type))
      .map((node) => node.props['aria-label'] ?? node.type),
    ['Chat messages', 'Pending send', 'Selected policy', 'form'],
  )
  const retry = main.findAllByType('button').find(
    (button) => viewText(button) === 'Retry pending message',
  )
  assert.ok(retry)
  await act(async () => retry.props.onClick())
  const status = main.findByProps({ role: 'alert' })
  assert.match(viewText(status), /Send could not be confirmed/)
})

test('consolidated chat styles preserve rendered layout and scrolling', async (t) => {
  const fixture = await contextFixture(t)
  const { ChatSession } = await server.ssrLoadModule('/src/components/chat/ChatSession.tsx')
  await fixture.render({}, createElement(ChatSession))
  const session = fixture.root.findByType(ChatSession)
  const styled = (predicate) => session.findAll((node) => node.props.sx && predicate(node.props))[0]
  const layout = styled(({ sx }) => sx.gridTemplateColumns)
  const history = styled(({ component }) => component === 'aside')
  const transcript = styled(({ 'aria-label': label }) => label === 'Transcript')
  const controls = styled(({ sx }) => sx.maxHeight?.md === '65%')
  assert.deepEqual(layout.props.sx.gridTemplateColumns, { xs: 'minmax(0, 1fr)', md: '17rem minmax(0, 1fr)' })
  assert.deepEqual(history.props.sx.maxHeight, { xs: '30dvh', md: 'none' })
  assert.equal(history.props.sx.overflowY, 'auto')
  assert.equal(transcript.props.sx.overflowY, 'auto')
  assert.equal(controls.props.sx.overflowY, 'auto')
})

test('consolidated chat styles preserve rendered message role variants', async (t) => {
  const { ChatTranscript } = await server.ssrLoadModule('/src/components/chat/ChatTranscript.tsx')
  const { root } = renderView(t, createElement(ChatTranscript, {
    messages: [
      { id: 1, role: 'USER', content: 'User message' },
      { id: 2, role: 'ASSISTANT', content: 'Assistant message' },
    ],
  }))
  const bubbles = root.findAll((node) => node.props.component === 'li' && node.props.sx)
  assert.equal(bubbles.length, 2)
  assert.equal(bubbles[0].props.sx.alignSelf, 'flex-end')
  assert.equal(bubbles[0].props.sx.bgcolor, 'primary.dark')
  assert.equal(bubbles[0].props.sx.color, 'primary.contrastText')
  assert.equal(bubbles[1].props.sx.alignSelf, 'flex-start')
  assert.equal(bubbles[1].props.sx.bgcolor, 'background.paper')
  assert.equal(bubbles[1].props.sx.color, 'text.primary')
  for (const bubble of bubbles) {
    const content = bubble.findAll((node) => node.props.sx?.whiteSpace === 'pre-wrap')[0]
    assert.ok(content, 'message preserves whitespace')
    assert.equal(content.props.sx.overflowWrap, 'anywhere')
  }
})

test('context-driven chat sections update and resolve recovery without state props', async (t) => {
  const fixture = await contextFixture(t)
  const { ChatSession } = await server.ssrLoadModule('/src/components/chat/ChatSession.tsx')
  await fixture.render({}, createElement(ChatSession))
  const choose = fixture.root.findAllByType('button').find((button) => button.children.join('') === 'Choose P-3')
  act(() => choose.props.onClick())
  assert.equal(fixture.root.findByType('input').props.maxLength, 2000)
  act(() => fixture.root.findByType('input').props.onChange({ target: { value: 'Rejected text' } }))
  await act(async () => { fixture.root.findByType('form').props.onSubmit({ preventDefault() {} }) })
  const restore = fixture.root.findAllByType('button').find((button) => button.children.join('') === 'Restore rejected text')
  assert.ok(restore)
  const main = fixture.root.findByType('main')
  assert.ok(main.findAllByType('button').includes(restore))
  act(() => restore.props.onClick())
  assert.equal(fixture.root.findByType('input').props.value, 'Rejected text')
  assert.equal(fixture.root.findAllByType('button').some((button) => button.children.join('') === 'Restore rejected text'), false)
})

test('session context fails explicitly outside its provider', async () => {
  const { useChatSessionContext } = await server.ssrLoadModule('/src/hooks/conversation/use-chat-session-context.ts')
  function Orphan() { useChatSessionContext(); return null }
  assert.throws(() => renderToStaticMarkup(createElement(Orphan)), /ChatSessionProvider/)
})

test('expired or changed auth cannot transmit a pending send with another account token', async (t) => {
  const page = await mount(t, '7')
  const { updateDraft } = await server.ssrLoadModule('/src/lib/chat-drafts.ts')
  const { supabase } = await server.ssrLoadModule('/src/lib/supabase.ts')
  const pending = {
    request_id: requestId,
    conversation_id: 7,
    message: 'Keep for Alice',
  }
  updateDraft('alice', '7', () => ({ text: '', pending }), page.tab)
  let account = 'alice'
  t.mock.method(supabase.auth, 'getSession', async () => ({
    data: {
      session: account
        ? { user: { id: account }, access_token: account }
        : null,
    },
  }))
  const payloads = []
  globalThis.fetch.mock.mockImplementation(async (url, options) => {
    if (options.method === 'POST') {
      assert.equal(options.headers.Authorization, 'Bearer alice')
      payloads.push(JSON.parse(options.body))
      return Response.json({ conversation_id: 7, messages: [] })
    }
    return Response.json(
      new URL(url).pathname.endsWith('/7') ? detail : [detail],
    )
  })
  await page.remount()
  for (const changed of [null, 'bob']) {
    account = changed
    await act(async () => {
      await page.state.retry()
    })
    assert.deepEqual(page.state.recovery, pending)
    assert.equal(page.state.reauthenticate, true)
    assert.deepEqual(payloads, [])
  }
  account = 'alice'
  await page.remount()
  assert.deepEqual(payloads, [])
  await act(async () => {
    await page.state.retry()
  })
  assert.deepEqual(payloads, [pending])
  assert.equal(page.state.recovery, undefined)
})
