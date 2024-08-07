<template>
  <div>
    <ModalDialog
      ref="confirmationDialog"
      max-width="720"
      :show-icon="false"
      :showCloseIcon="true"
      dialog-class="confirmation-dialog"
      :title="`${confirmDialogTitle}`"
    >
      <template #text>
        <p class="pt-4">
          {{ confirmDialogText }}
        </p>
      </template>
      <template #actions>
        <div class="d-flex justify-center dialog-button-container">
          <v-btn
            outlined
            large
            depressed
            class="mr-3"
            color="primary"
            data-test="btn-cancel-confirmation-dialog"
            @click="dialogConfirmClose"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            depressed
            class="font-weight-bold btn-dialog"
            data-test="btn-confirm-confirmation-dialog"
            color="primary"
            @click="dialogConfirm"
          >
            Confirm
          </v-btn>
        </div>
      </template>
    </ModalDialog>
    <ModalDialog
      ref="errorDialog"
      max-width="720"
      dialog-class="notify-dialog"
      :title="errorDialogTitle"
      :text="errorDialogText"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          data-test="dialog-ok-button"
          @click="dialogErrorClose"
        >
          Close
        </v-btn>
      </template>
    </ModalDialog>
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
          Short Name Payment History
        </h2>
      </template>
      <template #header-filter-slot />
      <template #item-slot-transactionDate="{ item }">
        <span>{{ formatDate(item.transactionDate, 'MMMM DD, YYYY') }}</span>
      </template>
      <template #item-slot-transactionDescription="{ item }">
        <span>{{ formatDescription(item) }}</span>
        <span
          v-if="isStatementTransaction(item)"
          class="transaction-details"
        >
          {{ formatAccountDisplayName(item) }}
        </span>
      </template>
      <template #item-slot-transactionAmount="{ item }">
        <span>{{ formatTransactionAmount(item) }}</span>
        <span class="transaction-details">{{ formatBalanceAmount(item) }}</span>
      </template>
      <template #item-slot-actions="{ item, index }">
        <div
          :id="`action-menu-${index}`"
          class="new-actions mx-auto"
        >
          <template v-if="item.isReversible">
            <v-btn
              small
              color="primary"
              min-width="5rem"
              min-height="2rem"
              class="open-action-btn single-action-btn"
              data-test="reverse-payment-button"
              :loading="loading"
              @click="showConfirmReversePaymentModal(item)"
            >
              Reverse Payment
            </v-btn>
          </template>
        </div>
      </template>
    </BaseVDataTable>
  </div>
