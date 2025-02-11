<template>
  <div>
    <DatePicker
      v-show="showDatePicker"
      ref="datePicker"
      :reset="dateRangeReset"
      :setStartDate="transactions.filters.filterPayload.dateFilter.startDate"
      :setEndDate="transactions.filters.filterPayload.dateFilter.endDate"
      class="date-picker"
      @submit="updateDateRange($event)"
    />
    <div
      v-if="extended"
      class="section-heading pa-4"
    >
      <h3>
        <v-icon
          color="primary"
          style="margin-top: -2px;"
        >
          mdi-format-list-bulleted
        </v-icon>
        Transactions
        <v-progress-circular
          v-if="transactions.loading"
          color="primary"
          indeterminate
          size="20"
        />
      </h3>
    </div>
    <BaseVDataTable
      class="transaction-list"
      :clearFiltersTrigger="clearFiltersTrigger"
      itemKey="id"
      :loading="transactions.loading"
      loadingText="Loading Transaction Records..."
      noDataText="No Transaction Records"
      :setItems="transactions.results"
      :setHeaders="headers"
      :setTableDataOptions="tableDataOptions"
      :totalItems="transactions.totalResults"
      :disableRowCount="true"
      @update-table-options="tableDataOptions = $event"
    >
      <template #header-filter-slot-actions>
        <v-btn
          v-if="transactions.filters.isActive"
          class="clear-btn mx-auto mt-auto"
          color="primary"
          outlined
          @click="clearFilters()"
        >
          Clear Filters
          <v-icon class="ml-1 mt-1">
            mdi-close
          </v-icon>
        </v-btn>
      </template>
      <!-- header title slots -->
      <template #header-title-slot-statusCode="{ header }">
        {{ header.value }}
        <IconTooltip icon="mdi-information-outline">
          <div v-html="getStatusCodeHelpText()" />
        </IconTooltip>
      </template>
      <!-- header filter slots -->
      <template #header-filter-slot-createdOn>
        <div @click="scrollToDatePicker()">
          <v-text-field
            class="base-table__header__filter__textbox date-filter"
            :append-icon="'mdi-calendar'"
            clearable
            dense
            filled
            hide-details
            :placeholder="'Date'"
            :value="datePickerValue"
            @click:clear="dateRangeReset++"
          />
        </div>
      </template>
      <!-- item slots -->
      <template #item-slot-lineItemsAndDetails="{ item }">
        <b
          v-for="lineItem, i in item.lineItems"
          :key="lineItem.description + i"
          class="dark-text"
        >
          {{ lineItem.description }}
        </b><br>
        <span
          v-for="detail, i in item.details"
          :key="detail.label + i"
        >
          {{ detail.label }} {{ detail.value }}
        </span><br>
      </template>
      <template #item-slot-total="{ item }">
        <span v-if="item.statusCode === InvoiceStatus.CANCELLED">$0.00</span>
        <span v-else>{{ '$' + item.total.toFixed(2) }}</span>
      </template>
      <template #item-slot-statusCode="{ item }">
        <v-row no-gutters>
          <v-col cols="auto">
            <v-icon
              v-if="[InvoiceStatus.COMPLETED, InvoiceStatus.PAID, InvoiceStatus.REFUNDED, InvoiceStatus.CREDITED].includes(item.statusCode)"
              color="success"
              :style="{ 'margin-top': '-6px', 'margin-right': '2px' }"
            >
              mdi-check
            </v-icon>
            <v-icon
              v-if="InvoiceStatus.OVERDUE === item.statusCode"
              color="error"
              :style="{ 'margin-right': '2px' }"
            >
              mdi-alert
            </v-icon>
            <b>{{ getInvoiceStatus(item) }}</b>
            <br>
            <span
              v-if="item.updatedOn"
              v-html="displayDate(item.updatedOn)"
            />
          </v-col>
          <v-col
            class="pl-1"
            align-self="center"
          >
            <IconTooltip
              v-if="[InvoiceStatus.OVERDUE, InvoiceStatus.REFUND_REQUESTED, InvoiceStatus.REFUNDED, InvoiceStatus.CREDITED].includes(item.statusCode)"
              icon="mdi-information-outline"
              maxWidth="300px"
              :location="{top: true}"
            >
              <div v-sanitize="getHelpText(item)" />
            </IconTooltip>
          </v-col>
        </v-row>
      </template>
      <template #item-slot-downloads="{ item }">
        <div
          v-if="item.statusCode === InvoiceStatus.COMPLETED || item.statusCode === InvoiceStatus.PAID"
          class="receipt"
          @click="downloadReceipt(item)"
        >
          <v-icon
            color="primary"
          >
            mdi-file-pdf-outline
          </v-icon>
          <span>
            Receipt
          </span>
        </div>
      </template>
    </BaseVDataTable>
  </div>
</template>

