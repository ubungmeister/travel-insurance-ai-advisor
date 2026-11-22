import type { ChatRequest, ChatResponse, ConversationDetail } from '../../api'

export function validateChatConfirmation(
  payload: ChatRequest,
  result: ChatResponse,
) {
  if (
    !Number.isSafeInteger(result.conversation_id) ||
    result.conversation_id <= 0 ||
    (payload.conversation_id !== undefined &&
      result.conversation_id !== payload.conversation_id) ||
    !Array.isArray(result.messages)
  ) {
    throw new Error('Invalid chat confirmation')
  }
}

/** Only merge into a full detail model; a first turn alone is not full detail. */
export function mergeChatTurn(
  current: ConversationDetail | undefined,
  result: ChatResponse,
) {
  if (!current) return undefined
  const messages = new Map(
    current.messages.map((message) => [message.id, message]),
  )
  result.messages.forEach((message) => messages.set(message.id, message))
  return {
    ...current,
    messages: [...messages.values()].sort((a, b) => a.id - b.id),
  }
}
