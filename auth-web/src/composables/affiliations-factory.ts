/* eslint-disable sort-imports */
import { Business } from './../models/business'
import { Affiliation, AffiliationState, AffiliationFilterParams } from './../models/affiliation'
import { debounce } from 'lodash/throttle'
import OrgService from '@/services/org.services'
import { computed, reactive } from '@vue/composition-api'
import { useStore } from 'vuex-composition-helpers'
import { Organization } from '@/models/Organization'

const affiliations = (reactive({
  filters: {
    isActive: false,
    filterPayload: {},
    pageLimit: 5,
    pageNumber: 1
  } as AffiliationFilterParams,
  loading: false,
  results: [] as Business[],
  totalResults: 0
}) as unknown) as AffiliationState

export const useAffiliations = () => {
  const store = useStore()
  const currentOrganization = computed(() => store.state.org.currentOrganization as Organization)

  // get affiliated entities for this organization
  const loadAffiliationList = debounce(async (filterField?: string, value?: any) => {
    affiliations.loading = true
    if (filterField) {
      // new filter so set page number back to 1
      affiliations.filters.pageNumber = 1
      affiliations.filters.filterPayload[filterField] = value
    }
    let filtersActive = false
    for (const key in affiliations.filters.filterPayload) {
      if (affiliations.filters.filterPayload[key]) filtersActive = true
      if (filtersActive) break
    }
    affiliations.filters.isActive = filtersActive

    try { // TODO add filter to getAffiliatiatedEntities at service
      const affiliatedEntities = await OrgService.getAffiliatiatedEntities(
        currentOrganization.value.id, affiliations.filters)
      if (affiliatedEntities?.data?.entities) {
        affiliations.results = affiliatedEntities.data.entities || []
        affiliations.totalResults = affiliatedEntities.data.entities.length
      } else throw new Error('No response from getaffiliations')
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get Affiliation list.', error)
    }
    affiliations.loading = false
  }, 200) as (filterField?: string, value?: any, viewAll?: boolean) => Promise<void>

  return {
    affiliations,
    loadAffiliationList
  }
}
