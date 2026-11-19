import { ChatForm } from '../../forms'
import { useCreateConversation } from '../../hooks'
import { PolicySelection } from './PolicySelection'

export function ChatSession() {
  const { result, selectPolicy, isPending, isError } = useCreateConversation()

  return (
    <>
      <PolicySelection
        result={result}
        isPending={isPending}
        isError={isError}
        onStart={selectPolicy}
      />
      <p>
        Mock chat only — replies are not coverage advice. Messages are not
        saved.
      </p>
      <ChatForm disabled={result?.status !== 'ready'} />
    </>
  )
}
