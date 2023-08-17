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
import { AccessType, DisplayModeValues, LDFlags, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Member, OrgPaymentDetails, Organization, PADInfoValidation } from '@/models/Organization'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import AccountTypeSelector from '@/components/auth/create-account/AccountTypeSelector.vue'
import { Address } from '@/models/address'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentMethodSelector from '@/components/auth/create-account/PaymentMethodSelector.vue'
import PremiumChooser from '@/components/auth/create-account/PremiumChooser.vue'
import SelectProductService from '@/components/auth/create-account/SelectProductService.vue'
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
      'userContact',
      'userProfile'
    ]),
    ...mapState('org', [
      'currentOrgPaymentType',
      'currentOrganization'
    ])

  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationType',
      'setViewOnlyMode'
    ]),
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
        'validatePADInfo',
        'syncMembership',
        'syncOrganization',
        'syncAddress',
        'getOrgPayments'
      ])
  }
})
export default class NonBcscAccountSetupView extends Vue {
  @Prop({ default: undefined }) private readonly orgId: number // org id used for bceid re-uplaod
  private readonly currentUser!: KCUserProfile
  private readonly currentOrgPaymentType!: string
  protected readonly userContact!: Contact
  private readonly createAffidavit!: () => Promise<User>
  private readonly updateUserFirstAndLastName!: (user?: User) => Promise<Contact>
  private readonly createOrg!: () => Promise<Organization>
  private readonly validatePADInfo!: () => Promise<PADInfoValidation>
  private readonly createUserContact!: (contact?: Contact) => Promise<Contact>
  private readonly updateUserContact!: (contact?: Contact) => Promise<Contact>
  private readonly getUserProfile!: (identifer: string) => Promise<User>
  readonly syncOrganization!: (orgId: number) => Promise<Organization>
  readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly syncAddress!: () => Promise<Address>
  private readonly getOrgPayments!: () => Promise<OrgPaymentDetails>
  private readonly setCurrentOrganizationType!: (orgType: string) => void
  private readonly setViewOnlyMode!: (mode: string) => void
  private readonly currentOrganization!: Organization
  private readonly userProfile!: User

  errorTitle = 'Account creation failed'
  errorText = ''
  private isLoading: boolean = false
  private readOnly = false
  private isAffidavitAlreadyApproved = false

  $refs: {
    errorDialog: ModalDialog,
    stepper: HTMLFormElement,
  }

  private accountStepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Select Product and Services',
        stepName: 'Products and Services',
        component: SelectProductService,
        componentProps: {
          isStepperView: true,
          noBackButton: true
        }
      },
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
        title: 'Account Administrator Information',
        stepName: 'Account Administrator Information',
        component: UserProfileForm,
        componentProps: {
          isStepperView: true,
          stepperSource: AccessType.EXTRA_PROVINCIAL
        }
      }
    ]

  private async beforeMount () {
    if (this.enablePaymentMethodSelectorStep) {
      const paymentMethodStep = {
        title: 'Payment Method',
        stepName: 'Payment Method',
        component: PaymentMethodSelector,
        componentProps: {}
      }
      this.accountStepperConfig.push(paymentMethodStep)
      // use the new premium chooser account when flag is enabled
      this.accountStepperConfig[3].alternate.component = PremiumChooser
    }
    // Loading user details if not exist and check user already verified with affidavit
    if (!this.userProfile) {
      await this.getUserProfile('@me')
    }
    this.isAffidavitAlreadyApproved = this.userProfile && this.userProfile?.verified
    // if user affidavit is already approve no need to show upload affidavit stepper
    // so removing it from array
    if (this.isAffidavitAlreadyApproved) {
      this.accountStepperConfig.splice(2, 1)
    }
  }
  private async mounted () {
    // on re-upload need show some pages are in view only mode
    this.readOnly = !!this.orgId
    // this.isAffidavitAlreadyApproved = this.userProfile && this.userProfile.verified
    if (this.orgId) {
      // setting view only mode for all other pages which not need to edit
      this.setViewOnlyMode(DisplayModeValues.VIEW_ONLY)
      this.$refs.stepper.jumpToStep(3)
      const orgId = this.orgId
      await this.syncOrganization(orgId)
      this.syncAddress()
      this.getOrgPayments()

      this.setCurrentOrganizationType(this.currentOrganization.orgType)
      // passing additional props for readonly
      this.accountStepperConfig[4].componentProps = { ...this.accountStepperConfig[4].componentProps, clearForm: true }
      this.accountStepperConfig[0].componentProps = { ...this.accountStepperConfig[0].componentProps, readOnly: true, orgId }

      if (this.enablePaymentMethodSelectorStep) {
        this.accountStepperConfig[3].componentProps = { ...this.accountStepperConfig[3].componentProps, readOnly: true }
        this.accountStepperConfig[5].componentProps = { ...this.accountStepperConfig[5].componentProps, readOnly: true }
      }
    } else {
      this.setViewOnlyMode('')
    }
  }

  private get enablePaymentMethodSelectorStep (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.PaymentTypeAccountCreation) || false
  }

  private async verifyAndCreateAccount () {
    this.isLoading = true
    let isProceedToCreateAccount = false
    if (this.currentOrgPaymentType === PaymentTypes.PAD) {
      // no need to validate for readonly view
      isProceedToCreateAccount = this.readOnly ? true : await this.verifyPAD()
    } else {
      isProceedToCreateAccount = true
    }

    if (isProceedToCreateAccount) {
      this.createAccount()
    }
  }

  private async verifyPAD () {
    const verifyPad: PADInfoValidation = await this.validatePADInfo()
    if (!verifyPad) {
      // proceed to create account even if the response is empty
      return true
    }
    if (verifyPad?.isValid) {
      // create account if PAD info is valid
      return true
    } else {
      this.isLoading = false
      this.errorText = 'Bank information validation failed'
      if (verifyPad?.message?.length) {
        let msgList = ''
        verifyPad.message.forEach((msg) => {
          msgList += `<li>${msg}</li>`
        })
        this.errorText = `<ul style="list-style-type: none;">${msgList}</ul>`
      }
      this.$refs.errorDialog.open()
      return false
    }
  }

  private async createAccount () {
    this.isLoading = true
    try {
      // normal account flow
      if (!this.readOnly) {
        // if user affidavit is already approve no need to make creade affidavit call
        if (!this.isAffidavitAlreadyApproved) {
          await this.createAffidavit()
        }
        await this.updateUserFirstAndLastName()
        const organization = await this.createOrg()
        await this.saveOrUpdateContact()
        await this.getUserProfile('@me')
        await this.syncOrganization(organization.id)
        await this.syncMembership(organization.id)
        // remove GOVN accoutn type from session
        ConfigHelper.removeFromSession(SessionStorageKeys.GOVN_USER)
      } else {
        // re-upload final submission valeus here
        await this.updateUserFirstAndLastName()
        await this.saveOrUpdateContact()
        await this.createAffidavit()
        await this.getUserProfile('@me')
      }

      this.$store.commit('updateHeader')
      const nextRoute = !this.isAffidavitAlreadyApproved ? '/setup-non-bcsc-account-success' : '/setup-account-success'
      this.$router.push(nextRoute)
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
