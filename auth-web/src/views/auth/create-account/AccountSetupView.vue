<template>
  <v-container
    class="view-container"
    data-test="div-account-setup-container"
  >
    <!-- Loading status -->
    <v-fade-transition>
      <div
        v-if="isCurrentUserSettingLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isCurrentUserSettingLoading"
        />
      </div>
    </v-fade-transition>
    <template v-if="!isCurrentUserSettingLoading">
      <div class="view-header flex-column">
        <h1 class="view-header__title">
          {{ $t('createBCRegistriesAccount') }}
        </h1>
        <p class="mt-3 mb-0">
          Create an account to access BC Registries products and services.
        </p>
      </div>
      <v-card flat>
        <Stepper
          :stepper-configuration="stepperConfig"
          :isLoading="isLoading"
          @final-step-action="verifyAndCreateAccount"
        />
      </v-card>
      <!-- Alert Dialog (Error) -->
      <ModalDialog
        ref="errorDialog"
        :title="errorTitle"
        :text="errorText"
        dialog-class="notify-dialog"
        max-width="640"
        data-test="modal-account-setup-error"
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
    </template>
  </v-container>
</template>

<script lang="ts">
import { PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import AccountCreate from '@/components/auth/create-account/AccountCreate.vue'
import ConfigHelper from '@/util/config-helper'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { PADInfoValidation } from '@/models/Organization'
import SelectProductPayment from '@/components/auth/create-account/SelectProductPayment.vue'
import Stepper from '@/components/auth/common/stepper/Stepper.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'AccountSetupView',
  components: {
    Stepper,
    ModalDialog
  },
  props: {
    redirectToUrl: {
      type: String,
      default: ''
    },
    skipConfirmation: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { root }) {
    const errorDialog = ref<InstanceType<typeof ModalDialog>>()
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    const state = reactive({
      errorTitle: 'Account creation failed',
      errorText: '',
      isLoading: false,
      isCurrentUserSettingLoading: false
    })
    const stepperConfig =
    [
      {
        title: 'Account Information',
        stepName: 'Account Information',
        component: AccountCreate,
        componentProps: {}
      },
      {
        title: 'Account Administrator Information',
        stepName: 'Account Administrator Information',
        component: UserProfileForm,
        componentProps: {
          isStepperView: true
        }
      },
      {
        title: 'Select Products and Payment',
        stepName: 'Products and Payment',
        component: SelectProductPayment,
        componentProps: {
          isStepperView: true
        }
      }
    ]

    async function verifyAndCreateAccount () {
      state.isLoading = true
      let isProceedToCreateAccount = false
      if (orgStore.currentOrgPaymentType === PaymentTypes.PAD) {
        isProceedToCreateAccount = await verifyPAD()
      } else {
        isProceedToCreateAccount = true
      }

      if (isProceedToCreateAccount) {
        this.createAccount()
      }
    }

    async function verifyPAD () {
      const verifyPad: PADInfoValidation = await orgStore.validatePADInfo()
      if (!verifyPad) {
      // proceed to create account even if the response is empty
        return true
      }
      if (verifyPad?.isValid) {
      // create account if PAD info is valid
        return true
      } else {
        state.isLoading = false
        state.errorText = 'Bank information validation failed'
        if (verifyPad?.message?.length) {
          let msgList = ''
          verifyPad.message.forEach((msg) => {
            msgList += `<li>${msg}</li>`
          })
          state.errorText = `<ul style="list-style-type: none;">${msgList}</ul>`
        }
        errorDialog.value.open()
        return false
      }
    }

    async function createAccount () {
      state.isLoading = true
      try {
        const organization = await orgStore.createOrg()
        await saveOrUpdateContact()
        await userStore.getUserProfile('@me')
        await orgStore.syncOrganization(organization.id)
        await orgStore.syncMembership(organization.id)
        // remove GOVN account type from session
        ConfigHelper.removeFromSession(SessionStorageKeys.GOVN_USER)
        // Remove with Vue 3
        root.$store.commit('updateHeader')
        root.$router.push('/setup-account-success')
      } catch (err) {
      // eslint-disable-next-line no-console
        console.error(err)
        state.isLoading = false
        switch (err?.response?.status) {
          case 409:
            state.errorText =
                  'An account with this name already exists. Try a different account name.'
            break
          case 400:
            switch (err.response.data?.code) {
              case 'MAX_NUMBER_OF_ORGS_LIMIT':
                state.errorText = 'Maximum number of accounts reached'
                break
              case 'ACTIVE_AFFIDAVIT_EXISTS':
                state.errorText = err.response.data.message || 'Affidavit already exists'
                break
              default:
                state.errorText = 'An error occurred while attempting to create your account.'
            }
            break
          default:
            state.errorText =
                  'An error occurred while attempting to create your account.'
        }
        errorDialog.value.open()
      }
    }

    async function saveOrUpdateContact () {
      if (userStore.userContact) {
        await userStore.updateUserContact()
      } else {
        await userStore.createUserContact()
      }
    }

    function closeError () {
      errorDialog.value.close()
    }

    onMounted(() => {
      useOrgStore().resetOrgInfoForCreateAccount()
    })

    return {
      ...toRefs(state),
      stepperConfig,
      verifyAndCreateAccount,
      createAccount,
      closeError
    }
  }
})
</script>
