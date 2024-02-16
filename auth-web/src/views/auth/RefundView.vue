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
            <th>Base Fee</th>
            <th>Service Fees</th>
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
            <td>{{ item.total - item.serviceFees }}</td>
            <td>{{ item.serviceFees }}</td>
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
      Refund total:
      <div>Base Fee: ${{ totalRefund.baseFee.toFixed(2) }}</div>
      <div>Service Fee: ${{ totalRefund.serviceFee.toFixed(2) }}</div>
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
import { Refund, refundRevenueType } from '@/models/refund'
import { computed, defineComponent, reactive, ref } from '@vue/composition-api'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'PaymentRefund',
  setup () {
    const invoiceId = ref('')
    const paymentLineItems = ref([])
    const isFullRefund = ref(false)
    const isPartialRefund = ref(true)
    const refundedItems = ref([])
    const orgStore = useOrgStore()
    const refundComment = ref('')
    const totalRefund = reactive({
      baseFee: 0,
      serviceFee: 0
    })

    const fetchInvoice = async () => {
      const invoice: any = await orgStore.getInvoice({ invoiceId: invoiceId.value })
      if (invoice.lineItems) {
        paymentLineItems.value = invoice.lineItems.map(item => ({
          ...item
        }))
      }
    }

    const processRefund = async () => {
      try {
        let refundRevenue: refundRevenueType[] = []

        refundedItems.value.forEach(index => {
          const item = paymentLineItems.value[index]
          const baseFee = item.total - item.serviceFees

          if (baseFee > 0) {
            refundRevenue.push({
              paymentLineItemId: item.id,
              refundAmount: baseFee,
              refundType: 'OTHER_FEES' // For baseFee
            })
          }

          if (item.serviceFees > 0) {
            refundRevenue.push({
              paymentLineItemId: item.id,
              refundAmount: item.serviceFees,
              refundType: 'SERVICE_FEE'
            })
          }
        })

        const refundPayload: Refund = {
          reason: refundComment.value,
          refundRevenue: refundRevenue
        }

        const response = await orgStore.refundInvoice(invoiceId.value, refundPayload)
        console.log('Refund successful:', refundPayload, response)
      } catch (error) {
        console.error('Refund process failed:', error)
      }
    }

    const addToRefund = (item, index) => {
      const isRefunded = refundedItems.value.includes(index)
      if (!isRefunded) {
        // Add to refund
        totalRefund.baseFee += item.total - item.serviceFees
        totalRefund.serviceFee += item.serviceFees
        refundedItems.value.push(index) // Mark item as refunded
      } else {
        // Remove from refund
        totalRefund.baseFee -= item.total - item.serviceFees
        totalRefund.serviceFee -= item.serviceFees
        const itemIndex = refundedItems.value.indexOf(index)
        refundedItems.value.splice(itemIndex, 1) // Unmark item as refunded
      }
    }

    const isFinalizeDisabled = computed(() => {
      return refundComment.value.trim().length === 0 ||
        (totalRefund.baseFee === 0 && totalRefund.serviceFee === 0)
    })

    return {
      invoiceId,
      paymentLineItems,
      fetchInvoice,
      processRefund,
      totalRefund,
      addToRefund,
      isFullRefund,
      refundedItems,
      isPartialRefund,
      refundComment,
      isFinalizeDisabled
    }
  }
})
</script>
