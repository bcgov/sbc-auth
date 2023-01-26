<template>
  <div>
    <date-picker v-show="showDatePicker" :reset="dateRangeReset" ref="datePicker" class="date-picker" @submit="updateDateRange($event)" />
    <base-v-data-table
      class="transaction-list"
      :clearFiltersTrigger="clearFiltersTrigger"
      :initialTableDataOptions="tableDataOptions"
      itemKey="id"
      :loading="transactions.loading"
      loadingText="loading text"
      noDataText="No Transaction Records"
      :setItems="transactions.results"
      :setHeaders="headers"
      :totalItems="transactions.totalResults"
      @update-table-options="tableDataOptions = $event"
    >
      <template v-slot:header-filter-slot-actions>
        <v-btn
          v-if="transactions.filters.isActive"
          class="clear-btn mx-auto mt-auto"
          color="primary"
          outlined
          @click="clearFilters()"
        >
          Clear Filters
          <v-icon class="ml-1 mt-1">mdi-close</v-icon>
        </v-btn>
      </template>
      <!-- header title slots -->
      <template v-slot:header-title-slot-statusCode="{ header }">
        {{ header.value }}
        <icon-tooltip icon="mdi-information-outline" :text="getStatusCodeHelpText()" />
      </template>
      <!-- header filter slots -->
      <template v-slot:header-filter-slot-createdOn>
        <v-text-field
          class="base-table__header__filter__textbox date-filter"
          :append-icon="'mdi-calendar'"
          clearable
          dense
          filled
          hide-details
          :placeholder="'Date'"
          :value="dateRangeSelected ? 'Custom' : ''"
          @click:clear="dateRangeReset++"
          @click="scrollToDatePicker()"
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
      <template v-slot:item-slot-statusCode="{ item }">
        <v-row no-gutters>
          <v-col cols="auto">
            <v-icon
              v-if="[InvoiceStatus.COMPLETED, InvoiceStatus.PAID, InvoiceStatus.REFUNDED].includes(item.statusCode)"
              color="success"
              :style="{ 'margin-top': '-6px', 'margin-right': '2px' }"
            >
              mdi-check
            </v-icon>
            <b>{{ invoiceStatusDisplay[item.statusCode] }}</b>
            <br/>
            <span v-if="item.updatedOn" v-html="displayDate(item.updatedOn)" />
          </v-col>
          <v-col class="pl-2" align-self="center">
            <icon-tooltip
              v-if="[InvoiceStatus.REFUND_REQUESTED, InvoiceStatus.REFUNDED].includes(item.statusCode)"
              icon="mdi-information-outline"
              maxWidth="300px"
              :text="getRefundHelpText(item)"
            />
          </v-col>
        </v-row>
      </template>
    </base-v-data-table>
  </div>
</template>

<script lang="ts">
import { BaseVDataTable, DatePicker, IconTooltip } from '@/components'
import { Ref, computed, defineComponent, nextTick, ref, watch } from '@vue/composition-api'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import { DataOptions } from 'vuetify'
import { InvoiceStatus } from '@/util/constants'
import _ from 'lodash'
import { invoiceStatusDisplay } from '@/resources/display-mappers'
import { useTransactions } from '@/composables'

export default defineComponent({
  name: 'TransactionsDataTable',
  components: { BaseVDataTable, DatePicker, IconTooltip },
  props: {
    headers: { default: [] as BaseTableHeaderI[] }
  },
  setup (props) {
    // refs
    const datePicker = ref(null)
    // composables
    const { transactions, loadTransactionList, clearAllFilters } = useTransactions()

    const getHeaders = computed(() => props.headers)

    // date picker stuff
    const dateRangeReset = ref(0)
    const dateRangeSelected = ref(false)
    const showDatePicker = ref(false)
    const scrollToDatePicker = async () => {
      showDatePicker.value = true
      // await for datePicker ref to update
      await nextTick()
      datePicker.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
    const updateDateRange = (val: { endDate?: string, startDate?: string }) => {
      showDatePicker.value = false
      if (val.endDate && val.startDate) dateRangeSelected.value = true
      else {
        dateRangeSelected.value = false
        val = { startDate: '', endDate: '' }
      }
      loadTransactionList('dateFilter', val)
    }

    // clear filters
    const clearFiltersTrigger = ref(0)
    const clearFilters = () => {
      // clear values in table
      clearFiltersTrigger.value++
      dateRangeReset.value++
      // clear transactions state filters and trigger search
      clearAllFilters()
    }

    const statusCodeDescs = [
      { description: 'Funds received', value: invoiceStatusDisplay[InvoiceStatus.CANCELLED].toUpperCase() },
      { description: 'Transaction is cancelled', value: invoiceStatusDisplay[InvoiceStatus.PAID].toUpperCase() },
      { description: 'Transaction is pending', value: invoiceStatusDisplay[InvoiceStatus.PENDING].toUpperCase() },
      { description: 'Transaction is in progress', value: invoiceStatusDisplay[InvoiceStatus.APPROVED].toUpperCase() },
      { description: 'Refund has been requested', value: invoiceStatusDisplay[InvoiceStatus.REFUND_REQUESTED].toUpperCase() },
      { description: 'Refund process is completed', value: invoiceStatusDisplay[InvoiceStatus.REFUNDED].toUpperCase() }
    ]
    const getStatusCodeHelpText = () => statusCodeDescs.reduce((text, statusCode) => `${text}${statusCode.value} - ${statusCode.description}<br/>`, '')
    const getRefundHelpText = (item: any) => {
      if (item?.statusCode === InvoiceStatus.REFUND_REQUESTED) {
        return 'We are processing your refund request.<br/>It may take up to 7 business days to refund your total amount.'
      }
      if (item?.statusCode === InvoiceStatus.REFUNDED) {
        return '$' + (item?.total?.toFixed(2) || '') + ' has been refunded to the account used for this trasaction.'
      }
      return ''
    }

    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)

    watch(() => tableDataOptions.value, (val: DataOptions) => {
      transactions.filters.pageNumber = val?.page || DEFAULT_DATA_OPTIONS.page
      transactions.filters.pageLimit = val?.itemsPerPage || DEFAULT_DATA_OPTIONS.itemsPerPage
      loadTransactionList()
    })

    const displayDate = (val: Date) => CommonUtils.formatDisplayDate(val, 'MMMM DD, YYYY')

    return {
      InvoiceStatus,
      clearFilters,
      clearFiltersTrigger,
      datePicker,
      dateRangeReset,
      dateRangeSelected,
      getHeaders,
      invoiceStatusDisplay,
      showDatePicker,
      statusCodeDescs,
      getRefundHelpText,
      getStatusCodeHelpText,
      tableDataOptions,
      transactions,
      displayDate,
      scrollToDatePicker,
      updateDateRange,
      loadTransactionList
    }
  }
})
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
.date-picker {
  left: 52%
}
</style>
