<template>
  <v-card>
    <v-card-title class="card-title">
      <v-icon
          class="pr-5"
          color="link"
          left
      >
        mdi-format-list-bulleted
      </v-icon>
      <b>Payments Received from {{ state.shortName?.shortName }} ({{state.totalResults}})</b>
    </v-card-title>
    <base-v-data-table
        id="eft-transactions-table"
        class="transaction-list"
        :clearFiltersTrigger="clearFiltersTrigger"
        itemKey="id"
        :loading="state.loading"
        loadingText="Loading Transaction Records..."
        noDataText="No Transaction Records"
        :setItems="state.results"
        :setHeaders="headers"
        :setTableDataOptions="tableDataOptions"
        :totalItems="state.totalResults"
        :filters="state.filters"
        :updateFilter="updateFilter"
        @update-table-options="tableDataOptions = $event"
    >
      <template #item-slot-transactionDate="{ item }">
        <span>{{ formatDate(item.transactionDate, 'MMMM DD, YYYY') }}</span>
      </template>
      <template #item-slot-depositAmount="{ item }">
        <span>{{ formatCurrency(item.depositAmount) }}</span>
      </template>
    </base-v-data-table>
  </v-card>
</template>
<script lang="ts">
import { EFTTransactionFilterParams } from '@/models/eft-transaction'
import PaymentService from '@/services/payment.services'
import CommonUtils from '@/util/common-util'
import { Ref, defineComponent, reactive, ref, watch } from '@vue/composition-api'
import { BaseVDataTable } from '@/components'
import { DEFAULT_DATA_OPTIONS } from '../../datatable/resources'
import { DataOptions } from 'vuetify'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameTransactions',
  components: { BaseVDataTable },
  props: {
    shortName: {
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

    const state = reactive({
      results: [],
      totalResults: 1,
      filters: {
        isActive: false,
        pageNumber: 1,
        pageLimit: 5
      } as EFTTransactionFilterParams,
      loading: false,
      shortName: {
        id: null
      }
    })

    function setShortName (shortname) {
      state.shortName = shortname
      loadTransactions(state.shortName.id)
    }

    watch(() => props.shortName, () => setShortName(props.shortName), { deep: true })
    async function loadTransactions (shortnameId: string): Promise<void> {
      try {
        state.loading = true
        const response = await PaymentService.getEFTTransactions(shortnameId, state.filters)
        if (response?.data) {
          /* We use appendToResults for infinite scroll, so we keep the existing results. */
          state.results = response.data.items
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

    function clearFilters (): void { }
    function updateFilter () : void { }

    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)

    watch(() => state.filters.pageNumber, (val: number) => { tableDataOptions.value.page = val })
    watch(() => tableDataOptions.value, (val: DataOptions) => {
      const newPage = val?.page || DEFAULT_DATA_OPTIONS.page
      const newLimit = val?.itemsPerPage || DEFAULT_DATA_OPTIONS.itemsPerPage
      // need this check or vi test continuously loops on initialization
      if (state.filters.pageNumber !== newPage || state.filters.pageLimit !== newLimit) {
        state.filters.pageNumber = val?.page || DEFAULT_DATA_OPTIONS.page
        state.filters.pageLimit = val?.itemsPerPage || DEFAULT_DATA_OPTIONS.itemsPerPage
        loadTransactions(state.shortName?.id)
      }
    })

    // clear filters
    const clearFiltersTrigger = ref(0)

    const formatDate = CommonUtils.formatDisplayDate
    const formatCurrency = CommonUtils.formatAmount

    return {
      clearFilters,
      clearFiltersTrigger,
      formatCurrency,
      formatDate,
      headers,
      tableDataOptions,
      state,
      updateFilter
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.card-title {
  background-color: $app-lt-blue;
  justify-content: left;
}

::v-deep {
  .base-table__header__filter.pb-5 {
    padding: 5px !important;
    height: 0 !important;//No filters for this table
  }
  .base-table__item-row {
    color: $gray7;
    font-weight: bold;
  }
  .base-table__item-cell {
    padding: 16px 0 16px 16px;
    vertical-align: middle;
  }
}
</style>
