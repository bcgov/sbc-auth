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
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        {{ unsettledAmountHeader }}
      </h1>
      <p class="mt-3 mb-0">
        Review and verify short name details {{ canEFTRefund }}, {{ displayRefundAlert }}
      </p>
      <v-alert
        v-if="displayRefundAlert && canEFTRefund"
        class="mt-3 mb-0 alert-item account-alert-inner"
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
            Please verify if the {{ unsettledAmount }} balance is eligible for a refund, or you can link to a new account.
          </p>
        </div>
      </v-alert>
    </div>

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

    <ShortNameTransactions
      :shortNameDetails="shortNameDetails"
    />
  </v-container>
</template>
<script lang="ts">
import { PropType, computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import PaymentService from '@/services/payment.services'
import { Role } from '@/util/constants'
import ShortNameAccountLink from '@/components/pay/eft/ShortNameAccountLink.vue'
import ShortNameRefund from '@/components/pay/eft/ShortNameRefund.vue'
import ShortNameTransactions from '@/components/pay/eft/ShortNameTransactions.vue'
import moment from 'moment'
import { useUserStore } from '@/stores/user'

interface ShortNameDetails {
  shortName: string;
  creditsRemaining?: number;
  linkedAccountsCount: number;
  lastPaymentReceivedDate: Date;
}

export default defineComponent({
  name: 'ShortNameMappingView',
  components: { ShortNameAccountLink, ShortNameTransactions, ShortNameRefund },
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
      highlightIndex: -1,
      snackbar: false,
      snackbarText: '',
      unsettledAmount: '',
      displayRefundAlert: false,
      canEFTRefund: computed((): boolean => currentUser.value?.roles?.includes(Role.EftRefund))
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

    async function onPaymentAction () {
      await loadShortname(props.shortNameId)
      updateState()
    }

    async function loadShortname (shortnameId: string): Promise<void> {
      try {
        const response = await PaymentService.getEFTShortnameSummary(shortnameId)
        if (response?.data) {
          state.shortNameDetails = response.data['items'][0]
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
      formatCurrency: CommonUtils.formatAmount,
      unsettledAmountHeader
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
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
  }
</style>
