<template>
  <v-card elevation="0">
    <v-card-text class="heading-info py-7 px-8">
      <h2 class="mb-2">
        Original Amount: <span class="ml-2">${{ originalAmount.toFixed(2) }}</span><br>
        Balance Due: <span class="ml-2">${{ totalBalanceDue.toFixed(2) }}</span>
      </h2>
      <template v-if="overCredit">
        <p class="mb-6">
          Transaction will be completed with your account credit.<br>
          You now have <strong>${{ creditBalance.toFixed(2) }} remaining credit</strong> in your account.
        </p>
      </template>
      <template v-else-if="partialCredit">
        <p class="mb-6">
          Payment is partially covered with your account credit: ${{ credit }}<br>
          You now have <strong>${{ creditBalance.toFixed(2) }} remaining credit</strong> in your account.
        </p>
      </template>
      <template v-else>
        <p class="mb-6">
          Transaction will be completed when payment is received in full.
          Online Banking payment methods can expect between <strong>2-5 days</strong> for your payment.
        </p>
      </template>
      <div
        v-if="!overCredit"
        class="mb-1"
      >
        <span class="payee-name">
          <strong>Payee Name:</strong>
          {{ payeeName }}
        </span>
        <span>
          <strong>Payment Identifier:</strong>
          {{ cfsAccountId }}
        </span>
      </div>
    </v-card-text>
    <v-card-text
      v-if="!overCredit"
      class="pt-7 pb-0 px-8"
    >
      <h3 class="mb-3">
        How to pay with online banking:
      </h3>
      <ol class="mb-5">
        <li>Sign in to your financial institution's online banking website or app</li>
        <li>Go to your financial institution's bill payment page</li>
        <li>Enter <b>"BC Registries"</b> as payee</li>
        <li>Enter this payment identifier as your account number: <b>{{ cfsAccountId }}</b></li>
        <li>Submit your payment for the balance due</li>
      </ol>
      <v-divider class="my-6" />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'

export default defineComponent({
  name: 'PayWithOnlineBanking',
  props: {
    onlineBankingData: {
      type: Object,
      required: true
    },
    showPayWithOnlyCC: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const state = reactive({
      payWithCreditCard: false,
      totalBalanceDue: 0,
      cfsAccountId: '',
      payeeName: '',
      overCredit: false,
      creditBalance: 0,
      partialCredit: false,
      credit: 0,
      originalAmount: 0
    })

    const updateOnlineBankingData = () => {
      state.totalBalanceDue = props.onlineBankingData?.totalBalanceDue || 0
      state.payeeName = props.onlineBankingData?.payeeName
      state.cfsAccountId = props.onlineBankingData?.cfsAccountId || ''
      state.overCredit = props.onlineBankingData?.overCredit || false
      state.partialCredit = props.onlineBankingData?.partialCredit || false
      state.creditBalance = props.onlineBankingData?.creditBalance || 0
      state.credit = props.onlineBankingData?.obCredit || 0
      state.originalAmount = props.onlineBankingData?.originalAmount || 0
    }

    watch(() => props.onlineBankingData, updateOnlineBankingData, { deep: true })

    onMounted(() => {
      updateOnlineBankingData()
    })

    return {
      ...toRefs(state)
    }
  }
})
</script>

<style lang="scss" scoped>
.bcol-payment-card {
  .heading-info {
    background: var(--v-primary-base);
    color: #fff !important;
    h2 {
      color: #fff !important;
    }
    .payee-name {
      padding-right: 16px;
      margin-right: 16px;
      border-right: 1px solid white;
    }
  }
  ol {
    li {
      margin-bottom: 4px;
    }
  }
  .pay-with-credit-card {
    ::v-deep {
      .v-input__slot {
        align-items: flex-start;
      }
      .v-label {
        display: block;
        color: #000;
        .subtxt {
          font-size: .875rem;
          margin-top: 6px;
        }
      }
    }
  }
}
</style>
