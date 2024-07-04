<template>
  <div>
    <CautionBox
      data-test="caution-box-details"
      setImportantWord="Important"
      :setAlert="false"
      :setMsg="alertMessage()"
    />
    <v-card
      outlined
      flat
      class="amount-owing-details-card mb-8 mt-8"
    >
      <v-card-text class="py-2 px-6">
        <v-row>
          <v-col cols="9">
            Amount Owing Details
          </v-col>
          <v-col class="text-end">
            {{ currentDateString() }}
          </v-col>
        </v-row>
        <v-divider class="my-2 mt-1" />
        <v-row
          v-for="statement in statementsOwing"
          :key="statement.id"
          data-test="statement-row"
        >
          <v-col
            cols="9"
            class="statement-col"
            data-test="statement-label"
          >
            <a
              class="link"
              @click="downloadStatement(statement)"
            >{{ formatStatementString(statement.fromDate, statement.toDate) }}</a>
          </v-col>
          <v-col
            class="text-end statement-col"
            data-test="statement-owing-value"
          >
            {{ formatCurrency(statement.amountOwing) }}
          </v-col>
        </v-row>
        <v-row>
          <v-col
            cols="9"
            class="statement-col"
          >
            Other unpaid transactions
          </v-col>
          <v-col
            class="text-end statement-col"
            data-test="total-other-owing"
          >
            {{ formatCurrency(invoicesOwing) }}
          </v-col>
        </v-row>
        <v-divider class="my-2 mt-1" />
        <v-row class="font-weight-bold">
          <v-col cols="9">
            Total Amount Due
          </v-col>
          <v-col
            class="text-end"
            data-test="total-amount-due"
          >
            {{ formatCurrency(totalAmountDue) }}
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <div>
      <span class="choose-text">Choose a way to settle your outstanding balance:</span>
    </div>

    <v-card
      outlined
      flat
      class="payment-method-card mb-8 mt-8"
      data-test="cc-payment-card"
    >
      <v-card-text class="payment-method-card-text py-2 d-flex">
        <input
          type="radio"
          class="payment-method-radio ml-8 mr-8 d-flex"
          name="payment-method"
          checked
        >
        <div class="payment-method-description d-flex">
          <div class="payment-type-label d-flex">
            <v-icon
              class="payment-type-icon pr-2"
              large
            >
              mdi-credit-card-outline
            </v-icon>
            <div class="payment-type-description">
              Credit Card
            </div>
          </div>
          <div class="payment-method-description pt-1 d-flex">
            For immediate settlement, pay any outstanding amounts owed using a credit card.
          </div>
        </div>
      </v-card-text>
    </v-card>
    <v-divider />
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          class="secondary-btn"
          data-test="btn-stepper-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          :disabled="!totalAmountDue"
          @click="goNext"
        >
          <span>Next</span>
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">

import { PropType, computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import CautionBox from '@/components/auth/common/CautionBox.vue'
import CommonUtils from '@/util/common-util'
import ConfigHelper from 'sbc-common-components/src/util/config-helper'
import { Pages } from '@/util/constants'
import { Payment } from '@/models/Payment'
import { StatementListItem } from '@/models/statement'
import moment from 'moment'
import { useOrgStore } from '@/stores'

export default defineComponent({
  name: 'OutstandingBalances',
  components: { CautionBox },
  props: {
    orgId: {
      type: String as PropType<string>,
      default: ''
    },
    changePaymentType: {
      type: String as PropType<string>,
      default: ''
    },
    statementSummary: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['step-forward'],
  setup (props, { root }) {
    const { statementSummary } = toRefs(props)
    const orgStore = useOrgStore()
    const state = reactive({
      statementsOwing: [],
      invoicesOwing: 0
    })

    const handlePayment = async () => {
      const payment: Payment = await orgStore.createOutstandingAccountPayment()
      const baseUrl = ConfigHelper.getAuthContextPath()
      const queryParams = `?paymentId=${payment?.id}&changePaymentType=${props.changePaymentType}`
      const returnUrl = `${baseUrl}/${Pages.MAIN}/${props.orgId}/${Pages.PAY_OUTSTANDING_BALANCE}${queryParams}`
      const encodedUrl = encodeURIComponent(returnUrl)

      // redirect to make payment UI
      await root.$router.push(`${Pages.MAKE_PAD_PAYMENT}${payment.id}/transactions/${encodedUrl}`)
    }

    function goBack () {
      this.$router.push(`${Pages.ACCOUNT_SETTINGS}/${Pages.PAYMENT_OPTION}`)
    }

    function goNext () {
      handlePayment()
    }

    async function getStatementsOwing () {
      const filterParams = {
        pageNumber: 1,
        pageLimit: 100,
        filterPayload: {
          isOwing: 'true'
        }
      }
      const response = await orgStore.getStatementsList(filterParams, Number(props.orgId))
      state.statementsOwing = response?.items || []
    }

    onMounted(async () => {
      await getStatementsOwing()
      state.invoicesOwing = statementSummary.value.totalInvoiceDue
    })

    const totalAmountDue = computed<number>(() => {
      const totalStatementOwing = state.statementsOwing.reduce((sum, statement) => sum + statement.amountOwing, 0)
      return totalStatementOwing + state.invoicesOwing
    })

    function currentDateString () {
      return CommonUtils.formatDisplayDate(moment(), 'MMMM DD, YYYY')
    }

    async function downloadStatement (statement: StatementListItem) {
      try {
        const fileType = 'application/pdf'
        const response = await orgStore.getStatement({ statementId: statement.id, type: fileType })
        const contentDispArr = response?.headers['content-disposition'].split('=')
        const fileName = (contentDispArr.length && contentDispArr[1]) ? contentDispArr[1] : `bcregistry-statement-pdf`
        CommonUtils.fileDownload(response.data, fileName, 'application/pdf')
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    function alertMessage () {
      return 'Please settle any outstanding statements and transactions before changing your payment method, ' +
          'or wait until all unpaid transactions are settled by your current method.'
    }

    watch([statementSummary], ([newStatementSummary]) => {
      // Perform actions when any of the watched props change
      console.log('statementSummary changed to:', newStatementSummary)
    })

    return {
      ...toRefs(state),
      goBack,
      goNext,
      alertMessage,
      currentDateString,
      formatStatementString: CommonUtils.formatStatementString,
      formatCurrency: CommonUtils.formatAmount,
      downloadStatement,
      totalAmountDue
    }
  }
})

</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
@import "$assets/scss/actions.scss";

.link {
  color: var(--v-primary-base) !important;
  text-decoration: underline;
  cursor: pointer;
}

.choose-text {
  font-size: 16px;
  font-weight: bold;
}
.amount-owing-details-card {
  border-color: $BCgovInputError !important;
  border-width: 2px !important;
  margin-bottom: 12px !important;
  .statement-col {
    padding-top: 4px !important;
    padding-bottom: 4px !important;
  }
}

.payment-method-card {
  border-color: $app-blue !important;
  border-width: 2px !important;
  margin-bottom: 12px !important;

  .payment-method-card-text {
    align-items: center;
    min-height: 120px;
    .payment-method-radio {
      width: 24px;
      height: 24px;
      align-items: center;
    }
    .payment-type-label {
      .payment-type-icon {
        font-size: 24px !important;
        color: $app-dk-blue;
      }
      .payment-type-description {
        font-size: 20px;
        font-weight: bolder;
      }
    }
    .payment-method-description{
      flex-direction: column;
      font-size: 14px;
    }
  }
}
</style>
