<template>
  <v-app>
    <v-container>
      <h2 class="mb-4">
        MVP Refunds
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
          value="full"
        />
        <v-radio
          label="Partial Refund"
          value="partial"
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
            <th v-if="refundType === 'partial'">
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
                :disabled="refundType === 'full'"
                dense
                hide-details="auto"
              />
            </td>

            <td>
              <v-text-field
                v-model.number="item.priorityFees"
                type="number"
                :disabled="refundType === 'full'"
                dense
                hide-details="auto"
              />
            </td>
            <td>
              <v-text-field
                v-model.number="item.futureEffectiveFees"
                type="number"
                :disabled="refundType === 'full'"
                dense
                hide-details="auto"
              />
            </td>
            <td>
              <v-text-field
                v-model.number="item.serviceFees"
                type="number"
                :disabled="refundType === 'full'"
                dense
                hide-details="auto"
              />
            </td>
            <td v-if="refundType === 'partial'">
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

      <div v-if="totalRefund.baseFee">
        Base Fee from: ${{ paymentLineItems[0].filingFees.toFixed(2) }} -> ${{ totalRefund.baseFee.toFixed(2) }}
      </div>
      <div v-if="totalRefund.serviceFee">
        Service Fee from: ${{ totalRefund.serviceFee.toFixed(2) }} -> ${{ totalRefund.serviceFee.toFixed(2) }}
      </div>
      <div
        v-if="refundType === 'full' && paymentLineItems.length > 0"
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
        v-if="refundRequestResponse"
        class="mt-4"
        border="left"
        dense
        outlined
        prominent
        shaped
        text
        :type="refundRequestResponse.includes('success') ? 'success' : 'error'"
      >
        {{ refundRequestResponse }}
      </v-alert>
    </v-container>
  </v-app>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { Invoice } from '@/models/invoice'
import { useOrgStore } from '@/stores/org'

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
      refundType: 'partial',
      refundRequestResponse: ''
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

        if (state.refundType === 'partial') {
          state.refundedItems.forEach(index => {
            const item = state.paymentLineItems[index]
            if (item.total > 0) {
              refundPayload.refundRevenue.push({
                paymentLineItemId: item.id,
                refundAmount: parseFloat(item.total),
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
          })
        } else {
          delete refundPayload.refundRevenue
        }

        const response = await state.orgStore.refundInvoice(state.invoiceId, refundPayload)
        state.refundRequestResponse = 'Refund successful.'
        console.log('Refund successful:', response)
      } catch (error) {
        state.refundRequestResponse = 'Refund failed.'
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
        (state.refundType === 'partial' && state.totalRefund.baseFee === 0 && state.totalRefund.serviceFee === 0)
    })

    watch(() => state.invoiceId, () => {
      state.refundRequestResponse = ''
    })

    return {
      ...toRefs(state),
      fetchInvoice,
      processRefund,
      changeRefundPayload,
      isFinalizeDisabled
    }
  }
})

</script>
