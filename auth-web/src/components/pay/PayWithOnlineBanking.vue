<template>
  <v-card elevation="0">
    <v-card-text class="heading-info py-7 px-8">
      <h2 class="mb-2">Balance Due: <span class="ml-2">{{overCredit ? '-': ''}}${{totalBalanceDue.toFixed(2)}}</span></h2>
      <template v-if="overCredit">
        <p class="mb-6">
          Transaction will be completed with your account credit.<br />
          You now have <strong>${{creditBalance.toFixed(2)}} remaining credit</strong> in your account.
        </p>
      </template>
      <template v-else-if="partialCredit">
        <p class="mb-6">
          Payment is partially covered with your account credit: ${{credit}}<br />
          You now have <strong>${{creditBalance.toFixed(2)}} remaining credit</strong> in your account.
        </p>
      </template>
      <template v-else>
        <p class="mb-6">
          Transaction will be completed when payment is received in full.
          Online Banking payment methods can expect between <strong>2-5 days</strong> for your payment.
        </p>
        </template>
        <template>
        <div class="mb-1" v-if="!overCredit">
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
    <v-card-text class="pt-7 pb-0 px-8" v-if="!overCredit">
      <template>
        <h3 class="mb-3">How to pay with online banking:</h3>
        <ol class="mb-5">
          <li>Sign in to your financial institution's online banking website or app</li>
          <li>Go to your financial institution's bill payment page</li>
          <li>Enter "BC Registries and Online Services" as payee</li>
          <li>Enter BC Registries and Online Services account number</li>
          <li>Submit your payment for the balance due</li>
        </ol>
      </template>
      <v-divider class="my-6"></v-divider>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">

import Vue from 'vue'
import { Component, Prop, Watch } from 'vue-property-decorator'

@Component
export default class PayWithOnlineBanking extends Vue {
  @Prop() onlineBankingData: any
  @Prop({ default: false }) showPayWithOnlyCC: boolean
  private payWithCreditCard: boolean = false
  private totalBalanceDue = 0
  private cfsAccountId: string = ''
  private payeeName: string = ''
  private overCredit:boolean = false
  private creditBalance = 0
  private partialCredit:boolean = false
  private credit = 0

  @Watch('onlineBankingData', { deep: true })
  async updateonlineBankingData (val, oldVal) {
    this.setData()
  }

  private setData () {
    this.totalBalanceDue = this.onlineBankingData?.totalBalanceDue || 0
    this.payeeName = this.onlineBankingData?.payeeName
    this.cfsAccountId = this.onlineBankingData?.cfsAccountId || ''
    this.overCredit = this.onlineBankingData?.overCredit || false
    this.partialCredit = this.onlineBankingData?.partialCredit || false
    this.creditBalance = this.onlineBankingData?.creditBalance || 0
    this.credit = this.onlineBankingData?.credit || 0
  }

  private mounted () {
    this.setData()
  }
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
