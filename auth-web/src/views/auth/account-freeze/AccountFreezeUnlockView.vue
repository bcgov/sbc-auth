<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        <v-icon color="error">mdi-alert</v-icon>
        Your account is Temporarily Suspended</h1>
      <p class="mt-3 mb-0">Account has been suspended due to non-sufficient funds (NSF).</p>
    </div>
    <v-card flat>
      <Stepper
        :stepper-configuration="stepperConfig"
        :isLoading="isLoading"
        :stepperColor="'error'"
        @final-step-action="unlockAccount"
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
import { Component, Vue } from 'vue-property-decorator'
import { LDFlags, LoginSource, PaymentTypes } from '@/util/constants'
import { Member, Organization, PADInfoValidation } from '@/models/Organization'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { mapActions, mapState } from 'vuex'
import AccountOverview from '@/components/auth/account-freeze/AccountOverview.vue'
import { Contact } from '@/models/contact'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import PaymentMethodSelector from '@/components/auth/create-account/PaymentMethodSelector.vue'
import PremiumChooser from '@/components/auth/create-account/PremiumChooser.vue'
import ReviewBankInformation from '@/components/auth/account-freeze/ReviewBankInformation.vue'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'

@Component({
  components: {
    CreateAccountInfoForm,
    UserProfileForm,
    AccountOverview,
    ReviewBankInformation,
    PaymentMethodSelector,
    Stepper,
    ModalDialog,
    PremiumChooser
  },
  computed: {
    ...mapState('user', [
      'userContact'
    ]),
    ...mapState('org', [
      'currentOrgPaymentType'
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
        'validatePADInfo',
        'syncMembership',
        'syncOrganization'
      ])
  }
})
export default class AccountFreezeUnlockView extends Vue {
  private readonly currentUser!: KCUserProfile
  private readonly currentOrgPaymentType!: string
  protected readonly userContact!: Contact
  private readonly createOrg!: () => Promise<Organization>
  private readonly validatePADInfo!: () => Promise<PADInfoValidation>
  private readonly createUserContact!: (contact?: Contact) => Contact
  private readonly updateUserContact!: (contact?: Contact) => Contact
  private readonly getUserProfile!: (identifer: string) => User
  readonly syncOrganization!: (orgId: number) => Promise<Organization>
  readonly syncMembership!: (orgId: number) => Promise<Member>
  private errorTitle = 'Account creation failed'
  private errorText = ''
  private isLoading: boolean = false

  $refs: {
    errorDialog: ModalDialog
  }

  private stepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Account Overview',
        stepName: 'Account Overview',
        component: AccountOverview,
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
        component: UserProfileForm,
        componentProps: {}
      }
    ]

  private async unlockAccount () {
  }

  private closeError () {
    this.$refs.errorDialog.close()
  }
}
</script>
