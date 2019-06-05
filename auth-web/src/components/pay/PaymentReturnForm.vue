<template>
    <div id="app">
        <v-app>
            <v-container fill-height>
                <v-layout row justify-center align-center>
                    <v-progress-circular color="primary" :size="50" indeterminate v-if="!errorMessage"></v-progress-circular>
                    <div class="loading-msg" v-if="!errorMessage">Preparing your payments</div>
                    <div class="loading-msg" v-if="errorMessage">{{errorMessage}}</div>
                </v-layout>
            </v-container>
        </v-app>
    </div>
</template>

<script  lang="ts">

import PaymentServices from '@/services/payment.services'
export default {
  name: 'PaymentReturnForm',

  props: {
    paymentId: String,
    transactionId: String,
    receiptNum: String
  },
  data () {
    return {
      errorMessage: ''
    }
  },
  mounted () {
    console.log('%c PaymentForm-Data Recieved on Mount as %s', 'color: blue ;font-size : 12px', this.receiptNum)

    if (this.paymentId && this.transactionId) {
      PaymentServices.updateTransaction(this.paymentId, this.transactionId, this.receiptNum)
        .then(response => {
          window.location.href = response.data.client_system_url
        })
        .catch(response => {
          this.errorMessage = this.$t('payFailedMessage')
        })
    } else {
      this.errorMessage = this.$t('payNoParams')
    }
  }
}
</script>

<style scoped>

</style>
