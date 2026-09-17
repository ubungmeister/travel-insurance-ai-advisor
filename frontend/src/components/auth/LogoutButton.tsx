import { useLogout } from '../../hooks'

export function LogoutButton() {
  const { mutate, isPending } = useLogout()

  return (
    <button type="button" onClick={() => mutate()} disabled={isPending}>
      {isPending ? 'Signing out...' : 'Sign out'}
    </button>
  )
}
