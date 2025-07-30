<template>
  <v-app>
    <v-container>
      <h2 class="mb-4">
        MVP Refunds - OPS only for now.
      </h2>
      <v-text-field
        id="invoice-id-input"
        v-model="invoiceId"
        label="Invoice Number EG. (REG00012343 or 12343)"
      />
      <v-btn
        id="fetch-invoice-btn"
        :disabled="!invoiceId.trim()"
        @click="fetchInvoice"
      >
        Fetch Invoice
      </v-btn>
      <v-radio-group
        id="refund-type-radio-group"
        v-model="refundType"
        row
      >
        <v-radio
          id="radio-full-refund"
          label="Full refund"
          :value="RefundType.FULL"
        />
        <v-radio
          id="radio-partial-refund"
          label="Partial Refund"
          :value="RefundType.PARTIAL"
        />
      </v-radio-group>
      <v-alert
        v-if="showRefundCreditCardError()"
        id="partial-refund-cc-warning"
        class="mt-4"
        border="left"
        dense
        outlined
        prominent
        shaped
        text
        :type="'error'"
      >
        Partial Refunds can only be applied to credit card(DIRECT_PAY) invoices.
      </v-alert>
      <v-alert
        v-if="invoiceRefund > 0"
        id="refunded-warning"
        class="mt-4"
        border="left"
        dense
        outlined
        prominent
        shaped
        text
        :type="'error'"
      >
        This invoice has already been refunded for an amount of {{ formatAmount(invoiceRefund) }} previously.
      </v-alert>
      <div
        v-if="refundType === RefundType.PARTIAL"
        id="partial-refund-add-refund-info"
        class="mb-4"
      >
        <h4>
          Specify the fee amounts to be refunded and click 'Add to Refund', the refund summary entries will be appear for review.
        </h4>
      </div>
      <v-form ref="form">
        <v-simple-table id="invoice-line-items-table">
          <thead id="invoice-line-items-headers">
            <tr>
              <th
                v-for="(item, index) in headers"
                :id="'header-items-' + index"
                :key="index"
              >
                {{ item }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, index) in paymentLineItems"
              id="item-row"
              :key="index"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ item.description }}</td>
              <td>
                <v-text-field
                  v-model.number="item.filingFees"
                  type="number"
                  prefix="$"
                  :suffix="`/ ${formatAmount(item.filingFeesOriginal)}`"
                  :disabled="disableFeeInputs() || isRefundItemAdded(index)"
                  :rules="[validateRefundFeeAmount(item.filingFeesOriginal)]"
                  dense
                  hide-details="auto"
                />
              </td>
              <td>
                <v-text-field
                  v-model.number="item.priorityFees"
                  type="number"
                  prefix="$"
                  :suffix="`/ ${formatAmount(item.priorityFeesOriginal)}`"
                  :disabled="disableFeeInputs() || isRefundItemAdded(index)"
                  :rules="[validateRefundFeeAmount(item.priorityFeesOriginal)]"
                  dense
                  hide-details="auto"
                />
              </td>
              <td>
                <v-text-field
                  v-model.number="item.futureEffectiveFees"
                  type="number"
                  prefix="$"
                  :suffix="`/ ${formatAmount(item.futureEffectiveFeesOriginal)}`"
                  :disabled="disableFeeInputs() || isRefundItemAdded(index)"
                  :rules="[validateRefundFeeAmount(item.futureEffectiveFeesOriginal)]"
                  dense
                  hide-details="auto"
                />
              </td>
              <td>
                <v-text-field
                  v-model.number="item.serviceFees"
                  type="number"
                  prefix="$"
                  :suffix="`/ ${formatAmount(item.serviceFeesOriginal)}`"
                  :disabled="disableFeeInputs() || isRefundItemAdded(index)"
                  :rules="[validateRefundFeeAmount(item.serviceFeesOriginal)]"
                  dense
                  hide-details="auto"
                />
              </td>
              <td v-if="showPartialRefundAction()">
                <v-btn
                  id="partial-refund-action-btn"
                  small
                  :disabled="disablePartialRefundAction(item)"
                  @click="changeRefundPayload(item, index)"
                >
                  {{ isRefundItemAdded(index) ? 'Remove from Refund' : 'Add to Refund' }}
                </v-btn>
              </td>
            </tr>
          </tbody>
        </v-simple-table>
      </v-form>
      <v-divider class="mb-4" />
      <h2 class="mb-4">
        Refund Summary:
      </h2>
      <div
        v-if="refundType === RefundType.PARTIAL"
        id="partial-refund-summary-info"
        class="mb-4"
      >
        <h4>
          By pressing the refund action, the specified amounts in the summary below will be refunded.
        </h4>
      </div>
      <v-simple-table
        v-if="refundType === RefundType.PARTIAL"
        id="refund-summary-table"
      >
        <thead id="refund-summary-headers">
          <tr>
            <th
              v-for="(item, index) in headers.slice(0, -1)"
              :id="'header-summary-items-' + index"
              :key="index"
            >
              {{ item }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in refundItems"
            :key="index"
          >
            <td>{{ item + 1 }}</td>
            <td>{{ paymentLineItems[item].description }}</td>
            <td>{{ formatAmount(paymentLineItems[item].filingFees) }}</td>
            <td>{{ formatAmount(paymentLineItems[item].priorityFees) }}</td>
            <td>{{ formatAmount(paymentLineItems[item].futureEffectiveFees) }}</td>
            <td>{{ formatAmount(paymentLineItems[item].serviceFees) }}</td>
          </tr>
        </tbody>
      </v-simple-table>
      <div
        v-if="refundType === RefundType.FULL && paymentLineItems.length > 0"
      >
        <h3>
          By pressing the refund action, the full paid amount will be refunded: ${{ invoicePaid.toFixed(2) }}
        </h3>
      </div>
      <v-text-field
        v-model="refundComment"
        label="Refund Comment"
        :rules="[validateRefundComment]"
        required
      />
      <br>
      <v-btn
        id="process-refund-btn"
        :disabled="isRefundSubmitDisabled || isLoading"
        :loading="isLoading"
        @click="processRefund"
      >
        REFUND
      </v-btn>
      <v-alert
        v-if="refundResponse"
        class="mt-4"
        border="left"
        dense
        outlined
        prominent
        shaped
        text
        :type="refundResponse.includes('success') ? 'success' : 'error'"
      >
        {{ refundResponse }}
      </v-alert>
    </v-container>
  </v-app>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, reactive, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { Invoice } from '@/models/invoice'
import { PaymentTypes } from '@/util/constants'
import { useOrgStore } from '@/stores/org'

enum RefundType {
  FULL = 'full',
  PARTIAL = 'partial'
}

enum RefundLineTypes {
  BASE_FEES = 'BASE_FEES',
  FUTURE_EFFECTIVE_FEES = 'FUTURE_EFFECTIVE_FEES',
  PRIORITY_FEES = 'PRIORITY_FEES',
  SERVICE_FEES = 'SERVICE_FEES'
}

export default defineComponent({
  name: 'PaymentRefund',
  setup () {
    const headers = [
      'Line Item #',
      'Description',
      'Filing Fee',
      'Priority Fee',
      'Future Effective Fees',
      'Service Fees',
      'Action']
    const state = reactive({
      isLoading: false,
      form: null,
      shouldValidate: true,
      disableSubmit: false,
      invoiceId: '',
      invoicePaymentMethod: '',
      invoicePaid: 0,
      invoiceRefund: 0,
      paymentLineItems: [],
      refundItems: [],
      orgStore: useOrgStore(),
      refundComment: '',
      totalRefund: {
        baseFee: 0,
        serviceFee: 0,
        priorityFee: 0,
        futureEffectiveFee: 0
      },
      refundType: RefundType.FULL,
      refundResponse: ''
    })

    const validateRefundComment = (value: string) => {
      if (!state.shouldValidate) return true
      return !!value || 'Refund comment is required'
    }

    const validateRefundFeeAmount = (maxAmount: number) => (value: number) => {
      if (!state.shouldValidate) return true
      if (value > maxAmount) return `Refund amount exceeds $${maxAmount}`
      return (value >= 0) || 'Refund amount cannot be negative.'
    }

    function showRefundCreditCardError () {
      if (state.refundType !== RefundType.PARTIAL) return false
      return state.invoicePaymentMethod && state.invoicePaymentMethod !== PaymentTypes.DIRECT_PAY
    }

    function disableFeeInputs () {
      return state.refundType === RefundType.FULL ||
          state.invoicePaymentMethod !== PaymentTypes.DIRECT_PAY ||
          state.disableSubmit || state.invoiceRefund > 0
    }

    function disablePartialRefundAction (item: any) {
      return item.filingFees > item.filingFeesOriginal || item.filingFees < 0 ||
          item.priorityFees > item.priorityFeesOriginal || item.priorityFees < 0 ||
          item.futureEffectiveFees > item.futureEffectiveFeesOriginal || item.futureEffectiveFees < 0 ||
          item.serviceFees > item.serviceFeesOriginal || item.serviceFees < 0
    }

    function showPartialRefundAction () {
      return !disableFeeInputs() && state.refundType === RefundType.PARTIAL
    }

    function isRefundItemAdded (index) {
      return state.refundItems.includes(index)
    }

    function matchInvoiceId (invoiceId: string) {
      // Should resolve REG0031233 -> 31233 etc.
      return invoiceId.match(/\d+/)
    }

    function updateInvoiceState (invoice: any) {
      state.invoicePaid = invoice.paid
      state.invoiceRefund = invoice.refund
      state.invoicePaymentMethod = invoice.paymentMethod
      state.paymentLineItems = invoice.lineItems ? updateInvoiceLineItems(invoice.lineItems) : []
    }

    function updateInvoiceLineItems (lineItems: any) {
      return lineItems.map(item => ({
        ...item,
        ...Object.fromEntries(
          Object.entries(item).map(([key, value]) => [`${key}Original`, value])
        )
      }))
    }

    function fetchInvoice () {
      const invoiceId = matchInvoiceId(state.invoiceId)
      state.orgStore.getInvoice({ invoiceId: invoiceId }).then((invoice: Invoice) => {
        updateInvoiceState(invoice)
      }).catch((error: Error) => console.error('Failed to fetch invoice:', error))
      clearRefundState()
    }

    function getRefundPayload () {
      let refundPayload = {
        reason: state.refundComment,
        refundRevenue: []
      }
      if (state.refundType === RefundType.PARTIAL) {
        state.refundItems.forEach(index => {
          const item = state.paymentLineItems[index]
          const feeTypes = [
            { key: 'filingFees', type: RefundLineTypes.BASE_FEES },
            { key: 'priorityFees', type: RefundLineTypes.PRIORITY_FEES },
            { key: 'futureEffectiveFees', type: RefundLineTypes.FUTURE_EFFECTIVE_FEES },
            { key: 'serviceFees', type: RefundLineTypes.SERVICE_FEES }
          ]

          feeTypes.forEach(fee => {
            if (item[fee.key] > 0) {
              refundPayload.refundRevenue.push({
                paymentLineItemId: item.id,
                refundAmount: parseFloat(item[fee.key]),
                refundType: fee.type
              })
            }
          })
        })
      }
      return refundPayload
    }

    async function processRefund () {
      try {
        state.isLoading = true
        const invoiceId = matchInvoiceId(state.invoiceId)
        const response = await state.orgStore.refundInvoice(invoiceId, getRefundPayload())
        state.refundResponse = 'Refund successful.'
        state.disableSubmit = true
        console.log('Refund successful:', response)
      } catch (error) {
        state.disableSubmit = false
        state.refundResponse = 'Refund failed.'
        console.error('Refund process failed:', error)
      } finally {
        state.isLoading = false
      }
    }

    function changeRefundPayload (item, index) {
      const isRefunded = state.refundItems.includes(index)
      if (!isRefunded) {
        state.refundItems.push(index)
        state.refundItems.sort()
      } else {
        const itemIndex = state.refundItems.indexOf(index)
        state.refundItems.splice(itemIndex, 1)
      }

      // Recalculate totals based on current refundedItems
      state.totalRefund.baseFee = 0
      state.totalRefund.serviceFee = 0
      state.totalRefund.priorityFee = 0
      state.totalRefund.futureEffectiveFee = 0

      state.refundItems.forEach(refundedIndex => {
        const refundedItem = state.paymentLineItems[refundedIndex]
        state.totalRefund.baseFee += Number(refundedItem.filingFees)
        state.totalRefund.serviceFee += refundedItem.serviceFees
        state.totalRefund.priorityFee += refundedItem.priorityFees
        state.totalRefund.futureEffectiveFee += refundedItem.futureEffectiveFees
      })
    }

    async function clearRefundState () {
      state.disableSubmit = false
      state.shouldValidate = false
      state.totalRefund.baseFee = 0
      state.totalRefund.serviceFee = 0
      state.totalRefund.priorityFee = 0
      state.paymentLineItems = []
      state.refundItems = []
      state.refundComment = ''
      state.refundResponse = ''
      state.form.resetValidation()
      await nextTick()
      state.shouldValidate = true
    }

    const isRefundSubmitDisabled = computed(() => {
      return state.refundComment.trim().length === 0 || state.disableSubmit ||
        (state.refundType === RefundType.PARTIAL && state.refundItems.length === 0) ||
          state.invoiceRefund > 0
    })

    watch(() => state.invoiceId, () => {
      state.refundResponse = ''
    })

    return {
      ...toRefs(state),
      fetchInvoice,
      processRefund,
      getRefundPayload,
      changeRefundPayload,
      isRefundSubmitDisabled,
      isRefundItemAdded,
      RefundType,
      RefundLineTypes,
      validateRefundComment,
      validateRefundFeeAmount,
      disableFeeInputs,
      showPartialRefundAction,
      disablePartialRefundAction,
      showRefundCreditCardError,
      headers,
      formatAmount: CommonUtils.formatAmount
    }
  }
})

</script>
