export type ChatRoute =
  | { kind: 'home'; slot: 'new' }
  | { kind: 'new'; slot: 'new' }
  | { kind: 'saved'; slot: string; id: number }
  | { kind: 'unavailable'; slot: 'unavailable' }

export function chatRoute(target?: string): ChatRoute {
  if (target === undefined) return { kind: 'home', slot: 'new' }
  if (target === 'new') return { kind: 'new', slot: 'new' }
  const id = /^[1-9]\d*$/.test(target) ? Number(target) : NaN
  return Number.isSafeInteger(id) && id <= 2147483647
    ? { kind: 'saved', slot: String(id), id }
    : { kind: 'unavailable', slot: 'unavailable' }
}
