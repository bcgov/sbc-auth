<template>
  <div data-test="div-payment-view">
    <v-container
      v-if="showLoading"
      data-test="div-payment-view-loading"
    >
      <v-row
        justify="center"
        align="center"
        class="py-12 loading-progressbar flex-column"
      >
        <v-progress-circular
          color="primary"
          :size="80"
          :width="5"
          indeterminate
          class="mt-12"
        />
        <div class="loading-msg">
          {{ showdownloadLoading ? $t('paymentDownloadMsg') : $t('paymentPrepareMsg') }}
        </div>
      </v-row>
    </v-container>
    <div v-else>
      <v-container
        v-if="errorMessage"
        data-test="div-payment-view-error"
      >
        <v-row
          justify="center"
          align="center"
        >
          <SbcSystemError
            v-if="showErrorModal"
            title="Payment Failed"
            primaryButtonTitle="Continue to Filing"
            :description="errorMessage"
            @continue-event="goToUrl(returnUrl)"
          />
          <div
            v-else
            class="mt-12"
          >
            <div class="text-center mb-4">
              <v-icon
                color="error"
                size="30"
              >
                mdi-alert-outline
              </v-icon>
            </div>
            <h4>{{ errorMessage }}</h4>
          </div>
        </v-row>
      </v-container>
      <v-container
        v-if="showOnlineBanking"
        data-test="div-payment-view-container"
        class="view-container"
      >
        <div class="payment-view-content">
          <h1 class="mb-1">
            Make a payment
          </h1>
          <p class="mb-8">
            Please find your balance and payment details below.
          </p>
          <PaymentCard
            :paymentCardData="paymentCardData"
            :showPayWithOnlyCC="showPayWithOnlyCC"
            @complete-online-banking="completeOBPayment"
            @pay-with-credit-card="payNow"
            @download-invoice="downloadInvoice"
          />
        </div>
      </v-container>
    </div>
  </div>
</template>

