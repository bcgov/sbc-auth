import { SessionStorageKeys } from '@/util/constants'
import { getLdFlag } from '@/util/flag-util'

describe('getLdFlag', () => {
  afterEach(() => {
    sessionStorage.removeItem(SessionStorageKeys.LaunchDarklyFlags)
  })

  it('returns a false flag value instead of the default', () => {
    sessionStorage.setItem(SessionStorageKeys.LaunchDarklyFlags, JSON.stringify({ 'disable-account-linking': false }))
    expect(getLdFlag('disable-account-linking', true)).toBe(false)
  })

  it('returns the default when the flag is missing', () => {
    expect(getLdFlag('disable-account-linking', true)).toBe(true)
  })
})
