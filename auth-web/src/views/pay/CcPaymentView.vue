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
          {{ t('paymentPrepareMsg') }}
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
import { InvoiceStatus, SessionStorageKeys } from '@/util/constants'
import { defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { isErrorType, normalizeError } from '@/util/error-util'
import ConfigHelper from '@/util/config-helper'
import PaymentServices from '@/services/payment.services'
import SbcSystemError from 'sbc-common-components/src/components/SbcSystemError.vue'
import { useI18n } from 'vue-i18n-composable'

export default defineComponent({
  name: 'CcPaymentView',
  components: {
    SbcSystemError
  },
  props: {
    paymentId: { type: String, default: '' },
    redirectUrl: { type: String, default: '' }
  },
  setup (props) {
    const { t } = useI18n()
    const state = reactive({
      errorMessage: '',
      showErrorModal: false,
      returnUrl: ''
    })

    const goToUrl = (url: string) => {
      window.location.href = url || props.redirectUrl
    }

    onMounted(async () => {
      if (!props.paymentId || !redirectUrlFixed()) {
        state.errorMessage = t('payNoParams').toString()
        return
      }
      const accountJson = ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount) || '{}'
      const account = accountJson ? JSON.parse(accountJson) : null
      if (account?.id) {
        try {
          const response = await PaymentServices.getInvoice(props.paymentId, account.id)
          const invoiceData = response?.data
          if (invoiceData && [InvoiceStatus.DELETE_ACCEPTED, InvoiceStatus.DELETED].includes(invoiceData.statusCode as InvoiceStatus)) {
            state.errorMessage = t('invoiceDeletedMessage').toString()
            state.showErrorModal = true
            return
          }
        } catch {
          // If getInvoice fails, continue to createTransactionForPadPayment (existing behaviour)
        }
      }
      PaymentServices.createTransactionForPadPayment(props.paymentId, redirectUrlFixed())
        .then(response => {
          state.returnUrl = response.data.paySystemUrl
          goToUrl(state.returnUrl)
        })
        .catch(error => {
          state.errorMessage = t('payFailedMessage').toString()
          const normalized = normalizeError(error)
          if (isErrorType(normalized, 'INVALID_TRANSACTION')) {
            goToUrl(redirectUrlFixed())
          } else {
            state.showErrorModal = true
          }
        })
    })

    function redirectUrlFixed () {
      if (!props.redirectUrl.includes('://')) {
        return props.redirectUrl.replace(':/', '://')
      }
      return props.redirectUrl
    }

    return {
      ...toRefs(state),
      t,
      goToUrl
    }
  }
})
</script>

<style lang="scss" scoped>

</style>
