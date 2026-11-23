import { useLayoutEffect, useRef, type UIEvent } from 'react'

const transcriptFollowThreshold = 80

/**
 * Keeps a chat transcript at its newest messages when it first loads or when
 * messages arrive, but stops following while the reader is browsing older turns.
 */
export function useChatTranscriptAutoScroll(messageCount: number) {
  const transcriptRef = useRef<HTMLDivElement>(null)
  const shouldFollowTranscript = useRef(true)

  useLayoutEffect(() => {
    const transcript = transcriptRef.current
    if (!transcript || !shouldFollowTranscript.current) return
    transcript.scrollTop = transcript.scrollHeight
  }, [messageCount])

  function onTranscriptScroll(event: UIEvent<HTMLDivElement>) {
    const transcript = event.currentTarget
    shouldFollowTranscript.current =
      transcript.scrollHeight -
        transcript.clientHeight -
        transcript.scrollTop <=
      transcriptFollowThreshold
  }

  return { transcriptRef, onTranscriptScroll }
}
