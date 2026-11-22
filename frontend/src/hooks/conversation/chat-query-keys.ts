export const chatKeys = {
  policies: (accountId: string) => ['chat', accountId, 'policies'] as const,
  history: (accountId: string) => ['chat', accountId, 'history'] as const,
  conversation: (accountId: string, id?: number) =>
    ['chat', accountId, 'conversation', id] as const,
  send: (accountId: string) => ['chat', accountId, 'send'] as const,
}
