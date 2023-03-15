/* eslint-disable sort-imports */
import { Business } from './../models/business'
import { Affiliation, AffiliationState, AffiliationFilterParams } from './../models/affiliation'
import { debounce } from 'lodash'
import OrgService from '@/services/org.services'
import { computed, reactive, Ref, watch } from '@vue/composition-api'
import { useStore } from 'vuex-composition-helpers'
import { Organization } from '@/models/Organization'

const affiliations = (reactive({
  filters: {
    isActive: false,
    filterPayload: {}
  } as AffiliationFilterParams,
  loading: false,
  results: [] as Business[],
  totalResults: 0
}) as unknown) as AffiliationState

export const useAffiliations = () => {
  const store = useStore()
  const businesses = computed(() => store.state.business.businesses)
  const currentOrganization = computed(() => store.state.org.currentOrganization as Organization)

  watch(businesses, () => {
    affiliations.results = businesses.value
    affiliations.totalResults = businesses.value.length
  })

  const entityCount = computed(() => {
    return businesses.value.length
  })

  // get affiliated entities for this organization
  const loadAffiliations = (filterField?: string, value?: any) => {
    affiliations.totalResults = businesses.value.length
    affiliations.results = businesses.value
  }

  return {
    entityCount,
    loadAffiliations,
    affiliations
  }
}
