<template>
  <v-app>
    <v-container>
      <h2 class="mb-4">
        MVP Refunds - OPS only for now.
      </h2>
      <v-text-field
        v-model="invoiceId"
        label="Invoice Number EG. (REG00012343 or 12343)"
        @keyup.enter="invoiceId.trim() && fetchInvoice()"
      />
      <v-btn
        :disabled="!invoiceId.trim()"
        @click="fetchInvoice"
      >
        Fetch Invoice
      </v-btn>
      <v-radio-group
        v-model="refundType"
        row
      >
        <v-radio
          label="Full refund"
          :value="RefundType.FULL"
        />
        <v-radio
          label="Partial Refund"
          :value="RefundType.PARTIAL"
        />
      </v-radio-group>
      <v-alert
          v-if="showRefundCreditCardError()"
          class="mt-4"
          border="left"
          dense
          outlined
          prominent
          shaped
          text
          :type="'error'"
      >
        Partial Refunds can only be applied to credit card invoices.
      </v-alert>
      <div v-if="refundType === RefundType.PARTIAL"
           class="mb-4"
      >
        <h4>
          Specify the fee amounts to be refunded and click 'Add to Refund', the refund summary entries will be appear for review.
        </h4>
      </div>
      <v-form ref="form">
        <v-simple-table>
          <thead>
            <tr>
              <th
                  :id="'header-items-' + index"
                  v-for="(item, index) in headers"
                  :key="index"
              >
                {{ item }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(item, index) in paymentLineItems"
              :key="index"
            >
              <td>{{ index + 1 }}</td>
              <td>{{ item.description }}</td>
              <td>
                <v-text-field
                  v-model.number="item.filingFees"
                  type="number"
                  prefix="$"
                  :suffix="`/ $${item.filingFeesOriginal}`"
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
                  :suffix="`/ $${item.priorityFeesOriginal}`"
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
                  :suffix="`/ $${item.futureEffectiveFeesOriginal}`"
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
                  :suffix="`/ $${item.serviceFeesOriginal}`"
                  :disabled="disableFeeInputs() || isRefundItemAdded(index)"
                  :rules="[validateRefundFeeAmount(item.serviceFeesOriginal)]"
                  dense
                  hide-details="auto"
                />
              </td>
              <td v-if="showPartialRefundAction()">
                <v-btn
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
      <div v-if="refundType === RefundType.PARTIAL"
           class="mb-4"
      >
        <h4>
          By pressing the refund action, the specified amounts in the summary below will be refunded.
        </h4>
      </div>
      <v-simple-table v-if="refundType === RefundType.PARTIAL">
        <thead>
        <tr>
          <th
              :id="'header-summary-items-' + index"
              v-for="(item, index) in headers.slice(0, -1)"
              :key="index"
          >
            {{ item }}
          </th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item, index) in refundItems"
            :key="index"
        >
          <td>{{ item + 1 }}</td>
          <td>{{ paymentLineItems[item].description }}</td>
          <td>${{ paymentLineItems[item].filingFees }}</td>
          <td>${{ paymentLineItems[item].priorityFees }}</td>
          <td>${{ paymentLineItems[item].futureEffectiveFees }}</td>
          <td>${{ paymentLineItems[item].serviceFees }}</td>
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
        :disabled="isRefundSubmitDisabled"
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
      form: null,
      shouldValidate: true,
      disableSubmit: false,
      invoiceId: '',
      invoicePaymentMethod: '',
      invoicePaid: 0,
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
      return (value <= maxAmount) || `Refund amount exceeds $${maxAmount}`
    }

    function showRefundCreditCardError() {
      if (state.refundType !== RefundType.PARTIAL) return false
      return state.invoicePaymentMethod && state.invoicePaymentMethod !== PaymentTypes.DIRECT_PAY
    }

    function disableFeeInputs() {
      return state.refundType === RefundType.FULL ||
          state.invoicePaymentMethod !== PaymentTypes.DIRECT_PAY ||
          state.disableSubmit
    }

    function disablePartialRefundAction(item: any) {
      return item.filingFees > item.filingFeesOriginal ||
          item.priorityFees > item.priorityFeesOriginal ||
          item.futureEffectiveFees > item.futureEffectiveFeesOriginal ||
          item.serviceFees > item.serviceFeesOriginal
    }

    function showPartialRefundAction() {
      return !disableFeeInputs() && state.refundType === RefundType.PARTIAL
    }

    function isRefundItemAdded(index) {
      return state.refundItems.includes(index)
    }

    function matchInvoiceId (invoiceId: string) {
      // Should resolve REG0031233 -> 31233 etc.
      return invoiceId.match(/\d+/)
    }
    function fetchInvoice () {
      const invoiceId = matchInvoiceId(state.invoiceId)
      state.orgStore.getInvoice({ invoiceId: invoiceId }).then((invoice: Invoice) => {
        state.invoicePaid = invoice.paid
        state.invoicePaymentMethod = invoice.paymentMethod
        state.paymentLineItems = invoice.lineItems ? invoice.lineItems.map(item => ({
          ...item,
          ...Object.fromEntries(
            Object.entries(item).map(([key, value]) => [`${key}Original`, value])
          ),
          isEditable: true
        })) : []
      }).catch((error: Error) => console.error('Failed to fetch invoice:', error))
      clearRefundState()
    }

    async function processRefund () {
      try {
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

        const invoiceId = matchInvoiceId(state.invoiceId)
        const response = await state.orgStore.refundInvoice(invoiceId, refundPayload)
        state.refundResponse = 'Refund successful.'
        state.disableSubmit = true
        console.log('Refund successful:', response)
      } catch (error) {
        state.refundResponse = 'Refund failed.'
        console.error('Refund process failed:', error)
      }
    }

    function changeRefundPayload (item, index) {
      const isRefunded = state.refundItems.includes(index)
      if (!isRefunded) {
        // Mark as refunded and make non-editable
        item.isEditable = false
        state.refundItems.push(index)
        state.refundItems.sort()
      } else {
        // If removing from refund, make editable again
        item.isEditable = true
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
        (state.refundType === RefundType.PARTIAL && state.totalRefund.baseFee === 0 && state.totalRefund.serviceFee === 0)
    })

    watch(() => state.invoiceId, () => {
      state.refundResponse = ''
    })

    return {
      ...toRefs(state),
      fetchInvoice,
      processRefund,
      changeRefundPayload,
      isRefundSubmitDisabled,
      isRefundItemAdded,
      RefundType,
      validateRefundComment,
      validateRefundFeeAmount,
      disableFeeInputs,
      showPartialRefundAction,
      disablePartialRefundAction,
      showRefundCreditCardError,
      headers
    }
  }
})

</script>
