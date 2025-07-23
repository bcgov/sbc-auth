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
      :setExpanded="expandedRows"
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
        <div class="d-flex align-center">
          <div
            v-if="hasDropdownContent(item)"
            class="expand-icon-container mr-2 mb-4"
            @click="toggleExpanded(item)"
          >
            <v-icon
              v-if="isExpanded(item)"
              class="expansion-icon"
              color="white"
            >
              mdi-chevron-up
            </v-icon>
            <v-icon
              v-else
              class="expansion-icon"
              color="white"
            >
              mdi-chevron-down
            </v-icon>
          </div>
          <div>
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
          </div>
        </div>
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
              v-if="[InvoiceStatus.OVERDUE, InvoiceStatus.REFUND_REQUESTED].includes(item.statusCode)"
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
      <!-- Expanded item template for dropdown rows -->
      <template #expanded-item="{ item }">
        <tr
          v-for="dropdownItem in getDropdownItems(item)"
          :key="dropdownItem.id"
          class="dropdown-row"
        >
          <td
            v-if="isColumnVisible('lineItemsAndDetails')"
            class="dropdown-cell"
          >
            <span class="dropdown-item-type ml-8">{{ dropdownItem.type }}</span>
          </td>
          <td
            v-if="isColumnVisible('folioNumber')"
            class="dropdown-cell"
          >
            <div class="dropdown-item-folio">
              {{ dropdownItem.folioNumber }}
            </div>
          </td>
          <td
            v-if="isColumnVisible('createdName')"
            class="dropdown-cell"
          >
            <div class="dropdown-item-created-name">
              {{ dropdownItem.createdName === 'None None' ? '-' : dropdownItem.createdName }}
            </div>
          </td>
          <td
            v-if="isColumnVisible('createdOn')"
            class="dropdown-cell"
          >
            <div class="dropdown-item-date">
              {{ displayDate(dropdownItem.date) }}
            </div>
            <div
              v-if="dropdownItem.time"
              class="dropdown-item-time"
            >
              {{ displayTime(dropdownItem.date) }}
            </div>
          </td>
          <td
            v-if="isColumnVisible('total')"
            class="dropdown-cell"
          >
            <div
              class="dropdown-item-amount font-weight-bold"
              :class="{ 'refund-amount': dropdownItem.isRefund }"
            >
              {{ dropdownItem.amount }}
            </div>
          </td>
          <td
            v-if="isColumnVisible('id')"
            class="dropdown-cell"
          >
            <div class="dropdown-item-transaction-id">
              {{ dropdownItem.transactionId }}
            </div>
          </td>
          <td
            v-if="isColumnVisible('invoiceNumber')"
            class="dropdown-cell"
          >
            <div class="dropdown-item-invoice-number">
              {{ dropdownItem.invoiceNumber }}
            </div>
          </td>
          <td
            v-if="isColumnVisible('paymentMethod')"
            class="dropdown-cell"
          >
            <div class="dropdown-item-payment-method">
              {{ getDropdownPaymentMethodDisplay(dropdownItem.paymentMethod) }}
            </div>
          </td>
          <td
            v-if="isColumnVisible('statusCode')"
            class="dropdown-cell"
          >
            <div class="dropdown-item-status">
              <v-icon
                color="success"
                style="margin-top: -6px; margin-right: 2px;"
              >
                mdi-check
              </v-icon>
              <span style="font-weight: bold;">{{ dropdownItem.status }}</span>
            </div>
          </td>
          <td
            v-if="isColumnVisible('downloads')"
            class="dropdown-cell"
          >
            <!-- Empty cell for downloads column -->
          </td>
          <td
            v-if="isColumnVisible('actions')"
            class="dropdown-cell"
          >
            <!-- Empty cell for actions column -->
          </td>
        </tr>
      </template>
    </BaseVDataTable>
  </div>
</template>

