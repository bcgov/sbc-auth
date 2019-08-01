<template>
    <div id="app">
        <v-app>
            <v-container fill-height>
                <v-layout row justify-center align-center>
                    <v-progress-circular color="primary" :size="50" indeterminate v-if="!errorMessage"></v-progress-circular>
                    <div class="loading-msg" v-if="!errorMessage"> {{ $t('paymentPrepareMsg') }}</div>
                    <div class="loading-msg" v-if="errorMessage">{{errorMessage}}</div>
                </v-layout>
            </v-container>
        </v-app>
    </div>
</template>

<script lang="ts">

import PaymentServices from '@/services/payment.services'
export default {
  name: 'PaymentForm',

  props: {
    paymentId: String,
    redirectUrl: String
  },
  data () {
    return {
      errorMessage: ''
    }
  },

  mounted () {
    if (this.paymentId && this.redirectUrl) {
      PaymentServices.createTransaction(this.paymentId, encodeURIComponent(this.redirectUrl))
        .then(response => {
          window.location.href = response.data.pay_system_url
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
