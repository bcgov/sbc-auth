<template>
  <v-card
    class="bcol-payment-card"
    data-test="div-bcol-payment-card"
  >
    <!-- wording for credit card payment -->
    <PayWithCreditCard
      v-if="payWithCreditCard"
      :totalBalanceDue="totalBalanceDue"
      :showPayWithOnlyCC="showPayWithOnlyCC"
      :partialCredit="partialCredit"
    />
    <!-- wording for online bank payment -->
    <PayWithOnlineBanking
      v-else
      :onlineBankingData="onlineBankingData"
    />

    <v-card-text class="pt-0 pb-8 px-8">
      <template v-if="!overCredit">
        <p v-if="showPayWithOnlyCC">
          Click <strong>"pay now"</strong> to complete transaction balance with credit card
        </p>
        <p v-else>
          Would you like to complete transaction immediately?
        </p>
        <v-checkbox
          v-model="payWithCreditCard"
          class="pay-with-credit-card mb-4"
          color="primary"
          hide-details
          :disabled="showPayWithOnlyCC"
        >
          <template #label>
            <div class="ml-1">
              <div class="font-weight-bold">
                Credit Card
              </div>
              <div class="subtitle-2 mt-1">
                Pay your balance and access files <strong>immediately</strong>
              </div>
              <div
                v-if="partialCredit"
                class="subtitle-2"
              >
                Account credit will <strong>not apply</strong> with credit card payment option.
              </div>
            </div>
          </template>
        </v-checkbox>
      </template>
      <v-divider class="mt-8" />
      <v-row>
        <v-col
          cols="12"
          class="pt-8 pb-0 d-inline-flex"
        >
          <v-btn
            v-if="!payWithCreditCard && !overCredit"
            large
            text
            color="primary"
            class="px-0"
            data-test="btn-download-invoice"
            @click="emitBtnClick('download-invoice')"
          >
            <v-icon class="mr-1">
              mdi-file-download-outline
            </v-icon>
            Download Invoice
          </v-btn>
          <v-spacer />
          <template v-if="payWithCreditCard">
            <v-btn
              large
              color="primary"
              width="100"
              class="font-weight-bold"
              @click="emitBtnClick('pay-with-credit-card')"
            >
              Pay Now
            </v-btn>
            <v-btn
              large
              width="100"
              class="ml-3"
              data-test="btn-cancel-online-banking"
              @click="cancel"
            >
              Cancel
            </v-btn>
          </template>
          <template v-else>
            <v-btn
              large
              color="primary"
              width="100"
              class="font-weight-bold"
              data-test="btn-complete-online-banking"
              @click="emitBtnClick('complete-online-banking')"
            >
              Ok
            </v-btn>
          </template>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, onMounted, reactive } from '@vue/composition-api'
import PayWithCreditCard from '@/components/pay/PayWithCreditCard.vue'
import PayWithOnlineBanking from '@/components/pay/PayWithOnlineBanking.vue'
import PaymentServices from '@/services/payment.services'

export default defineComponent({
  name: 'PaymentCard',
  components: {
    PayWithCreditCard,
    PayWithOnlineBanking
  },
  props: {
    paymentCardData: {
      type: Object,
      required: true
    },
    showPayWithOnlyCC: {
      type: Boolean,
      default: false
    }
  },
  emits: ['complete-online-banking', 'pay-with-credit-card', 'download-invoice'],
  setup (props, { emit }) {
    const state = reactive({
      payWithCreditCard: false,
      balanceDue: 0,
      totalBalanceDue: 0,
      cfsAccountId: '',
      payeeName: '',
      onlineBankingData: {} as any,
      credit: null as number | null,
      doHaveCredit: false,
      overCredit: false,
      partialCredit: false,
      creditBalance: 0,
      paymentId: '',
      totalPaid: 0,
      originalAmount: 0
    })

    const initializePaymentData = () => {
      state.totalBalanceDue = props.paymentCardData?.totalBalanceDue || 0
      state.totalPaid = props.paymentCardData?.totalPaid || 0
      state.originalAmount = (state.totalBalanceDue - state.totalPaid) || 0
      state.balanceDue = state.originalAmount
      state.payeeName = props.paymentCardData.payeeName
      state.cfsAccountId = props.paymentCardData?.cfsAccountId || ''
      state.payWithCreditCard = props.showPayWithOnlyCC
      state.credit = props.paymentCardData.obCredit || 0
      state.doHaveCredit = props.paymentCardData?.obCredit > 0
      state.creditBalance = Math.max(state.credit - state.balanceDue, 0)

      if (state.doHaveCredit) {
        state.overCredit = state.credit >= state.totalBalanceDue
        state.partialCredit = state.credit < state.totalBalanceDue
        state.balanceDue = Math.max(state.balanceDue - state.credit, 0)
        // Credit card uses totalBalanceDue, not balanceDue
        // Thus it doesn't include credit in calculation
      }

      state.paymentId = props.paymentCardData.paymentId

      // setting online data
      state.onlineBankingData = {
        originalAmount: state.originalAmount,
        totalBalanceDue: state.balanceDue,
        payeeName: state.payeeName,
        cfsAccountId: state.cfsAccountId,
        overCredit: state.overCredit,
        partialCredit: state.partialCredit,
        creditBalance: state.creditBalance,
        credit: state.credit
      }
    }

    function emitBtnClick (eventName: string) {
      if (eventName === 'complete-online-banking' && state.doHaveCredit) {
        PaymentServices.applycredit(state.paymentId)
      }
      emit(eventName)
    }

    function cancel () {
      if (props.showPayWithOnlyCC) { // cancel will redirect back to page
        emitBtnClick('complete-online-banking')
      } else {
        state.payWithCreditCard = false
      }
    }

    onMounted(() => {
      initializePaymentData()
    })

    return {
      ...state,
      cancel,
      emitBtnClick
    }
  }
})
</script>

<style lang="scss" scoped>
.bcol-payment-card {
  .heading-info {
    background: var(--v-primary-base);
    color: #fff !important;
    h2 {
      color: #fff !important;
    }
    .payee-name {
      padding-right: 16px;
      margin-right: 16px;
      border-right: 1px solid white;
    }
  }
  ol {
    li {
      margin-bottom: 4px;
    }
  }
  .pay-with-credit-card {
    ::v-deep {
      .v-input__slot {
        align-items: flex-start;
      }
      .v-label {
        display: block;
        color: #000;
        .subtxt {
          font-size: .875rem;
          margin-top: 6px;
        }
      }
    }
  }
}
</style>
