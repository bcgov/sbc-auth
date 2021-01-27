<template>
  <v-card elevation="0">
    <v-card-text class="heading-info py-7 px-8">
      <h2 class="mb-2">Balance Due: <span class="ml-2">${{totalBalanceDue.toFixed(2)}}</span></h2>
      <template>
        <p class="mb-1" v-if="showPayWithOnlyCC">
          <strong>Credit card will be the only payment option for this transaction</strong>.<br />
          Online banking payment option is not available.
        </p>
        <p class="mb-1" v-else>
          Click "pay now" to complete transaction balance with credit card.
          By credit card, your transaction will be completed <strong>immediately</strong>.
        </p>
      </template>

    </v-card-text>
    <v-card-text class="pt-7 pb-0 px-8">
      <template>
        <h3 class="body-1 font-weight-bold mb-3">How to pay with credit card:</h3>
        <ol class="mb-5">
          <li>Click on "Pay Now"</li>
          <li>Complete credit card payment</li>
          <li>Get confirmation receipt</li>
        </ol>
      </template>
      <v-divider class="my-6"></v-divider>
      </v-card-text>
  </v-card>
</template>

<script lang="ts">

import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class PayWithCreditCard extends Vue {
  @Prop() paymentCardData: any
  @Prop({ default: false }) showPayWithOnlyCC: boolean
  @Prop({ default: 0 }) totalBalanceDue: number
}
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
      border-right: 1px solid #fff;
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
