<template>
  <div data-test="div-payment-view">
    <v-container v-if="showLoading" data-test="div-payment-view-loading">
      <v-layout row flex-column justify-center align-center class="py-12 loading-progressbar">
        <v-progress-circular
          color="primary"
          :size="80"
          :width="5"
          indeterminate
          class="mt-12"
        ></v-progress-circular>
        <div class="loading-msg">{{ showdownloadLoading ? $t('paymentDownloadMsg')  : $t('paymentPrepareMsg') }}</div>
      </v-layout>
    </v-container>
    <div v-else>
      <v-container v-if="errorMessage" data-test="div-payment-view-error">
        <v-layout row justify-center align-center>
          <SbcSystemError
            v-on:continue-event="goToUrl(returnUrl)"
            v-if="showErrorModal"
            title="Payment Failed"
            primaryButtonTitle="Continue to Filing"
            :description="errorMessage">
          </SbcSystemError>
          <div class="mt-12" v-else>
            <div class="text-center mb-4">
              <v-icon color="error" size="30">mdi-alert-outline</v-icon>
            </div>
            <h4>{{errorMessage}}</h4>
          </div>
        </v-layout>
      </v-container>
      <v-container
        data-test="div-payment-view-container"
        class="view-container"
        v-if="showOnlineBanking">
        <div class="payment-view-content">
          <h1 class="mb-1">Make a payment</h1>
          <p class="mb-8">Please find your balance and payment details below.</p>
          <PaymentCard
            :paymentCardData="paymentCardData"
            @complete-online-banking="completeOBPayment"
            @pay-with-credit-card="payNow"
            @download-invoice="downloadInvoice"
            :showPayWithOnlyCC="showPayWithOnlyCC"
          ></PaymentCard>
        </div>
      </v-container>
    </div>
  </div>
</template>

<script lang="ts">

import { Component, Prop, Vue } from 'vue-property-decorator'
import { PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { Invoice } from '@/models/invoice'
import OrgModule from '@/store/modules/org'
import { OrgPaymentDetails } from '@/models/Organization'
import PaymentCard from '@/components/pay/PaymentCard.vue'
import SbcSystemError from 'sbc-common-components/src/components/SbcSystemError.vue'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  components: {
    SbcSystemError,
    PaymentCard
  },
  methods: {
    ...mapActions('org', [
      'createTransaction',
      'getOrgPayments',
      'getInvoice',
      'updateInvoicePaymentMethodAsCreditCard',
      'downloadOBInvoice'
    ])
  }
})
export default class PaymentView extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  @Prop({ default: '' }) paymentId: string
  @Prop({ default: '' }) redirectUrl: string
  private readonly createTransaction!: (transactionData) => any
  private readonly updateInvoicePaymentMethodAsCreditCard!: (invoicePayload) => any
  private readonly downloadOBInvoice!: (paymentId: string) => any
  private readonly getOrgPayments!: (orgId: number) => OrgPaymentDetails
  private readonly getInvoice!: (invoicePayload) => Invoice
  private showLoading: boolean = true
  private showdownloadLoading: boolean = false
  private showOnlineBanking: boolean = false
  private errorMessage: string = ''
  private showErrorModal: boolean = false
  private returnUrl: string = ''
  private paymentCardData: any
  private showPayWithOnlyCC: boolean = false

  private async mounted () {
    this.showLoading = true
    if (!this.paymentId || !this.redirectUrl) {
      this.showLoading = false
      this.errorMessage = this.$t('payNoParams').toString()
      return
    }
    try {
      const accountSettings = this.getAccountFromSession()
      // user should be signed in and should have account as well
      if (this.isUserSignedIn && !!accountSettings) {
        // get the invoice and check for OB
        try {
          const invoice: Invoice = await this.getInvoice({ invoiceId: this.paymentId, accountId: accountSettings?.id })
          if (invoice?.paymentMethod === PaymentTypes.ONLINE_BANKING) {
            // get account data to show in the UI
            const paymentDetails: OrgPaymentDetails = await this.getOrgPayments(accountSettings?.id)
            this.paymentCardData = {
              totalBalanceDue: invoice?.total || 0, // to fix credit amount
              payeeName: ConfigHelper.getPaymentPayeeName(),
              cfsAccountId: paymentDetails?.cfsAccount?.cfsAccountNumber || '',
              credit: paymentDetails?.credit,
              paymentId: this.paymentId,
              totalPaid: invoice?.paid || 0
            }

            this.showLoading = false
            this.showOnlineBanking = true
            this.showPayWithOnlyCC = !invoice?.isOnlineBankingAllowed // if isOnlineBankingAllowed is true, allowed show CC as only payment type
          }
        } catch (error) {
          // eslint-disable-next-line no-console
          console.error('error in accessing the invoice.Defaulting to CC flow')
        }
      }

      if (!this.showOnlineBanking) {
        await this.doCreateTransaction()
      }
    } catch (error) {
      this.doHandleError(error)
    }
  }

  // We need this, otherwise we can get redirect Urls with just a single slash.
  get redirectUrlFixed () {
    if (!this.redirectUrl.includes('://')) {
      return this.redirectUrl.replace(':/', '://')
    }
    return this.redirectUrl
  }

  private isUserSignedIn (): boolean {
    return !!ConfigHelper.getFromSession('KEYCLOAK_TOKEN')
  }

  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }

  private goToUrl (url:string) {
    window.location.href = url || this.redirectUrlFixed
  }

  private completeOBPayment () {
    this.goToUrl(this.returnUrl)
  }

  private async payNow () {
    // patch the transaction
    // redirect for payment
    try {
      const accountSettings = this.getAccountFromSession()
      await this.updateInvoicePaymentMethodAsCreditCard({ paymentId: this.paymentId, accountId: accountSettings?.id })
      await this.doCreateTransaction()
    } catch (error) {
      this.doHandleError(error)
    }
  }

  private async downloadInvoice () {
    // download invoice fot online banking
    this.showLoading = true // to avoid rapid download clicks
    this.showdownloadLoading = true // to avoid rapid download clicks
    this.errorMessage = ''
    try {
      const downloadType = 'application/pdf'

      const response = await this.downloadOBInvoice(this.paymentId)
      const contentDispArr = response?.headers['content-disposition'].split('=')

      const fileName = (contentDispArr.length && contentDispArr[1]) ? contentDispArr[1] : `bcregistry-${this.paymentId}`
      CommonUtils.fileDownload(response.data, fileName, downloadType)
      this.showdownloadLoading = false
      this.showLoading = false
    } catch (error) {
      this.showdownloadLoading = false
      this.showLoading = false
      this.errorMessage = this.$t('downloadFailedMessage').toString()
      // this.showErrorModal = true
    }
  }

  private async doCreateTransaction () {
    const transactionDetails = await this.createTransaction({
      paymentId: this.paymentId,
      redirectUrl: this.redirectUrlFixed
    })
    this.showLoading = false
    this.returnUrl = transactionDetails?.paySystemUrl
    this.goToUrl(this.returnUrl)
  }

  private doHandleError (error) {
    this.showLoading = false
    this.errorMessage = this.$t('payFailedMessage').toString()
    if (error.response.data && error.response.data.type === 'INVALID_TRANSACTION') { // Transaction is already completed.Show as a modal.
      this.goToUrl(this.redirectUrlFixed)
    } else {
      this.showErrorModal = true
    }
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.payment-view-content {
  margin: 0 auto;
  max-width: 48rem;
}

.loading-msg {
  font-weight: 600;
  margin-top: 14px;
}

</style>
