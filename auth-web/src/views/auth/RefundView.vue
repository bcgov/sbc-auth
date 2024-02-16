<template>
  <v-app>
    <v-container>
      <v-text-field
        v-model="invoiceId"
        label="Invoice ID"
      />
      <v-btn
        :disabled="!invoiceId.trim()"
        @click="fetchInvoice"
      >
        Fetch Invoice
      </v-btn>
      <v-checkbox
        v-model="isPartialRefund"
        label="Partial Refund"
        :disabled="isFullRefund"
      />
      <v-checkbox
        v-model="isFullRefund"
        label="Full Refund"
        :disabled="isPartialRefund"
      />
      <br>
      Invoice number #{{ invoiceId }}
      <br>
      <v-simple-table>
        <thead>
          <tr>
            <th>Line Item #</th>
            <th>Description</th>
            <th>Base Fee($)</th>
            <th>Service Fees($)</th>
            <th>priority Fees($)</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(item, index) in paymentLineItems"
            :key="index"
          >
            <td>{{ index + 1 }}</td>
            <td>{{ item.description }}</td>
            <td><v-text-field
              v-model="item.total"
              type="number"
              :disabled="!item.isEditable"
              dense
              hide-details="auto"
            /></td>
            <td><v-text-field
              v-model="item.serviceFees"
              type="number"
              :disabled="!item.isEditable"
              dense
              hide-details="auto"
            /></td>
            <td><v-text-field
              v-model="item.priorityFees"
              type="number"
              :disabled="!item.isEditable"
              dense
              hide-details="auto"
            /></td>

            <td v-if="!isFullRefund">
              <v-btn
                small
                :disabled="isFullRefund"
                @click="addToRefund(item, index)"
              >
                {{ refundedItems.includes(index) ? 'Remove from Refund' : 'Add to Refund' }}
              </v-btn>
            </td>
          </tr>
        </tbody>
      </v-simple-table>
      <br>
      Refund Summary:
      <div v-if="totalRefund.baseFee">
        Base Fee: ${{ totalRefund.baseFee.toFixed(2) }}
      </div>
      <div v-if="totalRefund.serviceFee">
        Service Fee: ${{ totalRefund.serviceFee.toFixed(2) }}
      </div>
      <div v-if="totalRefund.priorityFee">
        priorityFee Fee: ${{ totalRefund.priorityFee.toFixed(2) }}
      </div>
      <div v-if="isFullRefund">
        Paid: {{ invoicePaid }}
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
    </v-container>
  </v-app>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { Invoice } from '@/models/invoice'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'PaymentRefund',
  setup () {
    const state = reactive({
      invoiceId: '',
      invoicePaid: 0,
      paymentLineItems: [],
      isFullRefund: false,
      isPartialRefund: true,
      refundedItems: [],
      orgStore: useOrgStore(),
      refundComment: '',
      totalRefund: {
        baseFee: 0,
        serviceFee: 0,
        priorityFee: 0
      }
    })

    function fetchInvoice () {
      state.orgStore.getInvoice({ invoiceId: state.invoiceId }).then((invoice: Invoice) => {
        state.invoicePaid = invoice.paid
        state.paymentLineItems = invoice.lineItems ? invoice.lineItems.map(item => ({
          ...item,
          isEditable: true
        })) : []
      }).catch((error: Error) => console.error('Failed to fetch invoice:', error))
    }

    async function processRefund () {
      try {
        let refundPayload = {
          reason: state.refundComment,
          refundRevenue: []
        }

        if (!state.isFullRefund) {
          state.refundedItems.forEach(index => {
            const item = state.paymentLineItems[index]
            if (item.total > 0) {
              refundPayload.refundRevenue.push({
                paymentLineItemId: item.id,
                refundAmount: item.total,
                refundType: 'OTHER_FEES'
              })
            }
            if (item.serviceFees > 0) {
              refundPayload.refundRevenue.push({
                paymentLineItemId: item.id,
                refundAmount: item.serviceFees,
                refundType: 'SERVICE_FEE'
              })
            }
            if (item.priorityFees > 0) {
              refundPayload.refundRevenue.push({
                paymentLineItemId: item.id,
                refundAmount: item.priorityFees,
                refundType: 'PRIORITY_FEE'
              })
            }
          })
        } else {
          delete refundPayload.refundRevenue
        }

        const response = await state.orgStore.refundInvoice(state.invoiceId, refundPayload)
        console.log('Refund successful:', response)
      } catch (error) {
        console.error('Refund process failed:', error)
      }
    }

    // Adding/Removing items to/from refund
    function addToRefund (item, index) {
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
        state.totalRefund.baseFee += refundedItem.total
        state.totalRefund.serviceFee += refundedItem.serviceFees
        state.totalRefund.priorityFee += refundedItem.priorityFees
      })
    }

    // Compute if the finalize button should be disabled
    const isFinalizeDisabled = computed(() => {
      return state.refundComment.trim().length === 0 ||
        (!state.isFullRefund && state.totalRefund.baseFee === 0 && state.totalRefund.serviceFee === 0)
    })

    return {
      ...toRefs(state),
      fetchInvoice,
      processRefund,
      addToRefund,
      isFinalizeDisabled
    }
  }
})

</script>
