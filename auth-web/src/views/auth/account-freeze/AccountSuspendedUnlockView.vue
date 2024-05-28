<template>
  <v-container
    v-if="!isAccountEFTSuspended"
    class="view-container"
  >
    <div class="view-header">
      <div>
        <h1 class="view-header__title">
          Your Account is Suspended
        </h1>
        <p class="mt-3 mb-0 py-4 px-6 important">
          <v-icon
            color="red"
            class="pr-1"
            small
          >
            mdi-alert
          </v-icon>
          <span class="font-weight-bold">Important: </span>
          Your account has been suspended due to overdue payments. Please complete the following steps to reactivate your account.
        </p>
      </div>
    </div>
    <v-card flat>
      <Stepper
        ref="stepper"
        :stepper-configuration="stepperConfig"
        :isLoading="isLoading"
        redirectWhenDone="/account-hold"
        @final-step-action="unlockAccount"
        @step-forward="handleStepForward"
        @step-back="handleStepBack"
      />
    </v-card>

    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="640"
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
          color="error"
          class="font-weight-bold"
          @click="closeError"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </v-container>
  <v-container
    v-else
    class="view-container"
  >
    <AccountSuspendedView :isAdmin="true" />
  </v-container>
</template>

<script lang="ts">
import { AccountStatus, Pages } from '@/util/constants'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { defineComponent, ref } from '@vue/composition-api'
import AccountOverview from '@/components/auth/account-freeze/AccountOverview.vue'
import AccountSuspendedView from './AccountSuspendedView.vue'
import ConfigHelper from 'sbc-common-components/src/util/config-helper'
import MakePayment from '@/components/auth/account-freeze/MakePayment.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { storeToRefs } from 'pinia'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'AccountSuspendedUnlockView',
  components: {
    // eslint-disable-next-line vue/no-unused-components
    AccountOverview,
    // eslint-disable-next-line vue/no-unused-components
    MakePayment,
    Stepper,
    ModalDialog,
    AccountSuspendedView
  },
  setup (props, { root }) {
    const { userContact: currentUser } = storeToRefs(useUserStore())
    const { createAccountPayment } = useOrgStore()
    const { currentOrganization } = storeToRefs(useOrgStore())
    const errorTitle = 'Account unlocking failed'
    const errorText = ''
    const isLoading = ref(false)
    const errorDialog = ref(null)
    const stepper = ref(null)
    const stepperConfig: StepConfiguration[] = [
      {
        title: 'Account Overview',
        stepName: 'Account Overview',
        component: AccountOverview,
        componentProps: {}
      },
      {
        title: 'Make a Payment',
        stepName: 'Make a Payment',
        component: MakePayment,
        componentProps: {}
      }
    ]

    const unlockAccount = async () => {
      isLoading.value = true
      const payment = await createAccountPayment()
      const returnUrl = `${ConfigHelper.getAuthContextPath()}/${Pages.ACCOUNT_UNLOCK_SUCCESS}`
      const encodedUrl = encodeURIComponent(returnUrl)
      // redirect to make payment UI
      await root.$router.push(`${Pages.MAKE_PAD_PAYMENT}${payment.id}/transactions/${encodedUrl}`)
    }

    const isAccountEFTSuspended = currentOrganization.statusCode === AccountStatus.NSF_SUSPENDED

    const closeError = () => {
      errorDialog.value.close()
    }

    const handleStepForward = () => {
      stepper.value.stepForward()
    }

    const handleStepBack = () => {
      stepper.value.stepBack()
    }

    return {
      currentUser,
      currentOrganization,
      createAccountPayment,
      errorTitle,
      errorText,
      isLoading,
      errorDialog,
      stepper,
      stepperConfig,
      unlockAccount,
      isAccountEFTSuspended,
      closeError,
      handleStepForward,
      handleStepBack
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
// @import '@/assets/scss/actions.scss';
// @import '@/assets/scss/ShortnameTables.scss';

.important {
  background-color: #fae9e9;
  border: 2px solid #d3272c;
  color: #495057;
  font-size: 12px;
}

</style>
