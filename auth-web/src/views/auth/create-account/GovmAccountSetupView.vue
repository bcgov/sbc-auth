
<template>
  <v-container
    class="view-container"
    data-test="div-account-setup-container"
  >
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Create a Ministry Account
      </h1>
      <p class="mt-3 mb-0">
        Create an account to access products and services offered by BC Registries and Online Services
      </p>
    </div>
    <v-card flat>
      <Stepper
        :stepper-configuration="stepperConfig"
        :isLoading="isLoading"
        @final-step-action="createAccount"
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
  </v-container>
</template>

<script lang="ts">
import { AccessType, Pages } from '@/util/constants'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import AccountCreate from '@/components/auth/create-account/AccountCreate.vue'
import GovmContactInfoForm from '@/components/auth/create-account/GovmContactInfoForm.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import SelectProductPayment from '@/components/auth/create-account/SelectProductPayment.vue'
import { useAccountCreate } from '@/composables/account-create-factory'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'GovmAccountSetupView',
  components: {
    Stepper,
    ModalDialog
  },
  setup (props, { root }) {
    const { createGovmOrg, syncOrganization, syncMembership } = useOrgStore()
    const state = reactive({
      isLoading: false,
      errorTitle: 'Account creation failed',
      errorText: ''
    })
    const errorDialog = ref<InstanceType<typeof ModalDialog>>()
    const stepperConfig: Array<StepConfiguration> = [
      {
        title: 'Account Information',
        stepName: 'Account Information',
        component: AccountCreate,
        componentProps: {
          govmAccount: true,
          readOnly: true
        }
      },
      {
        title: 'Select Products and Payment',
        stepName: 'Products and Payment',
        component: SelectProductPayment,
        componentProps: {
          isStepperView: true,
          govmAccount: true
        }
      },
      {
        title: 'Contact Information',
        stepName: 'Contact Information',
        component: GovmContactInfoForm,
        componentProps: {
          isStepperView: true
        }
      }
    ]

    useOrgStore().setAccessType(AccessType.GOVM)

    async function createAccount () {
      this.isLoading = true
      try {
        // save or from here
        const organization: any = await createGovmOrg() // create govm account
        await syncOrganization(organization.id)
        await syncMembership(organization.id)
        // Remove with Vue 3
        root.$store.commit('updateHeader')
        root.$router.push(Pages.SETUP_GOVM_ACCOUNT_SUCCESS)
        state.isLoading = false
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error(err)
        state.isLoading = false
        useAccountCreate().handleCreateAccountError(state, err)
        errorDialog.value.open()
      }
    }

    function closeError () {
      errorDialog.value.close()
    }

    return {
      ...toRefs(state),
      stepperConfig,
      createAccount,
      closeError
    }
  }
})
</script>
