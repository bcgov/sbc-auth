<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">{{$t('createBCRegistriesAccount')}}</h1>
      <p class="mt-3 mb-0">Manage account settings, team members, and view account transactions</p>
    </div>
    <v-card flat>
      <Stepper
        :stepper-configuration="accountStepperConfig"
        @final-step-action="createAccount"
      ></Stepper>
    </v-card>
    <!-- Alert Dialog (Error) -->
    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
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
import { AccessType, LDFlags } from '@/util/constants'
import { Component, Vue } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { mapActions, mapState } from 'vuex'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import AccountTypeSelector from '@/components/auth/create-account/AccountTypeSelector.vue'
import { Contact } from '@/models/contact'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentMethodSelector from '@/components/auth/create-account/PaymentMethodSelector.vue'
import PremiumChooser from '@/components/auth/create-account/PremiumChooser.vue'
import UploadAffidavitStep from '@/components/auth/create-account/non-bcsc/UploadAffidavitStep.vue'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'

@Component({
  components: {
    CreateAccountInfoForm,
    UserProfileForm,
    AccountTypeSelector,
    AccountCreateBasic,
    AccountCreatePremium,
    PaymentMethodSelector,
    Stepper,
    ModalDialog,
    PremiumChooser
  },
  computed: {
    ...mapState('user', [
      'userContact'
    ])
  },
  methods: {
    ...mapActions('user',
      [
        'createUserContact',
        'updateUserContact',
        'getUserProfile',
        'createAffidavit',
        'updateUserFirstAndLastName'
      ]),
    ...mapActions('org',
      [
        'createOrg',
        'syncMembership',
        'syncOrganization'
      ])
  }
})
export default class NonBcscAccountSetupView extends Vue {
  private readonly currentUser!: KCUserProfile
  protected readonly userContact!: Contact
  private readonly createAffidavit!: () => User
  private readonly updateUserFirstAndLastName!: (user?: User) => Contact
  private readonly createOrg!: () => Promise<Organization>
  private readonly createUserContact!: (contact?: Contact) => Contact
  private readonly updateUserContact!: (contact?: Contact) => Contact
  private readonly getUserProfile!: (identifer: string) => User
  readonly syncOrganization!: (orgId: number) => Promise<Organization>
  readonly syncMembership!: (orgId: number) => Promise<Member>
  private errorTitle = 'Account creation failed'
  private errorText = ''

  $refs: {
    errorDialog: ModalDialog
  }

  private accountStepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Select Account Type',
        stepName: 'Select Account Type',
        component: AccountTypeSelector,
        componentProps: {}
      },
      {
        title: 'Upload your notarized affidavit',
        stepName: 'Upload Affidavit',
        component: UploadAffidavitStep,
        componentProps: {}
      },
      {
        title: 'Account Information',
        stepName: 'Account Information',
        component: AccountCreateBasic,
        componentProps: {},
        alternate: {
          title: 'Account Information',
          stepName: 'Account Information',
          component: AccountCreatePremium,
          componentProps: {}
        }
      },
      {
        title: 'User Profile',
        stepName: 'User Profile',
        component: UserProfileForm,
        componentProps: {
          isStepperView: true,
          stepperSource: AccessType.EXTRA_PROVINCIAL
        }
      }
    ]

  private beforeMount () {
    if (this.enablePaymentMethodSelectorStep) {
      const paymentMethodStep = {
        title: 'Payment Method',
        stepName: 'Payment Method',
        component: PaymentMethodSelector,
        componentProps: {}
      }
      this.accountStepperConfig.push(paymentMethodStep)
      // use the new premium chooser account when flag is enabled
      this.accountStepperConfig[2].alternate.component = PremiumChooser
    }
  }

  private get enablePaymentMethodSelectorStep (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.PaymentTypeAccountCreation) || false
  }

  private async createAccount () {
    try {
      await this.createAffidavit()
      await this.updateUserFirstAndLastName()
      const organization = await this.createOrg()
      await this.saveOrUpdateContact()
      await this.getUserProfile('@me')
      await this.syncOrganization(organization.id)
      await this.syncMembership(organization.id)
      this.$store.commit('updateHeader')
      this.$router.push('/setup-non-bcsc-account-success')
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error(err)
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

  private closeError () {
    this.$refs.errorDialog.close()
  }

  private async saveOrUpdateContact () {
    if (this.userContact) {
      await this.updateUserContact()
    } else {
      await this.createUserContact()
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
