
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
import { Action, State } from 'pinia-class'
import { Component, Vue } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import { Address } from '@/models/address'
import GovmContactInfoForm from '@/components/auth/create-account/GovmContactInfoForm.vue'
import GovmPaymentMethodSelector from '@/components/auth/create-account/GovmPaymentMethodSelector.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Pages } from '@/util/constants'
import SelectProductService from '@/components/auth/create-account/SelectProductService.vue'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    SelectProductService,
    AccountCreateBasic,
    GovmPaymentMethodSelector,
    Stepper,
    ModalDialog,
    GovmContactInfoForm
  }
})
export default class GovmAccountSetupView extends Vue {
  // private readonly createOrg!: () => Promise<Organization>
  @Action(useOrgStore) private createGovmOrg!: () => void
  @State(useOrgStore) private currentOrganization!: Organization
  @State(useOrgStore) private currentOrgAddress!: Address
  @Action(useOrgStore) private syncOrganization!: (orgId: number) => Promise<Organization>
  @Action(useOrgStore) private syncMembership!: (orgId: number) => Promise<Member>

  public errorTitle = 'Account creation failed'
  public errorText = ''
  public isLoading: boolean = false

  $refs: {
    errorDialog: InstanceType<typeof ModalDialog>
  }

  public stepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Account Information',
        stepName: 'Account Information',
        component: AccountCreateBasic,
        componentProps: {
          govmAccount: true
        }
      },
      {
        title: 'Products and Services',
        stepName: 'Products and Services',
        component: SelectProductService,
        componentProps: {
          isStepperView: true
        }
      },
      {
        title: 'Payment Information',
        stepName: 'Payment Information',
        component: GovmPaymentMethodSelector,
        componentProps: {
          isStepperView: true
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
  // TODO functionality for create account
  public async createAccount () {
    this.isLoading = true
    try {
      // save or from here
      const organization: any = await this.createGovmOrg() // create govm account
      await this.syncOrganization(organization.id)
      await this.syncMembership(organization.id)
      // Remove with Vue 3
      this.$store.commit('updateHeader')
      this.$router.push(Pages.SETUP_GOVM_ACCOUNT_SUCCESS)
      this.isLoading = false
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
      this.isLoading = false
      switch (err?.response?.status) {
        case 409:
          this.errorText =
                  'An account with this name already exists. Try a different account name.'
          break
        case 400:
          switch (err.response.data?.code) {
            case 'MAX_NUMBER_OF_ORGS_LIMIT':
              this.errorText = 'Maximum number of accounts reached'
              break
            case 'ACTIVE_AFFIDAVIT_EXISTS':
              this.errorText = err.response.data.message || 'Affidavit already exists'
              break
            default:
              this.errorText = 'An error occurred while attempting to create your account.'
          }
          break
        default:
          this.errorText =
                  'An error occurred while attempting to create your account.'
      }
      this.$refs.errorDialog.open()
    }
  }
  public closeError () {
    this.$refs.errorDialog.close()
  }
}
</script>
