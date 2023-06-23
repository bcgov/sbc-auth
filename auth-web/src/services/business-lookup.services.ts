import { BusinessLookupResultIF } from '@/models'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'
import { axios } from '@/util/http-util'

/**
 * Class that provides integration with the BusinessLookup API.
 * This class is substantially similar to the same class in Create and Edit UIs.
 */
export default class BusinessLookupServices {
  /** The full Registries Search API URL. */
  static get registriesSearchApiUrl (): string {
    const url = `${process.env.VUE_APP_REGISTRIES_SEARCH_API_URL}`
    const version = `${process.env.VUE_APP_REGISTRIES_SEARCH_API_VERSION}`
    return (url + version + '/')
  }

  /** The Registries Search API Key. */
  static get registriesSearchApiKey (): string {
    return `${process.env.VUE_APP_REGISTRIES_SEARCH_API_KEY}`
  }

  /** The Account ID. */
  static get accountId (): string {
    const account = JSON.parse(
      ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}')
    )
    return account?.id
  }

  /**
   * Searches for business by code or words.
   * @param query code or words to search
   * @param status status to match (ACTIVE or HISTORICAL or empty to match all statuses)
   * @returns a promise to return the search results
   */
  static async search (query: string, status = ''): Promise<BusinessLookupResultIF[]> {
    const legalType = 'A,BC,BEN,C,CC,CP,CUL,FI,GP,LL,LLC,LP,PA,S,SP,ULC,XCP,XL,XP,XS'

    let url = this.registriesSearchApiUrl + 'businesses/search/facets?start=0&rows=20'
    url += `&categories=legalType:${legalType}${status ? '::status:' + status : ''}`
    url += `&query=value:${encodeURIComponent(query)}`

    return axios.get(url, {
      headers: {
        'x-apikey': this.registriesSearchApiKey,
        'Account-Id': this.accountId
      }
    }).then(response => {
      const results: Array<BusinessLookupResultIF> = response?.data?.searchResults?.results
      if (!results) {
        throw new Error('Invalid API response')
      }

      // filter out results without a valid identifier
      return results.filter(result => {
        const pattern = /^[A-Z]{1,3}\d{7}$/
        return pattern.test(result.identifier)
      })
    })
  }
}
