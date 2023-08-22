import { LDFlags, Role } from '@/util/constants'
import { Transaction, TransactionFilterParams, TransactionState } from '@/models/transaction'
import { computed, reactive, ref } from '@vue/composition-api'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { Organization } from '@/models/Organization'
import PaymentService from '@/services/payment.services'
import debounce from 'lodash/throttle'
import { useOrgStore } from '@/store/org'
import { useUserStore } from '@/store/user'

const transactions = (reactive({
  filters: {
    isActive: false,
    filterPayload: {
      dateFilter: {
        startDate: '',
        endDate: ''
      }
    },
    pageLimit: 5,
    pageNumber: 1
  } as TransactionFilterParams,
  loading: false,
  results: [] as Transaction[],
  totalResults: 0
}) as unknown) as TransactionState

export const useTransactions = () => {
  const orgStore = useOrgStore()
  const userStore = useUserStore()
  const currentOrganization = computed(() => orgStore.state.currentOrganization as Organization)
  const currentUser = computed(() => userStore.state.currentUser as KCUserProfile)
  const viewAll = ref(false)
  const setViewAll = (val: boolean) => {
    if (val) {
      // check authorized
      if (!currentUser.value.roles.includes(Role.ViewAllTransactions)) {
        // eslint-disable-next-line no-console
        console.error('User is not authorized to view all transactions.')
        return
      }
    }
    viewAll.value = val
  }

  const loadTransactionList = debounce(async (filterField?: string, value?: any) => {
    transactions.loading = true
    if (filterField) {
      // new filter so set page number back to 1
      transactions.filters.pageNumber = 1
      transactions.filters.filterPayload[filterField] = value
    }
    let filtersActive = false
    for (const key in transactions.filters.filterPayload) {
      if (key === 'dateFilter') {
        if (transactions.filters.filterPayload[key].endDate) filtersActive = true
      } else if (transactions.filters.filterPayload[key]) filtersActive = true
      if (filtersActive) break
    }
    transactions.filters.isActive = filtersActive

    // Temporary code check in case of performance issues with public users
    if (!(LaunchDarklyService.getFlag(LDFlags.EnableDetailsFilter) || false)) {
      if (transactions.filters.filterPayload.lineItemsAndDetails) {
        // remove the filter that also queries details
        transactions.filters.filterPayload.lineItems = transactions.filters.filterPayload.lineItemsAndDetails
        delete transactions.filters.filterPayload.lineItemsAndDetails
      }
    }

    try {
      const response = await PaymentService.getTransactions(
        currentOrganization.value.id, transactions.filters, viewAll.value)
      if (response?.data) {
        transactions.results = response.data.items || []
        transactions.totalResults = response.data.total
      } else throw new Error('No response from getTransactions')
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get transaction list.', error)
    }
    transactions.loading = false
  }, 200) as (filterField?: string, value?: any, viewAll?: boolean) => Promise<void>

  const getTransactionReport = async () => {
    try {
      const response = await PaymentService.getTransactionReports(currentOrganization.value.id, transactions.filters.filterPayload)
      if (!response?.data) throw new Error('No response from getTransactionReports')
      return response.data
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get transaction report.', error)
      return { error: error }
    }
  }

  const clearAllFilters = () => {
    transactions.filters.filterPayload = { dateFilter: { startDate: '', endDate: '' } }
    transactions.filters.isActive = false
    transactions.filters.pageNumber = 1
    loadTransactionList()
  }

  return {
    transactions,
    clearAllFilters,
    loadTransactionList,
    getTransactionReport,
    setViewAll
  }
}