<script lang="ts">
import { BaseVDataTable, DatePicker, IconTooltip } from '@/components'
import { InvoiceStatus, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { Ref, computed, defineComponent, nextTick, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { invoiceStatusDisplay, paymentTypeDisplay } from '@/resources/display-mappers'
import { BaseTableHeaderI } from '@/components/datatable/interfaces'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import { DataOptions } from 'vuetify'
import PaymentService from '@/services/payment.services'
import { Transaction } from '@/models'
import _ from 'lodash'
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
    const state = reactive({
      expandedRows: [] as number[]
    })
    const datePicker = ref(null)
    // composables
    const { transactions, loadTransactionList, clearAllFilters, setViewAll } = useTransactions()
    setViewAll(props.extended)

    const getHeaders = computed(() => props.headers)

    const isColumnVisible = (columnName: string): boolean => {
      return props.headers.some(header => header.col === columnName)
    }

    const getInvoiceStatus = (item: Transaction) => {
      // Special case for Online Banking - it shouldn't show NSF, should show Pending.
      if (item.paymentMethod === PaymentTypes.ONLINE_BANKING &&
        item.statusCode === InvoiceStatus.SETTLEMENT_SCHEDULED) {
        return invoiceStatusDisplay[InvoiceStatus.PENDING]
      }
      // Check for partial refunds - this should take priority
      if (item.partialRefunds?.length > 0) {
        if ([PaymentTypes.ONLINE_BANKING, PaymentTypes.PAD].includes(item.paymentMethod)) {
          return invoiceStatusDisplay[InvoiceStatus.PARTIALLY_CREDITED]
        } else {
          return invoiceStatusDisplay[InvoiceStatus.PARTIALLY_REFUNDED]
        }
      }
      return invoiceStatusDisplay[item.statusCode]
    }

    const hasDropdownContent = (item: Transaction): boolean => {
      if (item.appliedCredits?.length > 0) {
        const totalAppliedCredits = item.appliedCredits.reduce((sum, credit) => sum + credit.amountApplied, 0)
        const remainingAmount = item.total - totalAppliedCredits
        return remainingAmount > 0
      }

      const hasContent = item.statusCode === InvoiceStatus.CREDITED ||
             item.partialRefunds?.length > 0 ||
             item.statusCode === InvoiceStatus.REFUNDED
      return hasContent
    }

    const expandedState = computed(() => {
      const expandedMap = new Map()
      state.expandedRows.forEach(id => {
        expandedMap.set(id, true)
      })
      return expandedMap
    })

    const isExpanded = (item: Transaction): boolean => {
      return expandedState.value.has(item.id)
    }

    const expandedRows = computed(() => {
      return transactions.results.filter(item =>
        state.expandedRows.includes(item.id)
      )
    })

    const toggleExpanded = (item: Transaction) => {
      if (isExpanded(item)) {
        state.expandedRows = state.expandedRows.filter(expandedItem => expandedItem !== item.id)
      } else {
        state.expandedRows.push(item.id)
      }
    }

    const getDropdownPaymentMethodDisplay = (paymentMethod: PaymentTypes, item?: Transaction): string => {
      // Special case for applied credits (only for main table, not dropdown)
      if (item?.appliedCredits?.length > 0) {
        const totalAppliedCredits = item.appliedCredits.reduce((sum, credit) => sum + credit.amountApplied, 0)
        const remainingAmount = item.total - totalAppliedCredits

        if (remainingAmount > 0) {
          if (item.paymentMethod === PaymentTypes.PAD) {
            return `${paymentTypeDisplay[PaymentTypes.CREDIT]} and ${paymentTypeDisplay[PaymentTypes.PAD]}`
          } else if (item.paymentMethod === PaymentTypes.ONLINE_BANKING) {
            return `${paymentTypeDisplay[PaymentTypes.CREDIT]} and ${paymentTypeDisplay[PaymentTypes.ONLINE_BANKING]}`
          }
        } else {
          return paymentTypeDisplay[PaymentTypes.CREDIT]
        }
      }
      return paymentTypeDisplay[paymentMethod] || paymentMethod
    }

    const getDropdownItems = (item: Transaction) => {
      const dropdownItems = []
      if (item.appliedCredits?.length > 0) {
        const totalAppliedCredits = item.appliedCredits.reduce((sum, credit) => sum + credit.amountApplied, 0)
        const remainingAmount = item.total - totalAppliedCredits

        item.appliedCredits.forEach(credit => {
          dropdownItems.push({
            id: `credit-${credit.id}`,
            type: '',
            date: credit.createdOn,
            time: true,
            amount: `$${credit.amountApplied.toFixed(2)}`,
            paymentMethod: paymentTypeDisplay[PaymentTypes.CREDIT],
            isRefund: false,
            status: invoiceStatusDisplay[InvoiceStatus.COMPLETED],
            folioNumber: item.folioNumber,
            createdName: item.createdName,
            transactionId: credit.id,
            invoiceNumber: item.invoiceNumber
          })
        })

        // Only add remaining amount row if there's a remaining balance
        if (remainingAmount > 0) {
          dropdownItems.push({
            id: `remaining-${item.id}`,
            type: '',
            date: item.appliedCredits[0].createdOn,
            time: true,
            amount: `$${remainingAmount.toFixed(2)}`,
            paymentMethod: item.paymentMethod,
            isRefund: false,
            status: invoiceStatusDisplay[InvoiceStatus.COMPLETED],
            folioNumber: item.folioNumber,
            createdName: item.createdName,
            transactionId: item.id,
            invoiceNumber: item.invoiceNumber
          })
        }
      }
      if (item.partialRefunds?.length > 0) {
        // Combine all partial refunds and sum their amounts
        const totalRefundAmount = item.partialRefunds.reduce((sum, refund) => sum + refund.refundAmount, 0)
        const isRefundAsCredits = [PaymentTypes.ONLINE_BANKING, PaymentTypes.PAD].includes(item.paymentMethod)
        const refundIds = item.partialRefunds.map(refund => refund.paymentLineItemId).join(', ')

        dropdownItems.push({
          id: `refund-${item.id}`,
          type: isRefundAsCredits ? 'Refund as credits' : 'Refund',
          date: item.partialRefunds[0].createdOn,
          time: false,
          amount: `-$${totalRefundAmount.toFixed(2)}`,
          paymentMethod: isRefundAsCredits ? paymentTypeDisplay[PaymentTypes.CREDIT] : item.paymentMethod,
          isRefund: true,
          status: isRefundAsCredits ? invoiceStatusDisplay[InvoiceStatus.PARTIALLY_CREDITED] : invoiceStatusDisplay[InvoiceStatus.PARTIALLY_REFUNDED],
          folioNumber: item.folioNumber,
          createdName: item.partialRefunds[0].createdName,
          transactionId: refundIds,
          invoiceNumber: item.invoiceNumber
        })
      }
      if ([InvoiceStatus.REFUNDED, InvoiceStatus.CREDITED].includes(item.statusCode)) {
        const isRefundAsCredits = [PaymentTypes.ONLINE_BANKING, PaymentTypes.PAD].includes(item.paymentMethod)
        dropdownItems.push({
          id: `full-${item.id}`,
          type: item.statusCode === InvoiceStatus.CREDITED ? 'Refund as credits' : 'Refund',
          date: item.refundDate || item.createdOn,
          time: true,
          amount: `-$${item.total.toFixed(2)}`,
          paymentMethod: isRefundAsCredits ? paymentTypeDisplay[PaymentTypes.CREDIT] : item.paymentMethod,
          isRefund: true,
          status: [PaymentTypes.ONLINE_BANKING, PaymentTypes.PAD].includes(item.paymentMethod)
            ? invoiceStatusDisplay[InvoiceStatus.CREDITED] : invoiceStatusDisplay[InvoiceStatus.REFUNDED],
          folioNumber: item.folioNumber,
          createdName: item.createdName,
          transactionId: item.id,
          invoiceNumber: item.invoiceNumber
        })
      }

      return dropdownItems
    }

    // date picker stuff
    const dateRangeReset = ref(1)
    const dateRangeSelected = ref(false)
    const showDatePicker = ref(false)
    const scrollToDatePicker = async () => {
      showDatePicker.value = true
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

    const clearFiltersTrigger = ref(0)
    const clearFilters = () => {
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
      { description: 'Refund process is completed', value: invoiceStatusDisplay[InvoiceStatus.REFUNDED].toUpperCase() },
      { description: 'Funds have been partially credited', value: invoiceStatusDisplay[InvoiceStatus.PARTIALLY_CREDITED].toUpperCase() },
      { description: 'Partial refund process is completed', value: invoiceStatusDisplay[InvoiceStatus.PARTIALLY_REFUNDED].toUpperCase() }
    ]
    const getStatusCodeHelpText = () => statusCodeDescs.reduce((text, statusCode) => {
      return `${text}<div class="mt-1">${statusCode.value} - ${statusCode.description}</div>`
    }, '')
    const getHelpText = (item: Transaction) => {
      switch (item?.statusCode) {
        case InvoiceStatus.REFUND_REQUESTED:
          return 'We are processing your refund request.<br/>It may take up to 7 business days to refund your total amount.'
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

    const displayTime = (val: string) => {
      const date = moment.utc(val).toDate()
      return CommonUtils.formatDisplayDate(date, 'h:mm A')
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
      ...toRefs(state),
      InvoiceStatus,
      clearFilters,
      clearFiltersTrigger,
      datePicker,
      dateRangeReset,
      dateRangeSelected,
      getHeaders,
      hasDropdownContent,
      isExpanded,
      isColumnVisible,
      expandedRows,
      getDropdownItems,
      toggleExpanded,
      getDropdownPaymentMethodDisplay,
      invoiceStatusDisplay,
      showDatePicker,
      statusCodeDescs,
      getHelpText,
      getStatusCodeHelpText,
      tableDataOptions,
      transactions,
      displayDate,
      displayTime,
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

.dropdown-row {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

s.dropdown-cell {
  padding: 8px 0 8px 16px;
  font-size: 0.875rem;
  vertical-align: top;
  border: 0px;
}

.expansion-icon {
  background-color: $app-blue;
  border-radius: 50%;
  color: white !important;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}
</style>
