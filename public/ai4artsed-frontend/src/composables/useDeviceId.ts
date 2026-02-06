/**
 * Shared device ID composable.
 *
 * Combines a persistent browser identifier with the current date
 * so that the same physical device gets a new identity each day
 * (important for shared classroom iPads where different kids use
 * the same browser on different days).
 */
export function useDeviceId(): string {
  let browserId = localStorage.getItem('browser_id')
  if (!browserId) {
    browserId =
      crypto.randomUUID?.() ||
      `${Math.random().toString(36).substring(2, 10)}${Date.now().toString(36)}`
    localStorage.setItem('browser_id', browserId)
  }
  const today = new Date().toISOString().split('T')[0]
  return `${browserId}_${today}`
}
