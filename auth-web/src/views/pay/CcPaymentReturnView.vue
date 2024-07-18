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
        <SbcSystemError
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

import { defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import PaymentServices from '@/services/payment.services'
import SbcSystemError from 'sbc-common-components/src/components/SbcSystemError.vue'
import { useI18n } from 'vue-i18n-composable'

export default defineComponent({
  name: 'CcPaymentReturnView',
  components: {
    SbcSystemError
  },
  props: {
    paymentId: { type: String, default: '' },
    transactionId: { type: String, default: '' },
    payResponseUrl: { type: String, default: '' }
  },
  setup (props) {
    const { t } = useI18n()
    const state = reactive({
      errorMessage: '',
      returnUrl: '',
      // show modal when paybc is down..otherwise [all unhandled technical error , show plain text error message..]
      showErrorModal: false
    })

    function goToUrl (url: string) {
      window.location.href = url
    }

    onMounted(async () => {
      if (!props.paymentId || !props.transactionId) {
        state.errorMessage = t('payNoParams').toString()
        return
      }

      try {
        const { data } = await PaymentServices.updateTransactionForPadPayment(props.paymentId, props.transactionId, props.payResponseUrl)
        state.returnUrl = data.clientSystemUrl

        if (data?.paySystemReasonCode === 'SERVICE_UNAVAILABLE') {
          // PayBC is down, show the custom modal
          state.errorMessage = t('payFailedMessagePayBcDown').toString()
          state.showErrorModal = true
        } else {
          goToUrl(state.returnUrl)
        }
      } catch {
        state.showErrorModal = false
        state.errorMessage = t('payFailedMessage').toString()
      }
    })

    return {
      ...toRefs(state),
      goToUrl
    }
  }
})
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
