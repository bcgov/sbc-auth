import { ShortNameType, ShortNameTypeDescription } from '@/util/constants'

/**
 * A class to put all the common short name utility methods.
 */
export default class ShortNameUtils {
  // Header Filter item definitions used for drop down select
  static ShortNameTypeItems = [
    { text: ShortNameTypeDescription[ShortNameType.EFT], value: ShortNameType.EFT },
    { text: ShortNameTypeDescription[ShortNameType.WIRE], value: ShortNameType.WIRE }
  ]

  static getShortNameTypeDescription (type: string) {
    return type ? ShortNameTypeDescription[type] : type
  }
}
