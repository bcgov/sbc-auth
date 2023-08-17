import ConfigHelper from '@/util/config-helper'
import { NameRequestLookupResultIF } from '@/models/business-nr-lookup'
import { SessionStorageKeys } from '@/util/constants'
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
    console.log(this.namexApiUrl)
    let url = this.namexApiUrl + 'requests/search'
    url += `?query=${encodeURIComponent(query)}`
    url += '&start=0&rows=20'
    const token = ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)

    return axios.get(url, {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    }).then(response => {
      const results: Array<NameRequestLookupResultIF> = response?.data?.searchResults?.results
      if (!results) {
        throw new Error('Invalid API response')
      }

      return results.filter(result => {
        const pattern = /^[A-Z]{1,3}\d{7}$/
        return pattern.test(result.nrNum)
      })
    })
  }
}
