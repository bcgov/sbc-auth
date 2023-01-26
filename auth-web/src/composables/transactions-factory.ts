import { Transaction, TransactionFilterParams, TransactionState } from '@/models/transaction'
import { computed, reactive, watch } from '@vue/composition-api'
import { Organization } from '@/models/Organization'
import PaymentService from '@/services/payment.services'
import debounce from 'lodash/throttle'
import { useStore } from 'vuex-composition-helpers'

const transactions = (reactive({
  filters: {
    isActive: false,
    filterPayload: {
      dateFilter: {
        startDate: '',
        endDate: ''
      }
    },
    pageLimit: 0,
    pageNumber: 1
  } as TransactionFilterParams,
  loading: false,
  results: [] as Transaction[],
  totalResults: 0
}) as unknown) as TransactionState

export const useTransactions = () => {
  const store = useStore()
  const currentOrganization = computed(() => store.state.org.currentOrganization as Organization)

  const loadTransactionList = debounce(async (filterField?: string, value?: any) => {
    transactions.loading = true
    if (filterField) transactions.filters.filterPayload[filterField] = value
    let filtersActive = false
    for (const key in transactions.filters.filterPayload) {
      if (key === 'dateFilter') {
        if (transactions.filters.filterPayload[key].endDate) filtersActive = true
      } else if (transactions.filters.filterPayload[key]) filtersActive = true
    }
    transactions.filters.isActive = filtersActive
    try {
      const response = await PaymentService.getTransactions(currentOrganization.value.id, transactions.filters)
      if (response?.data) {
        transactions.results = response.data.items || []
        transactions.totalResults = response.data.total
      } else throw new Error('No response from getTransactions')
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get transaction list.', error)
    }
    transactions.loading = false
  }, 200)

  const getTransactionReport = async () => {
    try {
      const response = await PaymentService.getTransactionReports(currentOrganization.value.id, transactions.filters.filterPayload)
      if (!response?.data) throw new Error('No response from getTransactionReports')
      return response.data
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to get transaction report.', error)
    }
  }

  const clearAllFilters = () => {
    transactions.filters.filterPayload = { dateFilter: { startDate: '', endDate: '' } }
    transactions.filters.isActive = false
    loadTransactionList()
  }

  return {
    transactions,
    clearAllFilters,
    loadTransactionList,
    getTransactionReport
  }
}
