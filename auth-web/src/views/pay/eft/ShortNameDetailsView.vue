<template>
  <v-container
    id="shortname-details"
    class="view-container"
  >
    <v-snackbar
      id="linked-account-snackbar"
      v-model="snackbar"
      :timeout="4000"
      transition="fade"
    >
      {{ snackbarText }}
    </v-snackbar>
    <div class="view-header flex-column d-flex justify-space-between">
      <div class="shortname-title">
        <h1 class="view-header__title">
          {{ shortNameDetails.shortName }}
        </h1>
        <p class="mt-3 mb-0 unsettled-amount">
          <span class="font-weight-bold">Unsettled Amount: </span>{{ unsettledAmount }}
        </p>
      </div>
      <div class="shortname-info">
        <div class="mb-2 overflow-wrap">
          <span class="font-weight-bold">Type: </span>
          {{ getShortNameTypeDescription(shortName.shortNameType) }}
        </div>
        <div class="mb-2 overflow-wrap">
          <span class="font-weight-bold">CAS Supplier Number: </span>
          {{ shortName.casSupplierNumber || 'N/A' }}
          <span
            class="pl-4 primary--text cursor-pointer"
            data-test="btn-edit"
            @click="openShortNameSupplierNumberDialog()"
          >
            <v-icon
              color="primary"
              size="20"
            > mdi-pencil-outline</v-icon>
            Edit
          </span>
        </div>
        <div class="overflow-wrap">
          <span class="font-weight-bold">Email: </span>
          <span class="email">{{ shortName.email || 'N/A' }}</span>
          <span
            class="pl-4 primary--text cursor-pointer"
            data-test="btn-edit"
            @click="openShortNameEmailDialog()"
          >
            <v-icon
              color="primary"
              size="20"
            > mdi-pencil-outline</v-icon>
            Edit
          </span>
        </div>
      </div>
    </div>
    <v-alert
      v-if="displayRefundAlert && canEFTRefund"
      class="mt-3 mb-4 alert-item account-alert-inner"
      :icon="false"
      prominent
      outlined
      type="warning"
    >
      <div class="account-alert-inner mb-0">
        <v-icon
          medium
        >
          mdi-alert
        </v-icon>
        <p class="account-alert__info mb-0 pl-3">
          <strong>Caution:</strong> Please verify if the unsettled amount of {{ unsettledAmount }} on the short name
          can be refunded or linked to a new account. If it's insufficient to settle an outstanding statement,
          the settlement process will be on hold until full payment is received.
        </p>
      </div>
    </v-alert>

    <ShortNameFinancialDialog
      :isShortNameFinancialDialogOpen="displayShortNameFinancialDialog"
      :shortName="shortName"
      :shortNameFinancialDialogType="shortNameFinancialDialogType"
      @on-patch="onShortNamePatch"
      @close-short-name-email-dialog="closeShortNameLinkingDialog"
    />

    <ShortNameRefund
      v-if="displayRefundAlert && canEFTRefund"
      :shortNameDetails="shortNameDetails"
      :unsettledAmount="unsettledAmount"
      class="mb-12"
    />

    <ShortNameAccountLink
      class="mb-12"
      :shortNameDetails="shortNameDetails"
      :highlightIndex="highlightIndex"
      @on-link-account="onLinkAccount"
      @on-payment-action="onPaymentAction"
    />

    <ShortNamePaymentHistory
      :shortNameDetails="shortNameDetails"
      @on-payment-action="onPaymentAction"
    />
  </v-container>
