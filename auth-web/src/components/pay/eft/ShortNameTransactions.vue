<template>
  <BaseVDataTable
    id="eft-transactions-table"
    class="transaction-list"
    itemKey="id"
    :loading="state.loading"
    loadingText="Loading Records..."
    noDataText="No Records."
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
        Payment History
      </h2>
    </template>
    <template #header-filter-slot />
    <template #item-slot-transactionDate="{ item }">
      <span>{{ formatDate(item.transactionDate, 'MMMM DD, YYYY') }}</span>
    </template>
    <template #item-slot-transactionDescription="{ item }">
      <span>{{ item.transactionDescription }}</span>
      <span
        v-if="isStatementPaid(item)"
        class="transaction-details"
      >
        {{ formatAccountDisplayName(item) }}
      </span>
    </template>
    <template #item-slot-transactionAmount="{ item }">
      <span>{{ formatCurrency(item.transactionAmount) }}</span>
    </template>
  </BaseVDataTable>
</template>
<script lang="ts">
import { defineComponent, reactive, watch } from '@vue/composition-api'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '../../datatable/resources'
import { EFTTransactionState } from '@/models/eft-transaction'
import PaymentService from '@/services/payment.services'
import { ShortNameTransactionRowType } from '@/util/constants'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameTransactions',
  components: { BaseVDataTable },
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({
        shortName: null
      })
    }
  },
  setup (props) {
    const headers = [
      {
        col: 'transactionDate',
        hasFilter: false,
        minWidth: '125px',
        value: 'Date'
      },
      {
        col: 'transactionDescription',
        hasFilter: false,
        minWidth: '200px',
        value: 'Description'
      },
      {
        col: 'statementId',
        hasFilter: false,
        minWidth: '200px',
        value: 'Related Statement Number'
      },
      {
        col: 'transactionAmount',
        hasFilter: false,
        minWidth: '125px',
        value: 'Amount'
      }
    ]

    const state = reactive<EFTTransactionState>({
      results: [],
      totalResults: 0,
      filters: {
        pageNumber: 1,
        pageLimit: 5
      },
      loading: false,
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS)
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

    function isStatementPaid (item: any) {
      return item?.transactionDescription === ShortNameTransactionRowType.STATEMENT_PAID
    }

    return {
      formatCurrency: CommonUtils.formatAmount,
      formatDate: CommonUtils.formatDisplayDate,
      formatAccountDisplayName: CommonUtils.formatAccountDisplayName,
      headers,
      state,
      infiniteScrollCallback,
      calculateTableHeight,
      isStatementPaid
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/ShortnameTables.scss';

::v-deep{
  #table-title-cell {
    background-color: $app-lt-blue;
  }

  .v-data-table__wrapper {
    overflow-y: auto;
  }

  .v-data-table__empty-wrapper {
    background-color: transparent !important; // remove highlight on no records row
  }

  .base-table__header__title {
    padding-bottom: 16px;
    top: 75px !important; // prevent fixed header sliding when there is a title
  }
}

.transaction-details {
  display: block;
  width: 100%;
  font-weight: normal;
}

</style>
