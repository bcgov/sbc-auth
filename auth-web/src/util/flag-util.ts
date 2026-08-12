import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'

/**
 * Read a LaunchDarkly flag in a way that supports `false` values.
 *
 * sbc-common-components' LaunchDarklyService.getFlag() uses `||` chaining, so a
 * flag whose value is `false` always falls through to the default value. This
 * helper reads the flag set the LD service stores in session storage on init
 * and checks key existence instead, so `false` is returned correctly.
 */
export function getLdFlag (flagName: string, defaultValue: any = null): any {
  const ldFlags = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.LaunchDarklyFlags) || '{}')
  if (flagName in ldFlags) {
    return ldFlags[flagName]
  }
  return defaultValue
}
