<template>
  <div id="app">
    <v-container>
      <v-layout row justify-center align-center>
        <v-progress-circular color="primary" :size="50" indeterminate v-if="!errorMessage"></v-progress-circular>
        <div class="loading-msg" v-if="!errorMessage"> {{ $t('paymentPrepareMsg') }}</div>
        <div class="loading-msg" v-if="errorMessage && !showErrorModal">{{ errorMessage }}</div>
        <sbc-system-error v-on:continue-event="goToUrl(returnUrl)" v-if="showErrorModal && errorMessage"
                          title="Payment Failed" primaryButtonTitle="Continue to Account Page"
                          :description="errorMessage"></sbc-system-error>
      </v-layout>
    </v-container>
  </div>
</template>

<script lang="ts">

import { Component, Prop, Vue } from 'vue-property-decorator'
import PaymentServices from '@/services/payment.services'
import SbcSystemError from 'sbc-common-components/src/components/SbcSystemError.vue'

@Component({
  components: {
    SbcSystemError
  }
})
export default class CcPaymentView extends Vue {
  @Prop() paymentId: string
  @Prop() redirectUrl: string
  errorMessage: string = ''
  showErrorModal: boolean = false
  returnUrl: string

  mounted () {
    if (!this.paymentId || !this.redirectUrlFixed) {
      this.errorMessage = this.$t('payNoParams').toString()
      return
    }
    PaymentServices.createTransactionForPadPayment(this.paymentId, this.redirectUrlFixed)
      .then(response => {
        this.returnUrl = response.data.paySystemUrl
        this.goToUrl(this.returnUrl)
      })
      .catch(error => {
        this.errorMessage = this.$t('payFailedMessage').toString()
        if (error.response.data && error.response.data.type === 'INVALID_TRANSACTION') { // Transaction is already completed.Show as a modal.
          this.goToUrl(this.redirectUrlFixed)
        } else {
          this.showErrorModal = true
        }
      })
  }

  // We need this, otherwise we can get redirect Urls with just a single slash.
  get redirectUrlFixed () {
    return this.redirectUrl?.replace(':/', '://')
  }

  goToUrl (url: string) {
    window.location.href = url || this.redirectUrlFixed
  }
}
</script>

<style lang="scss" scoped>

</style>
