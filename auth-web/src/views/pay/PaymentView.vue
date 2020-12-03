<template>
  <div id="app">
    <v-container v-if="showLoading">
      <v-layout row flex-column justify-center align-center class="py-12">
        <v-progress-circular
          color="primary"
          :size="50"
          indeterminate
          class="mt-12"
        ></v-progress-circular>
        <div class="loading-msg">{{ $t('paymentPrepareMsg') }}</div>
      </v-layout>
    </v-container>
    <v-container v-if="errorMessage">
      <v-layout row justify-center align-center>
        <SbcSystemError
          v-on:continue-event="goToUrl(returnUrl)"
          v-if="showErrorModal"
          title="Payment Failed"
          primaryButtonTitle="Continue to Filing"
          :description="errorMessage">
        </SbcSystemError>
        <div class="loading-msg" v-else>{{errorMessage}}</div>
      </v-layout>
    </v-container>
    <v-container v-if="showOnlineBanking">
      <v-row class="pt-6">
        <v-col md="6" offset-md="3">
          <h1 class="mb-1">Make a payment</h1>
          <p class="pb-2">Please find your balance and payment details below </p>
          <v-card class="bcol-payment-card">
            <v-card-text class="heading-info">
              <h2 class="mb-2">Balance Due: $21.50</h2>
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
                    BC Registries and Online Services
                  </span>
                  <span>
                    <strong>Account #:</strong>
                    87548675
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
                    @click="downloadInvoice"
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
                      @click="payNow"
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
                      @click="makePayment"
                      depressed
                    >
                      Ok
                    </v-btn>
                  </template>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">

import { Component, Prop, Vue } from 'vue-property-decorator'
import OrgModule from '@/store/modules/org'
import PaymentServices from '@/services/payment.services'
import { PaymentTypes } from '@/util/constants'
import SbcSystemError from 'sbc-common-components/src/components/SbcSystemError.vue'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  components: {
    SbcSystemError
  },
  methods: {
    ...mapActions('org', [
      'createTransaction'
    ])
  }
})
export default class PaymentView extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  @Prop({ default: '' }) paymentId: string
  @Prop({ default: '' }) redirectUrl: string
  protected readonly createTransaction!: (transactionData) => any
  private showLoading: boolean = true
  private showOnlineBanking: boolean = true
  private errorMessage: string = ''
  private showErrorModal: boolean = false
  private returnUrl: string = ''
  private payWithCreditCard: boolean = false

  private async mounted () {
    this.showLoading = true
    if (!this.paymentId || !this.redirectUrl) {
      this.showLoading = false
      this.errorMessage = this.$t('payNoParams').toString()
      return
    }
    try {
      const transactionDetails = await this.createTransaction({
        paymentId: this.paymentId,
        redirectUrl: this.redirectUrl
      })
      this.showLoading = false
      this.returnUrl = transactionDetails?.paySystemUrl
      if (transactionDetails?.paymentType === PaymentTypes.ONLINE_BANKING) {
        this.showOnlineBanking = true
        // stay
      } else {
        this.goToUrl(this.returnUrl)
      }
    } catch (error) {
      this.showLoading = false
      this.errorMessage = this.$t('payFailedMessage').toString()
      if (error.response.data && error.response.data.type === 'INVALID_TRANSACTION') { // Transaction is already completed.Show as a modal.
        this.goToUrl(this.redirectUrl)
      } else {
        this.showErrorModal = true
      }
    }
  }

  goToUrl (url:string) {
    window.location.href = url || this.redirectUrl
  }

  downloadInvoice () {
    // DOWNLOAD INVOICE
  }

  makePayment () {
    // MAKE PAYMENT
  }

  payNow () {
    // PAY NOW
  }

  cancel () {
    // CANCEL
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.loading-msg {
  font-weight: 600;
  margin-top: 14px;
}
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