<script lang="ts">
import { BaseVDataTable, DatePicker, IconTooltip } from '@/components'
import { InvoiceStatus, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { Ref, computed, defineComponent, nextTick, ref, watch } from '@vue/composition-api'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import { DataOptions } from 'vuetify'
import PaymentService from '@/services/payment.services'
import { Transaction } from '@/models'
import _ from 'lodash'
import { invoiceStatusDisplay } from '@/resources/display-mappers'
import moment from 'moment'
import { useTransactions } from '@/composables'

export default defineComponent({
  name: 'TransactionsDataTable',
  components: { BaseVDataTable: BaseVDataTable, DatePicker, IconTooltip },
  props: {
    extended: { default: false },
    headers: { default: [] as BaseTableHeaderI[] }
  },
  emit: ['isDownloadingReceipt'],
  setup (props, { emit }) {
    // refs
    const datePicker = ref(null)
    // composables
    const { transactions, loadTransactionList, clearAllFilters, setViewAll } = useTransactions()
    setViewAll(props.extended)

    const getHeaders = computed(() => props.headers)

    const getInvoiceStatus = (item: Transaction) => {
      // Special case for Online Banking - it shouldn't show NSF, should show Pending.
      if (item.paymentMethod === PaymentTypes.ONLINE_BANKING &&
        item.statusCode === InvoiceStatus.SETTLEMENT_SCHEDULED) {
        return invoiceStatusDisplay[InvoiceStatus.PENDING]
      }
      return invoiceStatusDisplay[item.statusCode]
    }

    // date picker stuff
    const dateRangeReset = ref(1)
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
      { description: 'Transaction is cancelled', value: invoiceStatusDisplay[InvoiceStatus.CANCELLED].toUpperCase() },
      { description: 'Funds received', value: invoiceStatusDisplay[InvoiceStatus.PAID].toUpperCase() },
      { description: 'Transaction created', value: invoiceStatusDisplay[InvoiceStatus.CREATED].toUpperCase() },
      { description: 'Funds have been credited', value: invoiceStatusDisplay[InvoiceStatus.CREDITED].toUpperCase() },
      { description: 'Transaction is waiting to be processed', value: invoiceStatusDisplay[InvoiceStatus.PENDING].toUpperCase() },
      { description: 'Transaction is in progress', value: invoiceStatusDisplay[InvoiceStatus.APPROVED].toUpperCase() },
      { description: 'Refund has been requested', value: invoiceStatusDisplay[InvoiceStatus.REFUND_REQUESTED].toUpperCase() },
      { description: 'Refund process is completed', value: invoiceStatusDisplay[InvoiceStatus.REFUNDED].toUpperCase() }
    ]
    const getStatusCodeHelpText = () => statusCodeDescs.reduce((text, statusCode) => {
      return `${text}<div class="mt-1">${statusCode.value} - ${statusCode.description}</div>`
    }, '')
    const getHelpText = (item: Transaction) => {
      switch (item?.statusCode) {
        case InvoiceStatus.REFUND_REQUESTED:
          return 'We are processing your refund request.<br/>It may take up to 7 business days to refund your total amount.'
        case InvoiceStatus.REFUNDED:
          return '$' + (item?.total?.toFixed(2) || '') + ' has been refunded to the account used for this transaction.'
        case InvoiceStatus.CREDITED:
          return '$' + (item?.total?.toFixed(2) || '') + ' has been credited to the account used for this transaction.'
        case InvoiceStatus.OVERDUE:
          return 'Your monthly statement is overdue.<br/>Please make your payment as soon as possible.'
        default:
          return ''
      }
    }

    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)

    watch(() => transactions.filters.pageNumber, (val: number) => { tableDataOptions.value.page = val })
    watch(() => tableDataOptions.value, (val: DataOptions) => {
      const newPage = val?.page || DEFAULT_DATA_OPTIONS.page
      const newLimit = val?.itemsPerPage || DEFAULT_DATA_OPTIONS.itemsPerPage
      // need this check or vi test continuously loops on initialization
      if (transactions.filters.pageNumber !== newPage || transactions.filters.pageLimit !== newLimit) {
        transactions.filters.pageNumber = val?.page || DEFAULT_DATA_OPTIONS.page
        transactions.filters.pageLimit = val?.itemsPerPage || DEFAULT_DATA_OPTIONS.itemsPerPage
        loadTransactionList()
      }
    })

    async function downloadReceipt (item: Transaction) {
      emit('isDownloadingReceipt', true)
      const currentAccount = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
      const receipt = await PaymentService.postReceipt(item, currentAccount.id)
      const filename = `bcregistry-receipts-${item.id}.pdf`
      CommonUtils.fileDownload(receipt.data, filename, 'application/pdf')
      emit('isDownloadingReceipt', false)
    }

    const displayDate = (val: string) => {
      const date = moment.utc(val).toDate()
      return CommonUtils.formatDisplayDate(date, 'MMMM DD, YYYY')
    }

    const datePickerValue = computed(() => {
      if (dateRangeSelected.value) {
        return 'Custom'
      }
      if (transactions.filters.filterPayload.dateFilter.isDefault) {
        return '1 Year'
      }
      return ''
    })

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
      getHelpText,
      getStatusCodeHelpText,
      tableDataOptions,
      transactions,
      displayDate,
      scrollToDatePicker,
      updateDateRange,
      loadTransactionList,
      getInvoiceStatus,
      datePickerValue,
      downloadReceipt
    }
  }
})
</script>

<style lang="scss" scoped>
.receipt {
  cursor: pointer;
  color: var(--v-primary-base);
}
.section-heading {
  background-color: $app-background-blue;
  border-radius: 5px 5px 0 0;
}
::v-deep .date-filter .v-input__slot,
::v-deep .date-filter .v-input__slot .v-text-field__slot input {
  cursor: pointer !important;
}
</style>
