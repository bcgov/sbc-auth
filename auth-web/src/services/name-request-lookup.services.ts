import { NameRequestLookupResultIF } from '@/models/business-nr-lookup'
import { axios } from '@/util/http-util'

/**
 * Class that provides integration with the BusinessLookup on NameRequest API.
 */
export default class NameRequestLookupServices {
  /** The full NameX API URL. */
  static get namexApiUrl (): string {
    const url = `${import.meta.env.VUE_APP_NAMEX_API_URL}`
    const version = `${import.meta.env.VUE_APP_NAMEX_API_VERSION}`
    return (url + version + '/')
  }

  /**
   * Searches for name request by code or words.
   * @param query code or words to search
   * @returns a promise to return the search results
   */
  static async search (query: string): Promise<NameRequestLookupResultIF[]> {
    let url = NameRequestLookupServices.namexApiUrl + 'requests/search'
    url += `?query=${encodeURIComponent(query)}`
    url += '&start=0&rows=20'

    try {
      const response = await axios.get(url)

      const results: Array<NameRequestLookupResultIF> = response?.data

      if (!results) {
        throw new Error('Invalid API response')
      }

      return results.filter(result => {
        const pattern = /^NR \d{7}$/
        return pattern.test(result.nrNum)
      })
    } catch (error) {
      throw new Error('Error fetching data from API: ' + error.message)
    }
  }
}
