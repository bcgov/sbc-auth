import { LDFlags, Role } from '@/util/constants'
import { Transaction, TransactionFilterParams, TransactionState } from '@/models/transaction'
import { computed, reactive, ref } from '@vue/composition-api'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import PaymentService from '@/services/payment.services'
import debounce from 'lodash/throttle'
import moment from 'moment'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

const transactions = (reactive({
  filters: {
    isActive: false,
    filterPayload: {
      dateFilter: {
        startDate: '',
        endDate: '',
        isDefault: false
      }
    },
    pageLimit: 5,
    pageNumber: 1
  } as TransactionFilterParams,
  loading: false,
  results: [] as Transaction[],
  totalResults: 0
}) as unknown) as TransactionState

// Request counter to track the latest request and ignore stale responses
let requestCounter = 0

export const useTransactions = () => {
  const orgStore = useOrgStore()
  const userStore = useUserStore()
  const currentOrganization = computed(() => orgStore.currentOrganization)
  const currentUser = computed(() => userStore.currentUser)
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
    requestCounter++
    const currentRequestId = requestCounter
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
      if (currentRequestId === requestCounter) {
        if (response?.data) {
          transactions.results = response.data.items || []
          transactions.totalResults = transactions.results.length * response.data.page + (response.data.hasMore ? 1 : 0)
        } else throw new Error('No response from getTransactions')
      }
    } catch (error) {
      if (currentRequestId === requestCounter) {
        // eslint-disable-next-line no-console
        console.error('Failed to get transaction list.', error)
      }
    }
    if (currentRequestId === requestCounter) {
      transactions.loading = false
    }
  }, 2000, { leading: true, trailing: true }) as (filterField?: string, value?: any, viewAll?: boolean) => Promise<void>

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

  const clearAllFilters = (skipLoadTransactions = false) => {
    transactions.filters.filterPayload = { dateFilter: { startDate: '', endDate: '', isDefault: false } }
    transactions.filters.isActive = false
    transactions.filters.pageNumber = 1
    if (!skipLoadTransactions) {
      loadTransactionList()
    }
  }

  // We need this specific function to set the default search to one year, otherwise too many rows and loss of performance.
  const defaultSearchToOneYear = () => {
    transactions.filters.filterPayload = {
      dateFilter: {
        startDate: moment().subtract(1, 'year').format('YYYY-MM-DD'),
        endDate: moment().add(1, 'day').format('YYYY-MM-DD'),
        isDefault: true
      }
    }
    transactions.filters.isActive = true
  }

  return {
    transactions,
    clearAllFilters,
    loadTransactionList,
    getTransactionReport,
    setViewAll,
    defaultSearchToOneYear
  }
}
