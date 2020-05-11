/**
 * Place to put all the custom utility methods
 */
import moment from 'moment'

export default class CommonUtils {
  // checking url matches the regex
  static isUrl (value:string):boolean {
    const URL_MATCHER = new RegExp('^(?:\\w+:)?\\/\\/([^\\s\\.]+\\.\\S{2}|localhost[\\:?\\d]*)\\S*$')
    return URL_MATCHER.test(value)
  }
  // formatting incorporation number according to the length of numbers
  static formatIncorporationNumber (incorpNum:string, numLength?:number):string {
    numLength = numLength || 7 // optional: go with '7' if nothing specified
    const numberFirstIndex = incorpNum.search(/[0-9]/i)
    if (numberFirstIndex > -1) {
      // cut,trim and replace special characters from the first part
      let businessIdentifierStr = incorpNum.substring(0, numberFirstIndex).trim()
      businessIdentifierStr = businessIdentifierStr.replace(/[^a-zA-Z]/g, '')
      // cut, get rid of alpha and special chars, and pad '0's according to the numLength if length is less than numLength, trim to numLength if otherwise
      let businessIdentifierNumbers = incorpNum.substring(numberFirstIndex)
      businessIdentifierNumbers = parseInt(businessIdentifierNumbers.replace(/[^0-9]/g, '')).toString()
      if (businessIdentifierNumbers.length && businessIdentifierNumbers.length < numLength) {
        businessIdentifierNumbers = businessIdentifierNumbers.padStart(numLength, '0')
      } else if (businessIdentifierNumbers.length && businessIdentifierNumbers.length > numLength) {
        businessIdentifierNumbers = businessIdentifierNumbers.substring(0, numLength)
      }
      // join both first part and second part
      incorpNum = (businessIdentifierStr + businessIdentifierNumbers)
    }
    return incorpNum.toUpperCase()
  }
  static validateIncorporationNumber (value: string):boolean {
    const VALID_FORMAT = new RegExp(/^(A|B|BC|C|CP|EPR|FM|FOR|LIC|LL|LLC|LP|MF|QA|QB|QC|QD|QE|REG|S|S-|S\/|XL|XP|XS|XS-|XS\/|CS|CS-|CS\/)?\d+$/)
    return VALID_FORMAT.test(value.toUpperCase())
  }
  // This will validate the password rules with the regex
  // atleast 1 number, 1 uppercase, 1 lowercase, 1 special character and minimum length is 8
  static validatePasswordRules (value: string):boolean {
    const VALID_PASSWORD_FORMAT = new RegExp(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})/)
    return VALID_PASSWORD_FORMAT.test(value)
  }

  // Formatting date in the desired format for displaying in the template
  static formatDisplayDate (date: Date) {
    return moment(date).format('DD MMM, YYYY')
  }
}
