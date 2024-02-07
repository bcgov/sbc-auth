<template>
  <BaseVDataTable
    id="eft-transactions-table"
    class="transaction-list"
    itemKey="id"
    :loading="state.loading"
    loadingText="Loading Transaction Records..."
    noDataText="No Transaction Records"
    :setItems="state.results"
    :setHeaders="headers"
    :setTableDataOptions="state.options"
    :totalItems="state.totalResults"
    :filters="state.filters"
    :pageHide="true"
    :hideFilters="true"
    :hasTitleSlot="true"
    :useObserver="true"
    :observerCallback="infiniteScrollCallback"
    :height="calculateTableHeight()"
    @update-table-options="state.options = $event"
  >
    <template #header-title>
      <h2 class="ml-4 py-6">
        <v-icon
          class="pr-4"
          color="link"
          left
        >
          mdi-format-list-bulleted
        </v-icon>
        {{ paymentsReceived }}
      </h2>
    </template>
    <template #header-filter-slot />
    <template #item-slot-transactionDate="{ item }">
      <span>{{ formatDate(item.transactionDate, 'MMMM DD, YYYY') }}</span>
    </template>
    <template #item-slot-depositAmount="{ item }">
      <span>{{ formatCurrency(item.depositAmount) }}</span>
    </template>
  </BaseVDataTable>
</template>
<script lang="ts">
import { computed, defineComponent, reactive, watch } from '@vue/composition-api'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '../../datatable/resources'
import { EFTTransactionState } from '@/models/eft-transaction'
import PaymentService from '@/services/payment.services'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameTransactions',
  components: { BaseVDataTable },
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({
        shortName: null,
        transactionDate: null
      })
    }
  },
  setup (props) {
    const headers = [
      {
        col: 'transactionDate',
        hasFilter: false,
        minWidth: '125px',
        value: 'Payment Received Date'
      },
      {
        col: 'depositAmount',
        hasFilter: false,
        minWidth: '125px',
        value: 'Amount'
      }
    ]

    const state = reactive<EFTTransactionState>({
      results: [],
      totalResults: 1,
      filters: {
        pageNumber: 1,
        pageLimit: 5
      },
      loading: false,
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS)
    })

    const paymentsReceived = computed<string>(() => {
      return `Payments Received from ${props.shortNameDetails.shortName} (${state.totalResults})`
    })

    watch(() => props.shortNameDetails, () => {
      return loadTransactions(props.shortNameDetails.id, false)
    }, { deep: true })

    async function loadTransactions (shortnameId: string, appendToResults: boolean = false): Promise<void> {
      try {
        state.loading = true
        const response = await PaymentService.getEFTTransactions(shortnameId, state.filters)
        if (response?.data) {
          /* We use appendToResults for infinite scroll, so we keep the existing results. */
          state.results = appendToResults ? state.results.concat(response.data.items) : response.data.items
          state.totalResults = response.data.total
        } else {
          throw new Error('No response from getEFTTransactions')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTTransactions list.', error)
      }
      state.loading = false
    }

    async function infiniteScrollCallback () {
      if (state.totalResults < (state.filters.pageLimit * state.filters.pageNumber)) return true
      state.filters.pageNumber++
      await loadTransactions(props.shortNameDetails.id, true)
      return false
    }

    function calculateTableHeight () {
      if (state.results.length <= state.filters.pageLimit) return null
      const height = state.results.length * 40
      if (height > 400) return '400px'

      return `${height}px`
    }

    return {
      formatCurrency: CommonUtils.formatAmount,
      formatDate: CommonUtils.formatDisplayDate,
      headers,
      state,
      paymentsReceived,
      infiniteScrollCallback,
      calculateTableHeight
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/ShortnameTables.scss';

.card-title {
  background-color: $app-lt-blue;
  justify-content: left;
}

::v-deep{
  #table-title-cell {
    background-color: $app-lt-blue;
  }

  .v-data-table__wrapper {
    overflow-y: auto;
  }

  .base-table__header__title {
    padding-bottom: 16px
  }
}

</style>