</template>
<script lang="ts">
import { PropType, computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import PaymentService from '@/services/payment.services'
import { Role } from '@/util/constants'
import ShortNameAccountLink from '@/components/pay/eft/ShortNameAccountLink.vue'
import { ShortNameDetails } from '@/models/pay/short-name'
import ShortNameFinancialDialog from '@/components/pay/eft/ShortNameFinancialDialog.vue'
import ShortNamePaymentHistory from '@/components/pay/eft/ShortNamePaymentHistory.vue'
import ShortNameRefund from '@/components/pay/eft/ShortNameRefund.vue'
import ShortNameUtils from '@/util/short-name-utils'
import moment from 'moment'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'ShortNameMappingView',
  components: { ShortNameAccountLink, ShortNameFinancialDialog, ShortNamePaymentHistory, ShortNameRefund },
  props: {
    shortNameId: {
      type: String as PropType<string>,
      default: null
    }
  },
  setup (props) {
    const userStore = useUserStore()
    const currentUser = computed(() => userStore.currentUser)
    const state = reactive({
      shortNameDetails: {} as ShortNameDetails,
      shortName: {},
      highlightIndex: -1,
      snackbar: false,
      snackbarText: '',
      unsettledAmount: '',
      displayRefundAlert: false,
      canEFTRefund: computed((): boolean => currentUser.value?.roles?.includes(Role.EftRefund)),
      displayShortNameFinancialDialog: false,
      shortNameFinancialDialogType: ''
    })

    onMounted(async () => {
      await loadShortname(props.shortNameId)
      updateState()
    })

    function updateState () {
      const details: ShortNameDetails = state.shortNameDetails

      state.unsettledAmount = details.creditsRemaining !== undefined
        ? CommonUtils.formatAmount(details.creditsRemaining) : ''

      state.displayRefundAlert = (
        (details.creditsRemaining > 0 && details.linkedAccountsCount > 0) ||
          (details.creditsRemaining > 0 && details.linkedAccountsCount <= 0 &&
              moment(details.lastPaymentReceivedDate).isBefore(moment().subtract(30, 'days')))
      )
    }

    const unsettledAmountHeader = computed<string>(() => {
      const details: ShortNameDetails = state.shortNameDetails
      return `Unsettled Amount for ${details.shortName}: ${state.unsettledAmount}`
    })

    function closeShortNameLinkingDialog () {
      state.displayShortNameFinancialDialog = false
    }

    async function onLinkAccount (account: any, results: Array<any>) {
      const indexOf = results.findIndex((result) => result.id === account.id)
      await loadShortname(props.shortNameId)
      state.snackbarText = `Bank short name ${state.shortNameDetails.shortName} was successfully linked.`
      state.highlightIndex = indexOf
      state.snackbar = true

      setTimeout(() => {
        state.highlightIndex = -1
      }, 4000)
    }

    function openShortNameEmailDialog () {
      state.shortNameFinancialDialogType = 'EMAIL'
      state.displayShortNameFinancialDialog = true
    }

    function openShortNameSupplierNumberDialog () {
      state.shortNameFinancialDialogType = 'CAS_SUPPLIER_NUMBER'
      state.displayShortNameFinancialDialog = true
    }

    async function onPaymentAction () {
      await loadShortname(props.shortNameId)
      updateState()
    }

    async function onShortNamePatch () {
      const eftShortNameResponse = await PaymentService.getEFTShortName(state.shortNameDetails.id)
      state.shortName = eftShortNameResponse.data
    }

    async function loadShortname (shortnameId: string): Promise<void> {
      try {
        const response = await PaymentService.getEFTShortnameSummary(shortnameId)
        if (response?.data) {
          state.shortNameDetails = response.data['items'][0]
          const eftShortNameResponse = await PaymentService.getEFTShortName(state.shortNameDetails.id)
          state.shortName = eftShortNameResponse.data
        } else {
          throw new Error('No response from getEFTShortname')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTShortname.', error)
      }
    }

    return {
      ...toRefs(state),
      onLinkAccount,
      onPaymentAction,
      onShortNamePatch,
      openShortNameEmailDialog,
      openShortNameSupplierNumberDialog,
      formatCurrency: CommonUtils.formatAmount,
      unsettledAmountHeader,
      closeShortNameLinkingDialog,
      getShortNameTypeDescription: ShortNameUtils.getShortNameTypeDescription
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
  .email {
    word-wrap: break-word;
    word-break: break-all;
  }
  .view-header__title {
    font-size: 24px;
    line-height: 32px;
  }
  .unsettled-amount {
    font-size: 18px;
  }
  .shortname-info {
    font-size: 18px;
  }
  #shortname-details {
    padding-top: 0;
  }
  .account-alert-inner {
    .v-icon {
      color: $app-alert-orange;
    }
    background-color: $BCgovGold0 !important;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
  }
  .account-alert__info {
    flex: 1 1 auto;
    color: $TextColorGray;
  }
  .v-application .view-header {
    flex-direction: row!important;
    margin-top: 40px;
    margin-bottom: 60px;
    .shortname-title, .shortname-info {
      z-index: 1;
      flex: 1 1 100%;
    }
    .shortname-info {
      flex: 0 0 320px;
    }
    &:after {
      content: '';
      display: block;
      position: absolute;
      left: 0;
      right: 0;
      top: -20px;
      z-index: 0;
      width: 100%;
      height: 160px;
      background-color: white;
      margin-top: 20px;
    }
  }
  .overflow-wrap {
    overflow-wrap: anywhere;
  }
</style>
