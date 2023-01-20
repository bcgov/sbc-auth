<template>
  <div>
    <date-picker v-show="showDatePicker" @submit="updateDateRange($event)" />
    <base-v-data-table
      class="transaction-list"
      :initialHeaders="headers"
      :initialTableDataOptions="tableDataOptions"
      itemKey="id"
      :loading="transactions.loading"
      loadingText="loading text"
      :noDataText="$t('noTransactionList')"
      :setItems="transactions.results"
      :totalItems="transactions.totalResults"
      @update-table-options="tableDataOptions = $event"
    >
      <!-- header title slots -->
      <template v-slot:header-title-slot-statusCode="{ header }">
        {{ header.value }}
        <v-tooltip bottom color="grey darken-4">
          <template v-slot:activator="{ on }">
            <v-icon color="primary" v-on="on">mdi-information-outline</v-icon>
          </template>
          <div v-for="statusCodeDesc, i in statusCodeDescs" :key="statusCodeDesc.value + i">
            {{ statusCodeDesc.value }} - {{ statusCodeDesc.description }}
          </div>
        </v-tooltip>
      </template>
      <!-- header filter slots -->
      <template v-slot:header-filter-slot-createdOn>
        <v-text-field
          class="base-table__header__filter__textbox"
          :append-icon="'mdi-calendar'"
          clearable
          dense
          filled
          hide-details
          :placeholder="'Date'"
          :value="dateRangeSelected ? 'Custom' : ''"
          @focus="showDatePicker = true"
        />
      </template>
      <!-- item slots -->
      <template v-slot:item-slot-lineItems="{ item }">
        <b v-for="lineItem, i in item.lineItems" :key="lineItem.description + i" class="dark-text">
          {{ lineItem.description }}
        </b><br/>
        <span v-for="detail, i in item.details" :key="detail.label + i">
          <!-- ux requested to remove all number labels -->
          <span v-if="!detail.label.toLowerCase().includes('number')">{{ detail.label }}</span>
          {{ detail.value }}
        </span><br/>
      </template>
      <template v-slot:item-slot-total="{ item }">
        <span v-if="item.statusCode === InvoiceStatus.CANCELLED">$0.00</span>
        <span v-else>{{ '$' + item.total.toFixed(2) }}</span>
      </template>
    </base-v-data-table>
  </div>
</template>

<script lang="ts">
import { BaseVDataTable, DatePicker } from '@/components'
import { Ref, computed, defineComponent, reactive, ref, watch } from '@vue/composition-api'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import { DataOptions } from 'vuetify'
import { InvoiceStatus } from '@/util/constants'
import { TransactionTableHeaders } from '@/resources/table-headers'
import _ from 'lodash'
import { invoiceStatusDisplay } from '@/resources/display-mappers'
import { useTransactions } from '@/composables'

export default defineComponent({
  name: 'TransactionsDataTable',
  components: { BaseVDataTable, DatePicker },
  setup () {
    const { transactions, loadTransactionList } = useTransactions()

    // FUTURE: in vue3 we can pull this out and add it within the resource
    const headers = _.cloneDeep(TransactionTableHeaders) as BaseTableHeaderI[]
    headers.forEach((header) => {
      if (header.hasFilter) header.customFilter.filterApiFn = (val: any) => loadTransactionList(header.col, val || '')
    })

    const dateRangeSelected = ref(false)
    const showDatePicker = ref(false)
    const updateDateRange = (val: { endDate: string, startDate: string }) => {
      console.log(val)
      showDatePicker.value = false
      if (val.endDate && val.startDate) dateRangeSelected.value = true
      else dateRangeSelected.value = false
      // loadTransactionList('createdOn', )
    }

    const statusCodeDescs = [
      { description: 'Funds received', value: invoiceStatusDisplay[InvoiceStatus.CANCELLED].toUpperCase() },
      { description: 'Transaction is cancelled', value: invoiceStatusDisplay[InvoiceStatus.PAID].toUpperCase() },
      { description: 'Transaction is pending', value: invoiceStatusDisplay[InvoiceStatus.PENDING].toUpperCase() },
      { description: 'Transaction is in progress', value: invoiceStatusDisplay[InvoiceStatus.APPROVED].toUpperCase() },
      { description: 'Refund has been requested', value: invoiceStatusDisplay[InvoiceStatus.REFUND_REQUESTED].toUpperCase() },
      { description: 'Refund process is completed', value: invoiceStatusDisplay[InvoiceStatus.REFUNDED].toUpperCase() }
    ]

    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)

    watch(() => tableDataOptions.value, (val: DataOptions) => {
      transactions.filters.pageNumber = val?.page || DEFAULT_DATA_OPTIONS.page
      transactions.filters.pageLimit = val?.itemsPerPage || DEFAULT_DATA_OPTIONS.itemsPerPage
    })

    return {
      InvoiceStatus,
      dateRangeSelected,
      headers,
      invoiceStatusDisplay,
      showDatePicker,
      statusCodeDescs,
      tableDataOptions,
      transactions,
      updateDateRange
    }
  }
})
//   @Emit('total-transaction-count')
//   private emitTotalCount () {
//     return this.totalTransactionsCount
//   }

//   private getStatusClass (item) {
//     switch (item.status) {
//       case TransactionStatus.COMPLETED: return 'status-paid'
//       case TransactionStatus.PENDING: return 'status-pending'
//       case TransactionStatus.CANCELLED: return 'status-deleted'
//       default: return ''
//     }
//   }

//   private formatStatus (status) {
//     // status show as pending array
//     const statusMapToPending = ['Settlement Scheduled', 'PAD Invoice Approved']
//     return statusMapToPending.includes(status) ? 'Pending' : status
//   }

//   private getStatusColor (status) {
//     switch (status?.toUpperCase()) {
//       case TransactionStatus.COMPLETED.toUpperCase():
//         return 'success'
//       case TransactionStatus.CANCELLED.toUpperCase():
//         return 'error'
//       default:
//         return ''
//     }
//   }
// }
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
.date-filter {
  font-size: 0.875rem;
}

.v-tooltip__content:before {
  content: ' ';
  position: absolute;
  top: -20px;
  left: 50%;
  margin-left: -10px;
  width: 20px;
  height: 20px;
  border-width: 10px 10px 10px 10px;
  border-style: solid;
  border-color: transparent transparent var(--v-grey-darken4) transparent;
}
</style>
