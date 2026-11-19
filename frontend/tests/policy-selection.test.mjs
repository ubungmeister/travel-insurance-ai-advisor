import assert from 'node:assert/strict'
import { after, test } from 'node:test'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createServer } from 'vite'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const server = await createServer({
  configFile: false,
  server: { middlewareMode: true, hmr: false },
  esbuild: { jsx: 'automatic' },
  plugins: [
    {
      name: 'isolate-browser-auth-in-render-tests',
      enforce: 'pre',
      load(id) {
        // Rendering needs no auth/network. Avoid initializing the browser SDK
        // (which requires a native WebSocket unavailable on Node 20).
        if (id.replaceAll('\\', '/').endsWith('/src/lib/supabase.ts')) {
          return 'export const supabase = {}'
        }
      },
    },
  ],
})
after(() => server.close())
const { PolicySelection } = await server.ssrLoadModule(
  '/src/components/chat/PolicySelection.tsx',
)
const { ChatSession } = await server.ssrLoadModule(
  '/src/components/chat/ChatSession.tsx',
)
const { ChatForm } = await server.ssrLoadModule('/src/forms/chat/ChatForm.tsx')

const policy = {
  policy_id: 1,
  policy_number: 'POL-123',
  plan_name: 'Dominant',
  plan_version: 2,
  territory: 'EUROPE',
  trip_purpose: 'VACATION',
  sport_category: 'RECREATIONAL',
  start_date: '2026-11-01',
  end_date: '2026-11-30',
  status: 'ISSUED',
}
const choices = {
  status: 'selection_required',
  conversation_id: null,
  selected_policy: null,
  policy_choices: [
    policy,
    { ...policy, policy_id: 2, policy_number: 'POL-456' },
  ],
}
function render(props = {}) {
  return renderToStaticMarkup(
    createElement(PolicySelection, {
      isPending: false,
      isError: false,
      onStart: () => {},
      ...props,
    }),
  )
}

function buttonsIn(element) {
  if (!element || typeof element !== 'object') return []
  if (Array.isArray(element)) return element.flatMap(buttonsIn)
  if (element.type === 'button') return [element]
  return buttonsIn(element.props?.children)
}

test('initial policy state has no manual start action', () => {
  const view = PolicySelection({
    isPending: false,
    isError: false,
    onStart: () => {},
  })
  assert.equal(buttonsIn(view).length, 0)
})

test('policy actions submit the chosen policy ID rather than the first choice', () => {
  const calls = []
  const view = PolicySelection({
    result: choices,
    isPending: false,
    isError: false,
    onStart: (...args) => calls.push(args),
  })
  const buttons = buttonsIn(view)
  buttons[1].props.onClick()
  buttons[0].props.onClick()
  assert.deepEqual(calls, [[2], [1]])
})

test('initial policy resolution announces loading without a start screen', () => {
  const html = render()
  assert.match(html, /role="status"/)
  assert.doesNotMatch(html, /<button/)
  assert.doesNotMatch(html, /<form/)
})

test('no-policy controls explain how to proceed without wrapping chat', () => {
  const html = render({
    result: {
      status: 'no_policies',
      conversation_id: null,
      selected_policy: null,
      policy_choices: [],
    },
  })
  assert.match(html, /No policies linked/)
  assert.match(html, /contact support/i)
  assert.match(html, /Check again/)
  assert.doesNotMatch(html, /<form/)
})

test('multiple-policy state shows distinguishable choices and no chat form', () => {
  const html = render({ result: choices })
  for (const text of [
    'POL-123',
    'POL-456',
    'Dominant',
    'EUROPE',
    '2026-11-01',
    '2026-11-30',
    'ISSUED',
  ]) {
    assert.ok(html.includes(text), text)
  }
  assert.match(html, /Choose a policy/)
  assert.doesNotMatch(html, /<form/)
})

test('pending selection disables choices and announces progress', () => {
  const html = render({ result: choices, isPending: true })
  assert.equal((html.match(/disabled=""/g) ?? []).length, 2)
  assert.match(html, /role="status"/)
})

test('failed selection retains choices and offers useful recovery text', () => {
  const html = render({ result: choices, isError: true })
  assert.match(html, /role="alert"/)
  assert.match(html, /try again/i)
  assert.match(html, /POL-123/)
  assert.match(html, /POL-456/)
  assert.doesNotMatch(html, /<form/)
})

test('ready policy controls identify the selection without wrapping chat', () => {
  const html = render({
    result: {
      status: 'ready',
      conversation_id: 7,
      selected_policy: policy,
      policy_choices: [],
    },
  })
  assert.match(html, /Selected policy/)
  assert.match(html, /POL-123/)
  assert.doesNotMatch(html, /<form/)
})

test('chat is visible immediately while policy resolution is pending', () => {
  const queryClient = new QueryClient()
  try {
    const html = renderToStaticMarkup(
      createElement(
        QueryClientProvider,
        { client: queryClient },
        createElement(ChatSession),
      ),
    )
    assert.match(html, /<form/)
    assert.match(html, /aria-label="Message" disabled=""/)
    assert.match(html, /Mock chat only/)
    assert.match(html, /not coverage advice/)
    assert.match(html, /role="status"/)
    assert.doesNotMatch(html, />Start chat</)
  } finally {
    queryClient.clear()
  }
})

test('chat sending is enabled only when the policy gate allows it', () => {
  const queryClient = new QueryClient()
  function renderForm(disabled) {
    return renderToStaticMarkup(
      createElement(
        QueryClientProvider,
        { client: queryClient },
        createElement(ChatForm, { disabled }),
      ),
    )
  }
  try {
    const disabled = renderForm(true)
    assert.equal((disabled.match(/disabled=""/g) ?? []).length, 2)
    const enabled = renderForm(false)
    assert.doesNotMatch(enabled, /disabled=""/)
    assert.match(enabled, /<form/)
    assert.match(enabled, />Send</)
  } finally {
    queryClient.clear()
  }
})
