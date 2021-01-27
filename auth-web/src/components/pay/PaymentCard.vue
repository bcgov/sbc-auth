<template>
  <v-card class="bcol-payment-card">
    <PayWithCreditCard v-if="payWithCreditCard"
    :totalBalanceDue="totalBalanceDue"
    :showPayWithOnlyCC="showPayWithOnlyCC"
    />

    <PayWithOnlineBanking
    :onlineBankingData="onlineBankingData"
    v-else />
    <v-card-text class="pt-0 pb-8 px-8">
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
          </div>
        </template>
      </v-checkbox>
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
import PayWithCreditCard from './PayWithCreditCard.vue'
import PayWithOnlineBanking from './PayWithOnlineBanking.vue'

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
  private totalBalanceDue = 0
  private cfsAccountId: string = ''
  private payeeName: string = ''
  private onlineBankingData: any = []

  private mounted () {
    this.totalBalanceDue = this.paymentCardData?.totalBalanceDue || 0
    this.payeeName = this.paymentCardData.payeeName
    this.cfsAccountId = this.paymentCardData?.cfsAccountId || ''
    this.payWithCreditCard = this.showPayWithOnlyCC

    // setting online data
    this.onlineBankingData = {
      totalBalanceDue: this.totalBalanceDue,
      payeeName: this.payeeName,
      cfsAccountId: this.cfsAccountId
    }
  }

  private cancel () {
    if (this.showPayWithOnlyCC) { // cancel will redirect back to page
      this.emitBtnClick('complete-online-banking')
    } else {
      this.payWithCreditCard = false
    }
  }

  private emitBtnClick (eventName) {
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
