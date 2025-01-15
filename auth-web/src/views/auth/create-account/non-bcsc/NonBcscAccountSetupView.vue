<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        {{ $t('createBCRegistriesAccount') }}
      </h1>
      <p class="mt-3 mb-0">
        Manage account settings, team members, and view account transactions
      </p>
    </div>
    <v-card flat>
      <Stepper
        ref="stepper"
        :stepper-configuration="accountStepperConfig"
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
import { AccessType, DisplayModeValues, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { defineComponent, onBeforeMount, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import AccountCreate from '@/components/auth/create-account/AccountCreate.vue'
import ConfigHelper from '@/util/config-helper'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { PADInfoValidation } from '@/models/Organization'
import SelectProductPayment from '@/components/auth/create-account/SelectProductPayment.vue'
import Stepper from '@/components/auth/common/stepper/Stepper.vue'
import UploadAffidavitStep from '@/components/auth/create-account/non-bcsc/UploadAffidavitStep.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'NonBcscAccountSetupView',
  components: {
    Stepper,
    ModalDialog
  },
  props: {
    orgId: {
      type: Number,
      default: undefined
    }
  },
  setup (props, { root }) {
    const errorDialog = ref<InstanceType<typeof ModalDialog>>()
    const stepper = ref<HTMLFormElement>()
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    const state = reactive({
      errorTitle: 'Account creation failed',
      errorText: '',
      isLoading: false,
      readOnly: false,
      isAffidavitAlreadyApproved: false
    })
    const accountStepperConfig =
      [
        {
          title: 'Upload your notarized affidavit',
          stepName: 'Upload Affidavit',
          component: UploadAffidavitStep,
          componentProps: {}
        },
        {
          title: 'Account Information',
          stepName: 'Account Information',
          component: AccountCreate,
          componentProps: {}
        },
        {
          title: 'Select Products and Services',
          stepName: 'Products and Payment',
          component: SelectProductPayment,
          componentProps: {
            isStepperView: true
          }
        },
        {
          title: 'Account Administrator Information',
          stepName: 'Account Administrator Information',
          component: UserProfileForm,
          componentProps: {
            isStepperView: true,
            stepperSource: AccessType.EXTRA_PROVINCIAL
          }
        }
      ]

    onBeforeMount(async () => {
    // Loading user details if not exist and check user already verified with affidavit
      if (!userStore.userProfile) {
        await userStore.getUserProfile('@me')
      }
      state.isAffidavitAlreadyApproved = userStore.userProfile && userStore.userProfile?.verified
      // if user affidavit is already approve no need to show upload affidavit stepper
      // so removing it from array
      if (state.isAffidavitAlreadyApproved) {
        accountStepperConfig.splice(0, 1)
      }
    })

    onMounted(async () => {
      useOrgStore().resetOrgInfoForCreateAccount()
      // on re-upload need show some pages are in view only mode
      state.readOnly = !!props.orgId
      if (props.orgId) {
        // setting view only mode for all other pages which not need to edit
        orgStore.setViewOnlyMode(DisplayModeValues.VIEW_ONLY)
        stepper.value.jumpToStep(3)
        const orgId = props.orgId
        await orgStore.syncOrganization(orgId)
        orgStore.syncAddress()
        orgStore.getOrgPayments()
        orgStore.setCurrentOrganizationType(orgStore.currentOrganization.orgType)
        // passing additional props for readonly
        accountStepperConfig[3].componentProps = { ...accountStepperConfig[4].componentProps, clearForm: true }
        accountStepperConfig[2].componentProps = { ...accountStepperConfig[2].componentProps, readOnly: true, orgId }
        accountStepperConfig[1].componentProps = { ...accountStepperConfig[1].componentProps, readOnly: true }
      } else {
        orgStore.setViewOnlyMode('')
      }
    })

    async function verifyAndCreateAccount () {
      state.isLoading = true
      let isProceedToCreateAccount = false
      if (orgStore.currentOrgPaymentType === PaymentTypes.PAD) {
        // no need to validate for readonly view
        isProceedToCreateAccount = state.readOnly ? true : await verifyPAD()
      } else {
        isProceedToCreateAccount = true
      }

      if (isProceedToCreateAccount) {
        createAccount()
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
        // normal account flow
        if (!state.readOnly) {
          // if user affidavit is already approve no need to make creade affidavit call
          if (!state.isAffidavitAlreadyApproved) {
            await userStore.createAffidavit()
          }
          await userStore.updateUserFirstAndLastName()
          const organization = await orgStore.createOrg()
          await saveOrUpdateContact()
          await userStore.getUserProfile('@me')
          await orgStore.syncOrganization(organization.id)
          await orgStore.syncMembership(organization.id)
          // remove GOVN account type from session
          ConfigHelper.removeFromSession(SessionStorageKeys.GOVN_USER)
        } else {
          // re-upload final submission values
          await userStore.updateUserFirstAndLastName()
          await saveOrUpdateContact()
          await userStore.createAffidavit()
          await userStore.getUserProfile('@me')
        }

        // Remove with Vue 3
        root.$store.commit('updateHeader')
        const nextRoute = !state.isAffidavitAlreadyApproved ? '/setup-non-bcsc-account-success' : '/setup-account-success'
        root.$router.push(nextRoute)
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

    function closeError () {
      errorDialog.value.close()
    }

    async function saveOrUpdateContact () {
      if (userStore.userContact) {
        await userStore.updateUserContact()
      } else {
        await userStore.createUserContact()
      }
    }
    return {
      ...toRefs(state),
      accountStepperConfig,
      errorDialog,
      stepper,
      verifyAndCreateAccount,
      closeError
    }
  }
})
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
