<template>
  <div
    id="short-name-linking-dialog"
  >
    <ModalDialog
      ref="accountLinkingDialog"
      max-width="720"
      :show-icon="false"
      :showCloseIcon="true"
      dialog-class="lookup-dialog"
      :title="`Linking ${currentShortName.shortName} to an Account`"
      @close-dialog="resetAccountLinkingDialog"
    >
      <template #text>
        <p>After the account has been linked, payment will be applied at 6:00 p.m. Pacific Time.</p>
        <h4>
          Search by Account ID or Name to Link:
        </h4>
        <ShortNameLookup
          :key="shortNameLookupKey"
          @account="selectedAccount = $event"
          @reset="resetAccountLinkingDialog"
        />
        <div
          v-if="selectedAccount.accountId"
        >
          <h4 class="mb-4">
            Payment Information
          </h4>
          <p class="mb-2 d-flex justify-space-between">
            Unsettled amount from the short name: <span class="font-weight-bold">{{ formatCurrency(currentShortName.creditsRemaining) }}</span>
          </p>
          <p class="d-flex justify-space-between">
            Amount owing on the selected account (Statement #{{ statementId }}):
            <span class="font-weight-bold">{{ formatCurrency(selectedAccount.totalDue) }}</span>
          </p>
        </div>
        <p
          v-if="selectedAccount.accountId && isUnsettledAmountAndOwingAmountMatch()"
          class="py-4 px-6 important"
        >
          <span class="font-weight-bold">Important:</span>
          The unsettled amount from the short name does not match with the amount owing on the account.
          This could result in over or under payment settlement.
          Please make sure you have selected the correct account to link.
        </p>
      </template>
      <template #actions>
        <div class="d-flex align-center justify-center w-100 h-100 ga-3">
          <v-btn
            large
            outlined
            color="outlined"
            data-test="dialog-ok-button"
            @click="cancelAndResetAccountLinkingDialog()"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            color="primary"
            data-test="dialog-ok-button"
            @click="linkAccount()"
          >
            Link Account
          </v-btn>
        </div>
      </template>
    </ModalDialog>
    <ModalDialog
      ref="accountLinkingErrorDialog"
      max-width="720"
      dialog-class="notify-dialog"
      :title="accountLinkingErrorDialogTitle"
      :text="accountLinkingErrorDialogText"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          data-test="dialog-ok-button"
          @click="closeAccountAlreadyLinkedDialog"
        >
          Close
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>
<script lang="ts">
import { Ref, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { EFTShortnameResponse } from '@/models/eft-transaction'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'
import ShortNameLookup from '@/components/pay/ShortNameLookup.vue'
import { ShortNameResponseStatus } from '@/util/constants'
import { useOrgStore } from '@/stores/org'

interface ShortNameLinkingDialog {
  shortNameLookupKey: number
  currentShortName: object
  selectedAccount: object
  accountLinkingErrorDialogTitle: string
  accountLinkingErrorDialogText: string
  totalDue: number
  areAmountsMismatch: boolean
  statementId: number
}

export default defineComponent({
  name: 'UnlinkedShortNameTable',
  components: { ModalDialog, ShortNameLookup },
  props: {
    isShortNameLinkingDialogOpen: {
      type: Boolean,
      default: false
    },
    selectedShortName: {
      default: {}
    }
  },
  emits: ['on-link-account', 'close-short-name-linking-dialog'],
  setup (props, { emit }) {
    const orgStore = useOrgStore()
    const accountLinkingDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const accountLinkingErrorDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const state = reactive<ShortNameLinkingDialog>({
      shortNameLookupKey: 0,
      currentShortName: {},
      selectedAccount: {},
      accountLinkingErrorDialogTitle: '',
      accountLinkingErrorDialogText: '',
      totalDue: 0,
      areAmountsMismatch: false,
      statementId: 0
    })

    function isUnsettledAmountAndOwingAmountMatch () {
      return state.currentShortName?.creditsRemaining !== state.selectedAccount?.totalDue
    }

    function openAccountLinkingDialog (item: EFTShortnameResponse) {
      state.currentShortName = item
      accountLinkingDialog.value.open()
    }

    function resetAccountLinkingDialog () {
      state.selectedAccount = {}
      state.totalDue = 0
      state.statementId = 0
      state.shortNameLookupKey++
      emit('close-short-name-linking-dialog')
    }

    function cancelAndResetAccountLinkingDialog () {
      accountLinkingDialog.value.close()
      resetAccountLinkingDialog()
    }

    function closeAccountAlreadyLinkedDialog () {
      accountLinkingErrorDialog.value.close()
    }

    async function linkAccount () {
      if (!state.currentShortName?.id || !state.selectedAccount?.accountId) {
        return
      }
      try {
        const response = await PaymentService.postShortNameLink(state.currentShortName.id, state.selectedAccount.accountId)
        if (response?.data) {
          emit('on-link-account', response.data)
          cancelAndResetAccountLinkingDialog()
        }
      } catch (error) {
        if (error.response.data.type === ShortNameResponseStatus.EFT_SHORT_NAME_ALREADY_MAPPED) {
          state.accountLinkingErrorDialogTitle = 'Account Already Linked'
          state.accountLinkingErrorDialogText = 'The selected bank short name is already linked to an account.'
          cancelAndResetAccountLinkingDialog()
          accountLinkingErrorDialog.value.open()
        } else {
          state.accountLinkingErrorDialogTitle = 'Something Went Wrong'
          state.accountLinkingErrorDialogText = 'An error occurred while linking the bank short name to an account.'
          cancelAndResetAccountLinkingDialog()
          accountLinkingErrorDialog.value.open()
        }
        console.error('Failed to postShortNameLink.', error)
      }
    }

    const getStatementsList = async (organizationId: string): Promise<any> => {
      const data = await orgStore.getStatementsList({}, organizationId)
      state.statementId = data.items[0].id
    }

    onMounted(async () => {
    })

    watch(() => [state.selectedAccount], ([selectedAccount]) => {
      if (selectedAccount?.accountId) {
        getStatementsList(selectedAccount.accountId)
      }
    })

    watch(() => [props.selectedShortName, props.isShortNameLinkingDialogOpen], ([selectedShortNameNewValue]) => {
      if (props.isShortNameLinkingDialogOpen && selectedShortNameNewValue) {
        openAccountLinkingDialog(selectedShortNameNewValue)
      }
    })

    return {
      ...toRefs(state),
      formatCurrency: CommonUtils.formatAmount,
      accountLinkingDialog,
      accountLinkingErrorDialog,
      openAccountLinkingDialog,
      resetAccountLinkingDialog,
      cancelAndResetAccountLinkingDialog,
      closeAccountAlreadyLinkedDialog,
      linkAccount,
      isUnsettledAmountAndOwingAmountMatch
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';

.actions-dropdown_item {
  cursor: pointer;
  padding: 0.5rem 1rem;
  &:hover {
    background-color: $gray1;
    color: $app-blue !important;
  }
}

h4 {
  color: black;
}

.important {
  background-color: #fff7e3;
  border: 2px solid #fcba19;
  color: #495057;
  font-size: 12px;
}

.w-100 {
  width: 100%;
}

.h-100 {
  height: 100%;
}

.ga-3 {
  gap: 12px;
}

::v-deep {
  .v-btn.v-btn--outlined {
      border-color: var(--v-primary-base);
      color: var(--v-primary-base);
  }
}

</style>
