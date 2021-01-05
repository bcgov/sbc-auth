<template>
  <v-card class="bcol-payment-card">
    <v-card-text class="heading-info">
      <h2 class="mb-2">Balance Due: ${{totalBalanceDue.toFixed(2)}}</h2>
      <template v-if="payWithCreditCard">
        <p class="mb-1">
          Click "pay now" to complete transaction balance with credit card.
          By credit card, your transaction will be completed <strong>immediately</strong>.
        </p>
      </template>
      <template v-else>
        <p class="mb-6">
          Transaction will be completed when payment is received in full.
          Online Banking payment methods can expect between <strong>2-5 days</strong> for your payment.
        </p>
        <div class="mb-1">
          <span class="payee-name">
            <strong>Payee Name:</strong>
            {{payeeName}}
          </span>
          <span>
            <strong>Account #:</strong>
            {{cfsAccountId}}
          </span>
        </div>
      </template>
    </v-card-text>
    <v-card-text>
      <template v-if="payWithCreditCard">
        <h4 class="mb-3">How to pay with credit card:</h4>
        <ol class="mb-5">
          <li>Click on "Proceed"</li>
          <li>Complete credit card payment</li>
          <li>Get confirmation receipt</li>
        </ol>
      </template>
      <template v-else>
        <h4 class="mb-3">How to pay with online banking:</h4>
        <ol class="mb-5">
          <li>Sign in to your financial institution's online banking website or app</li>
          <li>Go to your financial institution's bill payment page</li>
          <li>Enter "BC Registries and Online Services" as payee</li>
          <li>Enter BC Registries and Online Services account number</li>
          <li>Submit your payment for the balance due</li>
        </ol>
      </template>
      <v-divider></v-divider>
      <h4 class="mt-5 mb-4">Would you like to complete transaction immediately?</h4>
      <v-checkbox
        class="pay-with-credit-card mb-4"
        v-model="payWithCreditCard"
        color="primary"
      >
        <template v-slot:label>
          <div class="font-weight-bold ml-1">Credit Card</div>
          <div class="subtxt ml-1">Pay your balance and access files <strong>immediately</strong></div>
        </template>
      </v-checkbox>
      <v-divider></v-divider>
      <v-row>
        <v-col
          cols="12"
          class="pb-2 d-inline-flex"
        >
          <v-btn
            class="px-0"
            text
            color="primary"
            @click="emitBtnClick('download-invoice')"
            v-if="!payWithCreditCard"
          >
            <v-icon class="mr-1">
              mdi-file-download-outline
            </v-icon>
            Download Invoice
          </v-btn>
          <v-spacer></v-spacer>
          <template v-if="payWithCreditCard">
            <v-btn
              color="grey lighten-2"
              width="100"
              class="mr-3"
              @click="cancel"
              depressed
            >
              Cancel
            </v-btn>
            <v-btn
              color="primary"
              width="100"
              class="font-weight-bold"
              @click="emitBtnClick('pay-with-credit-card')"
              depressed
            >
              Pay Now
            </v-btn>
          </template>
          <template v-else>
            <v-btn
              color="primary"
              width="100"
              class="font-weight-bold"
              @click="emitBtnClick('complete-online-banking')"
              depressed
            >
              Ok
            </v-btn>
          </template>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">

import { Component, Emit, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class PaymentCard extends Vue {
  @Prop() paymentCardData: any
  private payWithCreditCard: boolean = false
  private totalBalanceDue = 0
  private cfsAccountId: string = ''
  private payeeName: string = ''

  private mounted () {
    this.totalBalanceDue = this.paymentCardData?.totalBalanceDue || 0
    this.payeeName = this.paymentCardData.payeeName
    this.cfsAccountId = this.paymentCardData?.cfsAccountId || ''
  }

  private cancel () {
    this.payWithCreditCard = false
  }

  private emitBtnClick (eventName) {
    this.$emit(eventName)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.bcol-payment-card {
  .v-card__text {
    padding: 16px 24px;
    font-size: 0.95rem;
  }
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
          font-size: .85rem;
          margin-top: 6px;
        }
      }
    }
  }
}
</style>
