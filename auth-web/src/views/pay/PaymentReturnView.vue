<template>
  <div id="app">
    <v-container>
      <v-row
        justify="center"
        align="center"
      >
        <v-row
          v-if="isLoading"
          justify="center"
          align="center"
          class="loading-progressbar"
        >
          <v-progress-circular
            color="primary"
            :size="100"
            :width="8"
            indeterminate
          />
          <div class="mt-6 font-italic font-weight-bold">
            Processing your payment ...
          </div>
        </v-row>
        <PaymentErrorMessage
          v-else
          :errorType="errorType"
          :tryAgainURL="tryAgainURL"
          :backUrl="backUrl"
        />
      </v-row>
    </v-container>
  </div>
</template>

<script  lang="ts">

import { Component, Prop, Vue } from 'vue-property-decorator'
import PaymentErrorMessage from '@/components/pay/common/PaymentErrorMessage.vue'
import PaymentServices from '@/services/payment.services'
import { paymentErrorType } from '@/util/constants'

@Component({
  components: {
    PaymentErrorMessage
  }
})
export default class PaymentReturnView extends Vue {
        @Prop() paymentId: string
        @Prop() transactionId: string
        @Prop() payResponseUrl: string
        returnUrl:string = ''
        isLoading:boolean = true
        errorType :string = paymentErrorType.GENERIC_ERROR // 'GENERIC_ERROR'
        backUrl:string = ''
        tryAgainURL:string = ''

        mounted () {
          if (!this.paymentId || !this.transactionId) {
            // this.errorMessage = this.$t('payNoParams').toString()
            this.errorType = paymentErrorType.GENERIC_ERROR
            this.backUrl = this.returnUrl // add URL here
            this.tryAgainURL = `/makepayment/${this.paymentId}/${encodeURIComponent(this.returnUrl)}` // add base url
            return
          }
          this.isLoading = true
          PaymentServices.updateTransaction(this.paymentId, this.transactionId, this.payResponseUrl)
            .then(response => {
              this.returnUrl = response.data.clientSystemUrl // encoding url
              const appendType = this.appendURLtype(this.returnUrl)
              const statusCode = response.data.statusCode
              const paySystemReasonCode = response.data.paySystemReasonCode
              if (statusCode === 'COMPLETED') {
                const status = btoa('COMPLETED') // convert to base 64
                // all good..go back
                this.goToUrl(`${this.returnUrl}${appendType}status=${status}`) // append success status
              } else {
                this.isLoading = false
                const status = btoa(paySystemReasonCode) // convert to base 64
                this.errorType = paySystemReasonCode
                this.backUrl = `${this.returnUrl}${appendType}status=${status}`
                this.tryAgainURL = `/makepayment/${this.paymentId}/${encodeURIComponent(this.returnUrl)}`
              }
            })
            .catch(() => {
              const status = btoa('FAILED') // convert to base 64
              const appendType = this.appendURLtype(this.returnUrl)
              this.isLoading = false
              this.errorType = paymentErrorType.GENERIC_ERROR
              this.backUrl = `${this.returnUrl}${appendType}status=${status}`
              this.tryAgainURL = `/makepayment/${this.paymentId}/${encodeURIComponent(this.returnUrl)}`
            })
        }
        goToUrl (url:string) {
          window.location.href = url
        }

        appendURLtype (url:string = '') {
          return url.match(/[\\?]/g) ? '&' : '?'
        }
}
</script>

<style lang="scss" scoped>
    @import '../../assets/scss/theme.scss';
    article{
        .v-card{
            line-height: 1.2rem;
            font-size: 0.875rem;
        }
    }
    section p{
        // font-size 0.875rem
        color: $gray6;
    }
    section + section{
        margin-top: 3rem;
    }
    h2{
        margin-bottom: 0.25rem;
    }
    #AR-header{
        margin-bottom: 1.25rem;
        line-height: 2rem;
        letter-spacing: -0.01rem;
        font-size: 2rem;
        font-weight: 500;
    }
    #AR-step-1-header, #AR-step-2-header, #AR-step-3-header, #AR-step-4-header{
        margin-bottom: 0.25rem;
        margin-top: 3rem;
        font-size: 1.125rem;
        font-weight: 500;
    }
    .title-container{
        margin-bottom: 0.5rem;
    }
    .agm-date{
        margin-left: 0.25rem;
        font-weight: 300;
    }
    // Save & Filing Buttons
    #buttons-container{
        padding-top: 2rem;
        border-top: 1px solid $gray5;
        .buttons-left{
            width: 50%;
        }
        .buttons-right{
            margin-left: auto;
        }
        .v-btn + .v-btn{
            margin-left: 0.5rem;
        }
    }
    .genErr{
        font-size: 0.9rem;
    }
    .error-dialog-padding{
        margin-left: 1rem;
    }

</style>
