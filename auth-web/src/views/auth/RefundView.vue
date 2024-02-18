<template>
  <!-- TODO: Note this code is very rough and will need to be rewritten. -->
  <v-app>
    <v-container>
      <h2 class="mb-4">
        MVP Refunds - OPS only for now.
      </h2>
      <v-text-field
        v-model="invoiceId"
        label="Invoice Number EG. (REG00012343 or 12343)"
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
      <v-simple-table>
        <thead>
          <tr>
            <th>Line Item #</th>
            <th>Description</th>
            <th>Filing Fee</th>
            <th>Priority Fees</th>
            <th>Future Effective Fees</th>
            <th>Service Fees</th>
            <th v-if="refundType === RefundType.PARTIAL">
              Actions
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
                v-model.number="item.total"
                type="number"
                :disabled="refundType === RefundType.FULL"
                dense
                hide-details="auto"
              />
            </td>

            <td>
              <v-text-field
                v-model.number="item.priorityFees"
                type="number"
                :disabled="refundType === RefundType.FULL"
                dense
                hide-details="auto"
              />
            </td>
            <td>
              <v-text-field
                v-model.number="item.futureEffectiveFees"
                type="number"
                :disabled="refundType === RefundType.FULL"
                dense
                hide-details="auto"
              />
            </td>
            <td>
              <v-text-field
                v-model.number="item.serviceFees"
                type="number"
                :disabled="refundType === RefundType.FULL"
                dense
                hide-details="auto"
              />
            </td>
            <td v-if="refundType === RefundType.PARTIAL">
              <v-btn
                small
                @click="changeRefundPayload(item, index)"
              >
                {{ refundedItems.includes(index) ? 'Remove from Refund' : 'Add to Refund' }}
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-simple-table>
      <v-divider class="mb-4" />
      <h2 class="mb-4">
        Refund Summary:
      </h2>
      <!-- TODO: this wont work for multiple payment line items, but we can worry about that after the demo. -->
      <div v-if="totalRefund.baseFee">
        Base Fee from: ${{ paymentLineItems[0].filingFees.toFixed(2) }} -> ${{ totalRefund.baseFee.toFixed(2) }}
      </div>
      <div v-if="totalRefund.serviceFee">
        Service Fee from: ${{ totalRefund.serviceFee.toFixed(2) }} -> ${{ totalRefund.serviceFee.toFixed(2) }}
      </div>
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
        :rules="[v => !!v || 'Refund comment is required']"
        required
      />
      <br>
      <v-btn
        :disabled="isFinalizeDisabled"
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

import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { Invoice } from '@/models/invoice'
import { useOrgStore } from '@/stores/org'

enum RefundType {
  FULL = 'full',
  PARTIAL = 'partial'
}

enum RefundLineTypes {
  OTHER_FEES = 'OTHER_FEES',
  SERVICE_FEE = 'SERVICE_FEE',
}

export default defineComponent({
  name: 'PaymentRefund',
  setup () {
    const state = reactive({
      invoiceId: '',
      invoicePaid: 0,
      paymentLineItems: [],
      refundedItems: [],
      orgStore: useOrgStore(),
      refundComment: '',
      totalRefund: {
        baseFee: 0,
        serviceFee: 0,
        priorityFee: 0
      },
      refundType: RefundType.FULL,
      refundResponse: ''
    })

    function fetchInvoice () {
      // Should resolve REG0031233 -> 31233 etc.
      const invoiceId = state.invoiceId.match(/\d+/)
      state.orgStore.getInvoice({ invoiceId: invoiceId }).then((invoice: Invoice) => {
        state.invoicePaid = invoice.paid
        state.paymentLineItems = invoice.lineItems ? invoice.lineItems.map(item => ({
          ...item,
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
          state.refundedItems.forEach(index => {
            const item = state.paymentLineItems[index]
            if (item.total > 0) {
              refundPayload.refundRevenue.push({
                paymentLineItemId: item.id,
                refundAmount: parseFloat(item.total),
                refundType: RefundLineTypes.OTHER_FEES
              })
            }
            if (item.serviceFees > 0) {
              refundPayload.refundRevenue.push({
                paymentLineItemId: item.id,
                refundAmount: item.serviceFees,
                refundType: RefundLineTypes.SERVICE_FEE
              })
            }
          })
        } else {
          delete refundPayload.refundRevenue
        }

        const response = await state.orgStore.refundInvoice(state.invoiceId, refundPayload)
        state.refundResponse = 'Refund successful.'
        console.log('Refund successful:', response)
      } catch (error) {
        state.refundResponse = 'Refund failed.'
        console.error('Refund process failed:', error)
      }
    }

    function changeRefundPayload (item, index) {
      const isRefunded = state.refundedItems.includes(index)
      if (!isRefunded) {
        // Mark as refunded and make non-editable
        item.isEditable = false
        state.refundedItems.push(index)
      } else {
        // If removing from refund, make editable again
        item.isEditable = true
        const itemIndex = state.refundedItems.indexOf(index)
        state.refundedItems.splice(itemIndex, 1)
      }

      // Recalculate totals based on current refundedItems
      state.totalRefund.baseFee = 0
      state.totalRefund.serviceFee = 0
      state.totalRefund.priorityFee = 0

      state.refundedItems.forEach(refundedIndex => {
        const refundedItem = state.paymentLineItems[refundedIndex]
        state.totalRefund.baseFee += Number(refundedItem.total)
        state.totalRefund.serviceFee += refundedItem.serviceFees
        state.totalRefund.priorityFee += refundedItem.priorityFees
      })
    }

    function clearRefundState () {
      state.totalRefund.baseFee = 0
      state.totalRefund.serviceFee = 0
      state.totalRefund.priorityFee = 0
      state.paymentLineItems = []
      state.refundedItems = []
    }

    const isFinalizeDisabled = computed(() => {
      return state.refundComment.trim().length === 0 ||
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
      isFinalizeDisabled,
      RefundType
    }
  }
})

</script>