<script lang="ts">
import { PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { OrgPaymentDetails } from '@/models/Organization'
import PaymentCard from '@/components/pay/PaymentCard.vue'
import PaymentService from '@/services/payment.services'

import SbcSystemError from 'sbc-common-components/src/components/SbcSystemError.vue'
import { mapActions } from 'pinia'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'PaymentView',
  components: {
    SbcSystemError,
    PaymentCard
  },
  props: {
    paymentId: {
      type: String,
      default: ''
    },
    redirectUrl: {
      type: String,
      default: ''
    }
  },
  setup (props) {
    const state = reactive({
      showLoading: true,
      showdownloadLoading: false,
      showOnlineBanking: false,
      errorMessage: '',
      showErrorModal: false,
      returnUrl: '',
      paymentCardData: null,
      showPayWithOnlyCC: false
    })

    const { createTransaction, getOrgPayments, getInvoice, updateInvoicePaymentMethodAsCreditCard, downloadOBInvoice } = mapActions(useOrgStore, [
      'createTransaction',
      'getOrgPayments',
      'getInvoice',
      'updateInvoicePaymentMethodAsCreditCard',
      'downloadOBInvoice'
    ])

    // We need this, otherwise we can get redirect Urls with just a single slash.
    const redirectUrlFixed = computed(() => {
      if (!props.redirectUrl.includes('://')) {
        return props.redirectUrl.replace(':/', '://')
      }
      return props.redirectUrl
    })

    function isUserSignedIn (): boolean {
      return !!ConfigHelper.getFromSession('KEYCLOAK_TOKEN')
    }

    function getAccountFromSession (): AccountSettings {
      return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
    }

    function goToUrl (url: string) {
      window.location.href = url || redirectUrlFixed.value
    }

    function completeOBPayment () {
      goToUrl(state.returnUrl)
    }

    function doCreateTransaction () {
      createTransaction({
        paymentId: props.paymentId,
        redirectUrl: redirectUrlFixed.value
      }).then((transactionDetails) => {
        state.showLoading = false
        state.returnUrl = transactionDetails?.paySystemUrl
        goToUrl(state.returnUrl)
      })
    }

    function doHandleError (error) {
      state.showLoading = false
      if (error.response.data && ['COMPLETED_PAYMENT', 'INVALID_TRANSACTION'].includes(error.response.data.type)) {
        // Skip PAYBC, take directly to the "clients redirect url", this avoids transaction already done error.
        PaymentService.isValidRedirectUrl(redirectUrlFixed.value).then((isValid) => {
          if (!isValid) {
            state.errorMessage = 'Payment failed' // Replace with $t('payFailedMessage') when i18n is available
            throw new Error('Invalid redirect url: ' + redirectUrlFixed.value)
          }
          goToUrl(redirectUrlFixed.value)
        })
      } else {
        state.errorMessage = 'Payment failed' // Replace with $t('payFailedMessage') when i18n is available
        state.showErrorModal = true
      }
    }

    function payNow () {
      // patch the transaction
      // redirect for payment
      try {
        const accountSettings = getAccountFromSession()
        updateInvoicePaymentMethodAsCreditCard({ paymentId: props.paymentId, accountId: accountSettings?.id })
        doCreateTransaction()
      } catch (error) {
        doHandleError(error)
      }
    }

    function downloadInvoice () {
      // download invoice fot online banking
      state.showLoading = true // to avoid rapid download clicks
      state.showdownloadLoading = true // to avoid rapid download clicks
      state.errorMessage = ''
      try {
        const downloadType = 'application/pdf'

        downloadOBInvoice(props.paymentId).then((response: any) => {
          const contentDispArr = response?.headers['content-disposition'].split('=')

          const fileName = (contentDispArr.length && contentDispArr[1]) ? contentDispArr[1] : `bcregistry-${props.paymentId}`
          CommonUtils.fileDownload(response.data, fileName, downloadType)
          state.showdownloadLoading = false
          state.showLoading = false
        }).catch(() => {
          state.showdownloadLoading = false
          state.showLoading = false
          state.errorMessage = 'Download failed' // Replace with $t('downloadFailedMessage') when i18n is available
          // state.showErrorModal = true
        })
      } catch {
        state.showdownloadLoading = false
        state.showLoading = false
        state.errorMessage = 'Download failed' // Replace with $t('downloadFailedMessage') when i18n is available
        // state.showErrorModal = true
      }
    }

    onMounted(() => {
      state.showLoading = true
      if (!props.paymentId || !props.redirectUrl) {
        state.showLoading = false
        state.errorMessage = 'No payment parameters' // Replace with $t('payNoParams') when i18n is available
        return
      }
      try {
        const accountSettings = getAccountFromSession()
        // user should be signed in and should have account as well
        if (isUserSignedIn() && !!accountSettings) {
          // get the invoice and check for OB
          try {
            getInvoice({ invoiceId: props.paymentId, accountId: accountSettings?.id }).then((invoice: any) => {
              if (invoice?.paymentMethod === PaymentTypes.ONLINE_BANKING) {
                // get account data to show in the UI
                getOrgPayments(accountSettings?.id).then((paymentDetails: OrgPaymentDetails) => {
                  state.paymentCardData = {
                    totalBalanceDue: invoice?.total || 0, // to fix credit amount
                    payeeName: ConfigHelper.getPaymentPayeeName(),
                    cfsAccountId: paymentDetails?.cfsAccount?.cfsAccountNumber || '',
                    obCredit: paymentDetails?.obCredit,
                    padCredit: paymentDetails?.padCredit,
                    paymentId: props.paymentId,
                    totalPaid: invoice?.paid || 0
                  }

                  state.showLoading = false
                  state.showOnlineBanking = true
                  // if isOnlineBankingAllowed is true, allowed show CC as only payment type
                  state.showPayWithOnlyCC = !invoice?.isOnlineBankingAllowed
                })
              }
            }).catch(() => {
              // eslint-disable-next-line no-console
              console.error('error in accessing the invoice.Defaulting to CC flow')
            })
          } catch {
            // eslint-disable-next-line no-console
            console.error('error in accessing the invoice.Defaulting to CC flow')
          }
        }

        if (!state.showOnlineBanking) {
          doCreateTransaction()
        }
      } catch (error) {
        doHandleError(error)
      }
    })

    return {
      ...toRefs(state),
      completeOBPayment,
      payNow,
      downloadInvoice,
      goToUrl
    }
  }
})
</script>

<style lang="scss" scoped>
.payment-view-content {
  margin: 0 auto;
  max-width: 48rem;
}

.loading-msg {
  font-weight: 600;
  margin-top: 14px;
}
</style>
