<template>
  <v-card class="bcol-payment-card" data-test='div-bcol-payment-card'>
    <!-- wording for credit card payment -->
    <PayWithCreditCard v-if="payWithCreditCard"
    :totalBalanceDue="totalBalanceDue"
    :showPayWithOnlyCC="showPayWithOnlyCC"
    :partialCredit="partialCredit"
    />
    <!-- wording for online bank payment -->
    <PayWithOnlineBanking
    :onlineBankingData="onlineBankingData"
    v-else />

    <v-card-text class="pt-0 pb-8 px-8">
      <template v-if="!overCredit">
        <p v-if="showPayWithOnlyCC">Click <strong>"pay now"</strong> to complete transaction balance with credit card</p>
        <p v-else>Would you like to complete transaction immediately?</p>
        <v-checkbox
          class="pay-with-credit-card mb-4"
          v-model="payWithCreditCard"
          color="primary"
          hide-details
          :disabled="showPayWithOnlyCC"
        >
          <template v-slot:label>
            <div class="ml-1">
              <div class="font-weight-bold">Credit Card</div>
              <div class="subtitle-2 mt-1">Pay your balance and access files <strong>immediately</strong></div>
              <div class="subtitle-2" v-if="partialCredit">Account credit will <strong>not apply</strong> with credit card payment option.</div>
            </div>
          </template>
        </v-checkbox>
      </template>
      <v-divider class="mt-8"></v-divider>
      <v-row>
        <v-col
          cols="12"
          class="pt-8 pb-0 d-inline-flex"
        >
          <v-btn
            large
            text
            color="primary"
            class="px-0"
            @click="emitBtnClick('download-invoice')"
            v-if="!payWithCreditCard && !overCredit"
            data-test='btn-download-invoice'
          >
            <v-icon class="mr-1">
              mdi-file-download-outline
            </v-icon>
            Download Invoice
          </v-btn>
          <v-spacer></v-spacer>
          <template v-if="payWithCreditCard">
            <v-btn
              large
              color="primary"
              width="100"
              class="font-weight-bold"
              @click="emitBtnClick('pay-with-credit-card')"
            >
              Pay Now
            </v-btn>
            <v-btn
              large
              width="100"
              class="ml-3"
              @click="cancel"
              data-test='btn-cancel-online-banking'
            >
              Cancel
            </v-btn>
          </template>
          <template v-else>
            <v-btn
              large
              color="primary"
              width="100"
              class="font-weight-bold"
              @click="emitBtnClick('complete-online-banking')"
              data-test='btn-complete-online-banking'
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
import PayWithCreditCard from '@/components/pay/PayWithCreditCard.vue'
import PayWithOnlineBanking from '@/components/pay/PayWithOnlineBanking.vue'
import PaymentServices from '@/services/payment.services'

@Component({
  components: {
    PayWithCreditCard,
    PayWithOnlineBanking
  }

})
export default class PaymentCard extends Vue {
  @Prop() paymentCardData: any
  @Prop({ default: false }) showPayWithOnlyCC: boolean
  private payWithCreditCard: boolean = false
  private balanceDue = 0
  private totalBalanceDue = 0
  private cfsAccountId: string = ''
  private payeeName: string = ''
  private onlineBankingData: any = []
  private credit?: number = null
  private doHaveCredit:boolean = false
  private overCredit:boolean = false
  private partialCredit:boolean = false
  private creditBalance = 0
  private paymentId: string
  private totalPaid = 0

  private mounted () {
    this.totalBalanceDue = this.paymentCardData?.totalBalanceDue || 0
    this.totalPaid = this.paymentCardData?.totalPaid || 0
    this.balanceDue = this.totalBalanceDue - this.totalPaid
    this.payeeName = this.paymentCardData.payeeName
    this.cfsAccountId = this.paymentCardData?.cfsAccountId || ''
    this.payWithCreditCard = this.showPayWithOnlyCC
    this.credit = this.paymentCardData.credit
    this.doHaveCredit = this.paymentCardData.credit !== null && this.paymentCardData.credit !== 0
    if (this.doHaveCredit) {
      this.overCredit = this.credit >= this.totalBalanceDue
      this.partialCredit = this.credit < this.totalBalanceDue
      this.balanceDue = this.overCredit ? this.balanceDue : this.balanceDue - this.credit
    }
    this.creditBalance = this.overCredit ? this.credit - this.balanceDue : 0
    this.paymentId = this.paymentCardData.paymentId

    // setting online data
    this.onlineBankingData = {
      totalBalanceDue: this.balanceDue,
      payeeName: this.payeeName,
      cfsAccountId: this.cfsAccountId,
      overCredit: this.overCredit,
      partialCredit: this.partialCredit,
      creditBalance: this.creditBalance,
      credit: this.credit
    }
  }

  private cancel () {
    if (this.showPayWithOnlyCC) { // cancel will redirect back to page
      this.emitBtnClick('complete-online-banking')
    } else {
      this.payWithCreditCard = false
    }
  }

  private async emitBtnClick (eventName) {
    if (eventName === 'complete-online-banking' && this.doHaveCredit) {
      await PaymentServices.applycredit(this.paymentId)
    }
    this.$emit(eventName)
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
