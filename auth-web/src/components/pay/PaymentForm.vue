<template>
    <div id="app">
        <v-app>
            <v-container fill-height>
                <v-layout row justify-center align-center>
                    <v-progress-circular color="primary" :size="50" indeterminate v-if="!errorMessage"></v-progress-circular>
                    <div class="loading-msg" v-if="!errorMessage"> {{ $t('paymentPrepareMsg') }}</div>
                    <div class="loading-msg" v-if="errorMessage && !showErrorModal">{{errorMessage}}</div>
                    <sbc-system-error v-on:continue-event="goToReturnUrl()" :showModal=showErrorModal title="Payment Failed" primaryButtonTitle="Continue to Filing" :description="errorHeading" ></sbc-system-error>
                </v-layout>
            </v-container>
        </v-app>
    </div>
</template>

<script lang="ts">

import { Vue, Component, Prop } from 'vue-property-decorator'
import PaymentServices from '@/services/payment.services'
import SbcSystemError from 'sbc-common-components/src/components/SbcSystemError.vue'

@Component({
  components: {
    SbcSystemError
  }
})
export default class PaymentForm extends Vue {
    @Prop() paymentId: string
    @Prop() redirectUrl: string
    errorMessage:string = ''
    showErrorModal:boolean
    returnUrl:string

    mounted () {
      if (!this.paymentId || !this.redirectUrl) {
        this.errorMessage = this.$t('payNoParams').toString()
        return
      }
      PaymentServices.createTransaction(this.paymentId, encodeURIComponent(this.redirectUrl))
        .then(response => {
          this.returnUrl = response.data.pay_system_url
          this.goToReturnUrl()
        })
        .catch(response => {
          if (response.data.code === 'PAY006') { // Transaction is already completed
            this.showErrorModal = true
            this.errorMessage = this.$t('payFailedMessage').toString()
          } else {
            this.errorMessage = this.$t('payFailedMessage').toString()
            this.showErrorModal = false
          }
        })
    }
    goToReturnUrl () {
      window.location.href = this.returnUrl
    }
}
</script>

<style scoped>

</style>
