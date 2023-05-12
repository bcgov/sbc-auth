// import { MHRSearchTypes, SearchTypes } from '@/resources'
// import { APIMHRSearchTypes, APIMHRMapSearchTypes, ErrorCategories } from '@/enums'
// import { axios } from '@/utils'
// import { SearchResponseI } from '@/interfaces'
// import { StatusCodes } from 'http-status-codes'

// const SEARCH_RESULT_SIZE = 100

// export const useSearch = () => {
//   const isMHRSearchType = (type: string): boolean => {
//     const mhi = MHRSearchTypes.findIndex(mh => mh.searchTypeAPI === type)
//     return mhi >= 0
//   }
//   const isPPRSearchType = (type: string): boolean => {
//     const sti = SearchTypes.findIndex(st => st.searchTypeAPI === type)
//     return sti >= 0
//   }
//   const mapMhrSearchType = (type: string, reverseMap: boolean = false): APIMHRSearchTypes|APIMHRMapSearchTypes => {
//     if (reverseMap) {
//       const index = Object.values(APIMHRSearchTypes).indexOf(type as APIMHRSearchTypes)
//       return APIMHRMapSearchTypes[Object.keys(APIMHRMapSearchTypes)[index]]
//     } else {
//       const index = Object.values(APIMHRMapSearchTypes).indexOf(type as APIMHRMapSearchTypes)
//       return APIMHRSearchTypes[Object.keys(APIMHRSearchTypes)[index]]
//     }
//   }
//   const getSearchConfig = (params: object = null) => {
//     const url = sessionStorage.getItem('REGISTRIES_SEARCH_API_URL')
//     const apiKey = sessionStorage.getItem('REGISTRIES_SEARCH_API_KEY')
//     const currentAccount = sessionStorage.getItem('CURRENT_ACCOUNT')

//     if (!url) console.error('Error: REGISTRY_SEARCH_API_URL expected, but not found.')
//     if (!apiKey) console.error('Error: REGISTRY_SEARCH_API_KEY expected, but not found.')
//     if (!currentAccount) console.error('Error: current account expected, but not found.')

//     const currentAccountId = JSON.parse(currentAccount)?.id

//     return { baseURL: url, headers: { 'Account-Id': currentAccountId, 'x-apikey': apiKey }, params: params }
//   }
//   /**
//    * Search for a Business Name using Registry Search API
//    * @param searchValue search term, which is required
//    * @param isPPR search for active and historical statuses is search is for PPR
//    * @returns array of search results
//    */
//   const searchBusiness = async (searchValue: string, isPPR: boolean = false): Promise<SearchResponseI> => {
//     if (!searchValue) return
//     // basic params
//     const params = { query: `value:${searchValue}`, categories: 'status:active', start: 0, rows: SEARCH_RESULT_SIZE }
//     // include all statuses for PPR business searches by removing categories filter
//     isPPR && delete params.categories
//     // add search-api config stuff
//     const config = getSearchConfig(params)
//     return axios
//       .get<SearchResponseI>('businesses/search/facets', config)
//       .then(response => {
//         const data: SearchResponseI = response?.data
//         if (!data) {
//           throw new Error('Invalid API response')
//         }
//         return data
//       })
//       .catch(error => {
//         return {
//           searchResults: null,
//           error: {
//             statusCode: error?.response?.status || StatusCodes.NOT_FOUND,
//             message: error?.response?.data?.message,
//             category: ErrorCategories.SEARCH,
//             type: error?.parsed?.rootCause?.type
//           }
//         }
//       })
//   }

//   return {
//     isMHRSearchType,
//     isPPRSearchType,
//     mapMhrSearchType,
//     searchBusiness
//   }
// }
