<template>
  <v-card elevation="0">
    <v-card-text class="heading-info py-7 px-8">
      <h2 class="mb-2">
        Balance Due: <span class="ml-2">${{ totalBalanceDue.toFixed(2) }}</span>
      </h2>
      <p
        v-if="showPayWithOnlyCC"
        class="mb-1"
      >
        <strong>Credit card is the only payment option for this transaction</strong>.<br>
        Online Banking is not available for this transaction.
      </p>
      <p
        v-if="partialCredit"
        class="mb-1"
      >
        You can't <strong>use your account credit</strong> with credit card payment.<br>
        <strong>Full amount</strong> will be charged if you pay by credit card.
      </p>
      <p
        v-else
        class="mb-1"
      >
        Click "pay now" to complete transaction balance with credit card.
        By credit card, your transaction will be completed <strong>immediately</strong>.
      </p>
    </v-card-text>
    <v-card-text class="pt-7 pb-0 px-8">
      <h3 class="body-1 font-weight-bold mb-3">
        How to pay with credit card:
      </h3>
      <ol class="mb-5">
        <li>Click on "Pay Now"</li>
        <li>Complete credit card payment</li>
        <li>Get confirmation receipt</li>
      </ol>
      <v-divider class="my-6" />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'PayWithCreditCard',
  props: {
    showPayWithOnlyCC: {
      type: Boolean,
      default: false
    },
    totalBalanceDue: {
      type: Number,
      default: 0
    },
    partialCredit: {
      type: Boolean,
      default: false
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

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
