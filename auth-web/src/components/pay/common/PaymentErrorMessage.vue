<template>
  <v-container
    class="view-container pay-error"
    data-test="pay-error"
  >
    <v-row justify="center">
      <v-col
        cols="12"
        lg="8"
        class="text-center"
      >
        <v-icon
          size="35"
          color="error"
          class="mb-6"
        >
          {{ error.errorIcon }}
        </v-icon>
        <h1 v-html="error.errorTitle" />
        <p
          class="mt-8 mb-12"
          v-html="error.errorMessage"
        />
        <div class="btns">
          <v-btn
            large
            link
            color="primary"
            :href="backUrl"
            class="error-btn"
            data-test="btn-pay-error-tryagain"
          >
            Ok
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import Vue from 'vue'
import { paymentErrorType } from '@/util/constants'
import { StringChain } from 'lodash'

@Component
export default class PaymentErrorMessage extends Vue {
  @Prop({ default: 'GENERIC_ERROR' }) errorType: string
  @Prop({ default: '' }) backUrl: StringChain

  public get error () {
    let errorTitle = ''
    let errorMessage = ''
    let errorIcon = 'mdi-alert-circle-outline'

    switch (this.errorType) {
      case paymentErrorType.GENERIC_ERROR:
        errorTitle = this.$t('paymentErrorTitle').toString()
        errorMessage = this.$t('paymentErrorSubText').toString()
        break
      case paymentErrorType.PAYMENT_CANCELLED:
        errorTitle = this.$t('paymentCancelTitle').toString()
        errorMessage = this.$t('paymentCancelSubText').toString()
        break
      case paymentErrorType.DECLINED:
        errorTitle = this.$t('paymentDeclinedTitle').toString()
        errorMessage = this.$t('paymentDeclinedSubText').toString()
        break
      case paymentErrorType.INVALID_CARD_NUMBER:
        errorTitle = this.$t('paymentInvalidErrorTitle').toString()
        errorMessage = this.$t('paymentInvalidErrorSubText').toString()
        break
      case paymentErrorType.DECLINED_EXPIRED_CARD:
        errorTitle = this.$t('paymentExpiredCardErrorTitle').toString()
        errorMessage = this.$t('paymentExpiredCardErrorSubText').toString()
        break
      case paymentErrorType.DUPLICATE_ORDER_NUMBER:
        errorTitle = this.$t('paymentDuplicateErrorTitle').toString()
        errorMessage = this.$t('paymentDuplicateErrorSubText').toString()
        break
      case paymentErrorType.TRANSACTION_TIMEOUT_NO_DEVICE:
        errorTitle = this.$t('paymentTimeoutErrorTitle').toString()
        errorMessage = this.$t('paymentTimeoutErrorSubText').toString()
        errorIcon = 'mdi-clock-outline'
        break
      case paymentErrorType.VALIDATION_ERROR:
        errorTitle = this.$t('paymentValidationErrorTitle').toString()
        errorMessage = this.$t('paymentValidationErrorSubText').toString()
        break
      default:
        errorTitle = this.$t('paymentErrorTitle').toString()
        errorMessage = this.$t('paymentErrorSubText').toString()
        break
    }

    return { errorTitle, errorMessage, errorIcon }
  }
}
</script>

<style lang="scss" scoped>
  .pay-error{
    .error-btn{
          min-width: 139px !important;

    }
  }
</style>
