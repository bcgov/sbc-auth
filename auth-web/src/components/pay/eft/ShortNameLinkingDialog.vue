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
        <p
          v-if="selectedAccount.accountId"
          class="py-4 px-6 important"
        >
          <span class="font-weight-bold">Important:</span> Once an account is linked, all payment received
          from the same short name will be applied to settle outstanding balances of
          the selected account.
        </p>
        <h4>
          Search by Account ID or Name to Link:
        </h4>
        <ShortNameLookup
          :key="shortNameLookupKey"
          @account="selectedAccount = $event"
          @reset="resetAccountLinkingDialog"
        />
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
            Link to an Account and Settle Payment
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
import { EFTShortnameResponse } from '@/models/eft-transaction'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'
import ShortNameLookup from '@/components/pay/ShortNameLookup.vue'
import { ShortNameResponseStatus } from '@/util/constants'

interface ShortNameLinkingDialog {
  shortNameLookupKey: number
  currentShortName: object
  selectedAccount: object
  accountLinkingErrorDialogTitle: string
  accountLinkingErrorDialogText: string
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
    const accountLinkingDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const accountLinkingErrorDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const state = reactive<ShortNameLinkingDialog>({
      shortNameLookupKey: 0,
      currentShortName: {},
      selectedAccount: {},
      accountLinkingErrorDialogTitle: '',
      accountLinkingErrorDialogText: ''
    })

    function openAccountLinkingDialog (item: EFTShortnameResponse) {
      state.currentShortName = item
      accountLinkingDialog.value.open()
    }

    function resetAccountLinkingDialog () {
      state.selectedAccount = {}
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
        const response = await PaymentService.patchEFTShortname(state.currentShortName.id, state.selectedAccount.accountId)
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
        console.error('Failed to patchEFTShortname.', error)
      }
    }

    onMounted(async () => {
    })

    watch(() => [props.selectedShortName, props.isShortNameLinkingDialogOpen],
      () => {
        if (props.isShortNameLinkingDialogOpen && props.selectedShortName) {
          openAccountLinkingDialog(props.selectedShortName)
        }
      }
    )

    return {
      ...toRefs(state),
      accountLinkingDialog,
      accountLinkingErrorDialog,
      openAccountLinkingDialog,
      resetAccountLinkingDialog,
      cancelAndResetAccountLinkingDialog,
      closeAccountAlreadyLinkedDialog,
      linkAccount
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
