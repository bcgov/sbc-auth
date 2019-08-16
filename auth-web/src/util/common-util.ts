/**
 * Place to put all the custom utility methods
 */
const URL_MATCHER = new RegExp('^(?:\\w+:)?\\/\\/([^\\s\\.]+\\.\\S{2}|localhost[\\:?\\d]*)\\S*$')
export default {
  isUrl (value:string):boolean {
    return URL_MATCHER.test(value)
  }
}
