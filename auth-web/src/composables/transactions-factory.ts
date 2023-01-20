import { Transaction, TransactionFilterParams, TransactionState } from '@/models/transaction'
import { computed, reactive, watch } from '@vue/composition-api'
import { Organization } from '@/models/Organization'
import PaymentService from '@/services/payment.services'
import { useStore } from 'vuex-composition-helpers'

const transactions = (reactive({
  filters: {
    filterPayload: {
      dateFilter: {
        startDate: '',
        endDate: ''
      },
      folioNumber: '',
      createdBy: ''
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

  const loadTransactionList = async (filterField?: string, value?: any) => {
    console.log('loadTransactionList')
    transactions.loading = true
    if (filterField) transactions.filters.filterPayload[filterField] = value
    try {
      const response = await PaymentService.getTransactions(currentOrganization.value.id, transactions.filters)
      if (response?.data) {
        transactions.results = response.data.items || []
        transactions.totalResults = response.data.total
      } else throw new Error('No response from getTransactions')
    } catch (error) {
      console.error('Failed to get transaction list.', error)
    }
    transactions.loading = false
  }

  watch(() => [transactions.filters, transactions.filters.filterPayload], () => {
    console.log('watch transactions.filters')
    loadTransactionList()
  }, { deep: true })

  const getTransactionReport = async () => {
    try {
      const response = await PaymentService.getTransactionReports(currentOrganization.value.id, transactions.filters.filterPayload)
      if (!response?.data) throw new Error('No response from getTransactionReports')
      return response.data
    } catch (error) {
      console.error('Failed to get transaction report.', error)
    }
  }

  return {
    transactions,
    loadTransactionList,
    getTransactionReport
  }
}
