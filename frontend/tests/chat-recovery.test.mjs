import assert from 'node:assert/strict'
import { after, test } from 'node:test'
import { createElement, useEffect } from 'react'
import TestRenderer, { act } from 'react-test-renderer'
import { renderToStaticMarkup } from 'react-dom/server'
import { createServer } from 'vite'

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

const policy = { policy_id: 3, policy_number: 'P-3' }
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

async function mount(t, route) {
  const { useChatSession } = await server.ssrLoadModule(
    '/src/hooks/conversation/use-chat-session.ts',
  )
  const tab = storage()
  t.mock.method(globalThis, 'fetch', async () => {
    throw new Error('Unexpected request')
  })
  let state
  let renderer
  const paths = []
  const navigate = (path) => paths.push(path)
  function Probe({ target }) {
    const current = useChatSession('alice', target, navigate, tab)
    useEffect(() => {
      state = current
    })
    return null
  }
  async function remount(target = route) {
    await act(async () => {
      renderer?.unmount()
      renderer = TestRenderer.create(createElement(Probe, { target }))
    })
  }
  t.after(() => act(() => renderer?.unmount()))
  return {
    tab,
    paths,
    remount,
    get state() {
      return state
    },
  }
}

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