</template>
<script lang="ts">
import { Ref, defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import {
  ShortNameHistoryType,
  ShortNameHistoryTypeDescription,
  ShortNamePaymentActions,
  ShortNameReversePaymentErrors
} from '@/util/constants'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '../../datatable/resources'
import { EFTTransactionState } from '@/models/eft-transaction'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'
import _ from 'lodash'
import moment from 'moment-timezone'

export default defineComponent({
  name: 'ShortNamePaymentHistory',
  components: { ModalDialog, BaseVDataTable },
  props: {
    shortNameDetails: {
      type: Object,
      default: () => ({
        shortName: null
      })
    }
  },
  setup (props, { emit }) {
    const enum ConfirmationType {
      REVERSE_PAYMENT = 'reversePayment',
    }
    const confirmationDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const errorDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const headers = [
      {
        col: 'transactionDate',
        hasFilter: false,
        width: '200px',
        value: 'Date'
      },
      {
        col: 'transactionDescription',
        hasFilter: false,
        width: '195px',
        value: 'Description'
      },
      {
        col: 'statementNumber',
        hasFilter: false,
        width: '250px',
        value: 'Related Statement Number'
      },
      {
        col: 'transactionAmount',
        hasFilter: false,
        width: '175px',
        value: 'Amount'
      },
      {
        col: 'actions',
        hasFilter: false,
        value: 'Actions',
        width: '150px'
      }
    ]

    const state = reactive<EFTTransactionState>({
      errorDialogTitle: '',
      errorDialogText: '',
      confirmDialogTitle: '',
      confirmDialogText: '',
      confirmObject: undefined,
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
        const response = await PaymentService.getEFTShortnameHistory(shortnameId, state.filters)
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

    function isStatementTransaction (item: any) {
      return item?.statementNumber
    }

    function formatTransactionAmount (item: any) {
      if (item.amount === undefined) return ''
      let amount = CommonUtils.formatAmount(item.amount)
      if (item.transactionType === ShortNameHistoryType.STATEMENT_PAID) {
        amount = `-${amount}`
      }
      return amount
    }

    function formatBalanceAmount (item: any) {
      if (item.shortNameBalance === undefined) return ''
      return `Balance: ${CommonUtils.formatAmount(item.shortNameBalance)}`
    }

    function formatDescription (item: any) {
      if (item.isProcessing) return `${ShortNameHistoryTypeDescription[item.transactionType]} (Processing)`
      return ShortNameHistoryTypeDescription[item.transactionType]
    }

    function formatTransactionDate (str: string): string {
      const date = moment.utc(str).toDate()
      return (date) ? moment(date).tz('America/Vancouver').format('MMMM D, YYYY') : ''
    }

    async function reversePayment (item: any) {
      state.loading = true
      try {
        const params = {
          action: ShortNamePaymentActions.REVERSE,
          statementId: item.statementNumber
        }
        await PaymentService.postShortnamePaymentAction(props.shortNameDetails.id, params)
      } catch (error) {
        state.loading = false
        handleReversePaymentError(error)
        console.error('An errored occurred reversing payment.', error)
      }
      emit('on-payment-action')
    }

    function handleReversePaymentError (error) {
      state.errorDialogTitle = 'Unable to Reverse Payment'
      switch (error.response?.data?.type) {
        case ShortNameReversePaymentErrors.INVALID_STATE:
          state.errorDialogText = 'Unable to reverse the payment due to an unprocessable state.'
          break
        case ShortNameReversePaymentErrors.UNPAID_STATEMENT:
          state.errorDialogText = 'Unpaid statement cannot be reversed.'
          break
        case ShortNameReversePaymentErrors.UNPAID_STATEMENT_INVOICE:
          state.errorDialogText = 'Unpaid statement invoice cannot be reversed.'
          break
        case ShortNameReversePaymentErrors.EXCEEDS_SIXTY_DAYS:
          state.errorDialogText = 'This statement exceeds the allowable reverse period of 60 days.'
          break
        default:
          state.errorDialogTitle = 'Something Went Wrong'
          state.errorDialogText = 'An error occurred while trying to reverse a payment.'
          break
      }

      errorDialog.value.open()
    }

    function dialogConfirm () {
      confirmationDialog.value.close()
      const confirmationType = state.confirmObject.type
      if (confirmationType === ConfirmationType.REVERSE_PAYMENT) {
        reversePayment(state.confirmObject.item)
      }
      resetConfirmationDialog()
    }

    function dialogConfirmClose () {
      confirmationDialog.value.close()
    }

    function resetConfirmationDialog () {
      state.confirmDialogTitle = ''
      state.confirmDialogText = ''
      state.confirmObject = undefined
    }

    function showConfirmReversePaymentModal (item) {
      state.confirmDialogTitle = 'Reverse Payment'
      state.confirmDialogText = 'The paid amount will be reversed to the short name, marking the transactions ' +
          'and statement as unpaid. The System will then notify the client with a payment reminder.'
      state.confirmObject = { item: item, type: ConfirmationType.REVERSE_PAYMENT }
      confirmationDialog.value.open()
    }

    function dialogErrorClose () {
      errorDialog.value.close()
    }

    return {
      ...toRefs(state),
      errorDialog,
      confirmationDialog,
      formatBalanceAmount,
      formatTransactionAmount,
      formatDate: formatTransactionDate,
      formatAccountDisplayName: CommonUtils.formatAccountDisplayName,
      formatDescription,
      dialogConfirm,
      dialogConfirmClose,
      dialogErrorClose,
      showConfirmReversePaymentModal,
      headers,
      state,
      infiniteScrollCallback,
      calculateTableHeight,
      isStatementTransaction
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
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

.dialog-button-container {
  width: 100%;
  .v-btn {
    width: 106px
  }
}

</style>
