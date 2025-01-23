<template>
  <v-container
    v-if="isAccountStatusNsfSuspended && hasEFTPaymentMethod && !isViewLoading"
    class="view-container"
  >
    <div class="view-header">
      <div>
        <h1 class="view-header__title">
          Your Account is Suspended
        </h1>
        <p class="mt-3 mb-0 py-6 px-6 important">
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
        redirectWhenDone="/"
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
    v-else-if="isAccountStatusNsfSuspended && !isViewLoading"
    class="view-container"
  >
    <div class="view-header">
      <div class="w-100">
        <h1 class="view-header__title">
          Your Account is Suspended
        </h1>
        <p class="mt-3 mb-0 py-6 px-6 important">
          <v-icon
            color="red"
            class="pr-1"
            small
          >
            mdi-alert
          </v-icon>
          <span class="font-weight-bold">Important: </span>
          Please complete the following steps to complete your payment.
        </p>
      </div>
    </div>
    <v-card flat>
      <Stepper
        ref="stepper"
        :stepper-configuration="stepperConfig"
        :isLoading="isLoading"
        @final-step-action="unlockAccount"
        @step-forward="handleStepForward"
      />
    </v-card>

    <!-- Alert Dialog (Error) -->
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
</template>

<script lang="ts">
import { AccountStatus, Pages, PaymentTypes } from '@/util/constants'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import AccountOverview from '@/components/auth/account-freeze/AccountOverview.vue'
import AccountOverviewNSF from '@/components/auth/account-freeze/AccountOverviewNSF.vue'
import ConfigHelper from 'sbc-common-components/src/util/config-helper'
import MakePayment from '@/components/auth/account-freeze/MakePayment.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { OrgPaymentDetails } from '@/models/Organization'
import PaymentReview from '@/components/auth/account-freeze/PaymentReview.vue'
import ReviewBankInformation from '@/components/auth/account-freeze/ReviewBankInformation.vue'
import { storeToRefs } from 'pinia'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountFreezeUnlockView',
  components: {
    // eslint-disable-next-line vue/no-unused-components
    AccountOverviewNSF,
    // eslint-disable-next-line vue/no-unused-components
    ReviewBankInformation,
    // eslint-disable-next-line vue/no-unused-components
    PaymentReview,
    // eslint-disable-next-line vue/no-unused-components
    AccountOverview,
    // eslint-disable-next-line vue/no-unused-components
    MakePayment,
    Stepper,
    ModalDialog
  },
  setup (props, { root }) {
    const orgStore = useOrgStore()
    const { createAccountPayment, createOutstandingAccountPayment, getOrgPayments } = orgStore
    const { currentOrganization } = storeToRefs(orgStore)
    const errorDialog = ref(null)
    const stepper = ref(null)

    const state = reactive<{
      errorTitle: string;
      errorText: string;
      isLoading: boolean;
      hasEFTPaymentMethod: boolean;
      isViewLoading: boolean;
      stepperConfig: StepConfiguration[];
      isAccountStatusNsfSuspended: boolean;
    }>({
      errorTitle: 'Account unlocking failed',
      errorText: '',
      isLoading: false,
      hasEFTPaymentMethod: false,
      isViewLoading: true,
      stepperConfig: [],
      isAccountStatusNsfSuspended: false
    })

    async function unlockAccount (alternateFlow: string) {
      if (state.isLoading) {
        return
      }

      if (alternateFlow === 'eft-payment-instructions') {
        await root.$router.push(`${Pages.ACCOUNT_HOLD}`)
        return
      }
      state.isLoading = true
      let payment
      try {
        if (state.hasEFTPaymentMethod) {
          payment = await createOutstandingAccountPayment()
        } else {
          payment = await createAccountPayment()
        }
      } catch (error) {
        console.log(error)
      } finally {
        state.isLoading = false
      }

      const baseUrl = ConfigHelper.getAuthContextPath()
      const returnUrl = `${baseUrl}/${Pages.ACCOUNT_UNLOCK_SUCCESS}`
      const encodedUrl = encodeURIComponent(returnUrl)
      // redirect to make payment UI
      await root.$router.push(`${Pages.MAKE_CC_PAYMENT}${payment.id}/transactions/${encodedUrl}`)
    }

    async function checkPaymentMethods () {
      try {
        const orgPayments: OrgPaymentDetails = await getOrgPayments()
        const paymentMethod = orgPayments.paymentMethod === PaymentTypes.EFT
        state.hasEFTPaymentMethod = paymentMethod
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    }

    function closeError () {
      errorDialog.value.close()
    }

    function handleStepForward () {
      stepper.value.stepForward()
    }

    function handleStepBack () {
      stepper.value.stepBack()
    }

    // Check on a polling basis if our account is unlocked, if it's unlocked redirect to account unlocked.
    async function pollForAccountUnlock (tries = 0) {
      tries++
      if (tries >= 5) {
        return
      }
      await orgStore.syncOrganization(currentOrganization.value?.id)
      if ([AccountStatus.NSF_SUSPENDED, AccountStatus.SUSPENDED]
        .includes(currentOrganization.value.statusCode as AccountStatus)) {
        setTimeout(async () => {
          await pollForAccountUnlock(tries)
        }, 2000)
      } else {
        await root.$router.push(`${Pages.ACCOUNT_UNLOCK_SUCCESS}`)
      }
    }

    onMounted(async () => {
      state.isAccountStatusNsfSuspended = currentOrganization.value.statusCode === AccountStatus.NSF_SUSPENDED
      await checkPaymentMethods()
      if (state.hasEFTPaymentMethod) {
        state.stepperConfig = [
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
      } else {
        state.stepperConfig = [
          {
            title: 'Account Overview',
            stepName: 'Account Overview',
            component: AccountOverviewNSF,
            componentProps: {}
          },
          {
            title: 'Review Information',
            stepName: 'Review Information',
            component: ReviewBankInformation,
            componentProps: {}
          },
          {
            title: 'Payment & Review',
            stepName: 'Payment & Review',
            component: PaymentReview,
            componentProps: {}
          }
        ]
      }
      state.isViewLoading = false
      setTimeout(async () => {
        await pollForAccountUnlock(0)
      }, 2000)
    })

    return {
      ...toRefs(state),
      stepper,
      unlockAccount,
      closeError,
      handleStepForward,
      handleStepBack,
      currentOrganization,
      errorDialog
    }
  }
})
</script>

<style lang="scss" scoped>
.important {
  background-color: #fae9e9;
  border: 1.5px solid #d3272c;
  color: #495057;
  font-size: 14px;
}

.w-100 {
  width: 100%;
}

</style>
