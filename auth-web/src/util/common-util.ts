/**
 * Place to put all the custom utility methods
 */
import { Address, BaseAddressModel } from '@/models/address'
import { Permission } from '@/util/constants'
import moment from 'moment'

export default class CommonUtils {
  // checking url matches the regex
  static isUrl (value:string):boolean {
    const URL_MATCHER = new RegExp('^(?:\\w+:)?\\/\\/([^\\s\\.]+\\.\\S{2}|localhost[\\:?\\d]*)\\S*$')
    return URL_MATCHER.test(value)
  }
  // formatting incorporation number according to the length of numbers
  static formatIncorporationNumber (incorpNum:string, isNR: boolean = false, numLength?:number):string {
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
      incorpNum = (isNR) ? `${businessIdentifierStr} ${businessIdentifierNumbers}` : `${businessIdentifierStr}${businessIdentifierNumbers}`
    }
    return incorpNum.toUpperCase()
  }
  static validateIncorporationNumber (value: string):boolean {
    const VALID_FORMAT = new RegExp(/^(A|B|BC|C|CP|EPR|FM|FOR|LIC|LL|LLC|LP|MF|QA|QB|QC|QD|QE|REG|S|S-|S\/|XL|XP|XS|XS-|XS\/|CS|CS-|CS\/)?\d+$/)
    return VALID_FORMAT.test(value.toUpperCase())
  }
  static validateNameRequestNumber (value: string):boolean {
    const VALID_FORMAT = new RegExp(/^(NR )?\d+$/)
    return VALID_FORMAT.test(value.toUpperCase())
  }
  static validateEmailFormat (value: string):boolean {
    const VALID_FORMAT = new RegExp(/^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/)
    return VALID_FORMAT.test(value)
  }
  // This will validate the password rules with the regex
  // atleast 1 number, 1 uppercase, 1 lowercase, 1 special character and minimum length is 8
  static validatePasswordRules (value: string):boolean {
    const VALID_PASSWORD_FORMAT = new RegExp(/^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*])(?=.{8,})/)
    return VALID_PASSWORD_FORMAT.test(value)
  }

  // Formatting date in the desired format for displaying in the template
  static formatDisplayDate (date: Date, format?: string) {
    return (date) ? moment(date).format(format || 'MM-DD-YYYY') : ''
  }

  // Formatting date in the desired format for vue date pickers
  static formatDatePickerDate (date?: Date) {
    return moment(date || new Date()).format('YYYY-MM-DD')
  }

  static fileDownload (data: any, fileName: string, fileType: string = 'text/plain') {
    const blob = new Blob([data], { type: fileType })
    if (typeof window.navigator.msSaveBlob !== 'undefined') {
      // IE workaround for "HTML7007: One or more blob URLs were
      // revoked by closing the blob for which they were created.
      // These URLs will no longer resolve as the data backing
      // the URL has been freed."
      window.navigator.msSaveBlob(blob, fileName)
    } else {
      const blobURL = (window.URL && window.URL.createObjectURL) ? window.URL.createObjectURL(blob) : window.webkitURL.createObjectURL(blob)
      let tempLink = document.createElement('a')
      tempLink.style.display = 'none'
      tempLink.href = blobURL
      tempLink.setAttribute('download', fileName)

      // Safari thinks _blank anchor are pop ups. We only want to set _blank
      // target if the browser does not support the HTML5 download attribute.
      // This allows you to download files in desktop safari if pop up blocking
      // is enabled.
      if (typeof tempLink.download === 'undefined') {
        tempLink.setAttribute('target', '_blank')
      }
      document.body.appendChild(tempLink)
      tempLink.click()
      setTimeout(() => {
        document.body.removeChild(tempLink)
        window.URL.revokeObjectURL(blobURL)
      }, 200)
    }
  }

  static isSigningIn ():boolean {
    const path = window.location.pathname
    return path.includes('/signin') || path.includes('/signin-redirect') || path.includes('/signin-redirect-full')
  }
  static isSigningOut ():boolean {
    const path = window.location.pathname
    return path.includes('/signout')
  }

  static getAdminPermissions (): string[] {
    return [
      Permission.REMOVE_BUSINESS,
      Permission.CHANGE_ADDRESS,
      Permission.CHANGE_ORG_NAME,
      Permission.INVITE_MEMBERS,
      Permission.CHANGE_ACCOUNT_TYPE,
      Permission.CHANGE_ROLE,
      Permission.RESET_PASSWORD,
      Permission.TRANSACTION_HISTORY,
      Permission.MANAGE_STATEMENTS,
      Permission.VIEW_ADMIN_CONTACT
    ]
  }
  static getViewOnlyPermissions (): string[] {
    return [
      Permission.VIEW_ACCOUNT,
      Permission.VIEW_ADDRESS,
      Permission.VIEW_ADMIN_CONTACT
    ]
  }
  // for converting address object of sbc-auth to as needed for BaseAddress component
  static convertAddressForComponent (address: Address) : BaseAddressModel {
    return {
      addressCity: address.city,
      addressCountry: address.country,
      addressRegion: address.region,
      deliveryInstructions: address.deliveryInstructions,
      postalCode: address.postalCode,
      streetAddress: address.street,
      streetAddressAdditional: address.streetAdditional
    }
  }
  // for converting address object of BaseAddress component to as needed for sbc-auth
  static convertAddressForAuth (iaddress: BaseAddressModel) : Address {
    return {
      city: iaddress.addressCity,
      country: iaddress.addressCountry,
      region: iaddress.addressRegion,
      deliveryInstructions: iaddress.deliveryInstructions,
      postalCode: iaddress.postalCode,
      street: iaddress.streetAddress,
      streetAdditional: iaddress.streetAddressAdditional
    }
  }
}
