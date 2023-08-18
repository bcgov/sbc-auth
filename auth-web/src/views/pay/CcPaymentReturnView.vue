<template>
  <div id="app">
    <v-container>
      <v-row
        justify="center"
        align="center"
      >
        <v-progress-circular
          v-if="!errorMessage"
          color="primary"
          :size="50"
          indeterminate
        />
        <div
          v-if="!errorMessage"
          class="loading-msg"
        >
          {{ $t('paymentDoneMsg') }}
        </div>
        <div
          v-if="errorMessage && !showErrorModal"
          class="loading-msg"
        >
          {{ errorMessage }}
        </div>
        <sbc-system-error
          v-if="showErrorModal && errorMessage"
          title="Payment Failed"
          primaryButtonTitle="Continue to Account Page"
          :description="errorMessage"
          @continue-event="goToUrl(returnUrl)"
        />
      </v-row>
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
export default class CcPaymentReturnView extends Vue {
  @Prop() paymentId: string
  @Prop() transactionId: string
  @Prop() payResponseUrl: string
  returnUrl: string
  errorMessage: string = ''
  // show modal when paybc is down..otherwise [all unhandled technical error , show plain text error message..]
  showErrorModal: boolean = false

  mounted () {
    if (!this.paymentId || !this.transactionId) {
      this.errorMessage = this.$t('payNoParams').toString()
      return
    }
    PaymentServices.updateTransactionForPadPayment(this.paymentId, this.transactionId, this.payResponseUrl)
      .then(response => {
        this.returnUrl = response.data.clientSystemUrl
        if (response.data.paySystemReasonCode && response.data.paySystemReasonCode === 'SERVICE_UNAVAILABLE') {
          // PayBC down time..Show the custom modal
          this.errorMessage = this.$t('payFailedMessagePayBcDown').toString()
          this.showErrorModal = true
        } else {
          // all good..go back
          this.goToUrl(this.returnUrl)
        }
      })
      .catch(() => {
        // technical error..need not to show the modal
        this.showErrorModal = false
        this.errorMessage = this.$t('payFailedMessage').toString()
      })
  }

  goToUrl (url: string) {
    window.location.href = url
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';

article {
  .v-card {
    line-height: 1.2rem;
    font-size: 0.875rem;
  }
}

section p {
  // font-size 0.875rem
  color: $gray6;
}

section + section {
  margin-top: 3rem;
}

h2 {
  margin-bottom: 0.25rem;
}

#AR-header {
  margin-bottom: 1.25rem;
  line-height: 2rem;
  letter-spacing: -0.01rem;
  font-size: 2rem;
  font-weight: 500;
}

#AR-step-1-header, #AR-step-2-header, #AR-step-3-header, #AR-step-4-header {
  margin-bottom: 0.25rem;
  margin-top: 3rem;
  font-size: 1.125rem;
  font-weight: 500;
}

.title-container {
  margin-bottom: 0.5rem;
}

.agm-date {
  margin-left: 0.25rem;
  font-weight: 300;
}

// Save & Filing Buttons
#buttons-container {
  padding-top: 2rem;
  border-top: 1px solid $gray5;

  .buttons-left {
    width: 50%;
  }

  .buttons-right {
    margin-left: auto;
  }

  .v-btn + .v-btn {
    margin-left: 0.5rem;
  }
}

.genErr {
  font-size: 0.9rem;
}

.error-dialog-padding {
  margin-left: 1rem;
}
</style>
