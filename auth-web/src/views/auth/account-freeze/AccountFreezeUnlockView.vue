<template>
  <v-container class="view-container" v-if="isAccountStatusNsfSuspended">
    <div class="view-header">
      <div class="view-header__icon">
        <v-icon large color="error" class="mt-1 mr-4">mdi-alert-circle-outline</v-icon>
      </div>
      <div>
        <h1 class="view-header__title">
          This account has been temporarily suspended
        </h1>
        <p class="mt-3 mb-0">To unlock your account, please complete the following steps.</p>
      </div>
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
  <v-container class="view-container" v-else>
    <AccountSuspendedView :isAdmin="true"></AccountSuspendedView>
  </v-container>
</template>

<script lang="ts">
import AccountOverview from '@/components/auth/account-freeze/AccountOverview.vue'
import PaymentReview from '@/components/auth/account-freeze/PaymentReview.vue'
import ReviewBankInformation from '@/components/auth/account-freeze/ReviewBankInformation.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { Organization } from '@/models/Organization'
import { Payment } from '@/models/Payment'
import { AccountStatus, Pages } from '@/util/constants'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ConfigHelper from 'sbc-common-components/src/util/config-helper'
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import AccountSuspendedView from './AccountSuspendedView.vue'

@Component({
  components: {
    AccountOverview,
    ReviewBankInformation,
    PaymentReview,
    Stepper,
    ModalDialog,
    AccountSuspendedView
  },
  methods: {
    ...mapActions('org', [
      'createAccountPayment'
    ])
  },
  computed: {
    ...mapState('user', [
      'userContact'
    ]),
    ...mapState('org', [
      'currentOrganization'
    ])

  }
})
export default class AccountFreezeUnlockView extends Vue {
  private readonly currentUser!: KCUserProfile
  private readonly currentOrganization!: Organization
  private readonly createAccountPayment!: () => Payment
  private errorTitle = 'Account unlocking failed'
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
        component: PaymentReview,
        componentProps: {}
      }
    ]

  private async unlockAccount () {
    const payment: Payment = await this.createAccountPayment()
    const returnUrl = `${ConfigHelper.getAuthContextPath()}/${Pages.ACCOUNT_UNLOCK_SUCCESS}`
    const encodedUrl = encodeURIComponent(returnUrl)
    // redirect to make payment UI
    await this.$router.push(`${Pages.MAKE_PAD_PAYMENT}${payment.id}/transactions/${encodedUrl}`)
  }

  private get isAccountStatusNsfSuspended () : boolean {
    return this.currentOrganization.statusCode === AccountStatus.NSF_SUSPENDED
  }
  private closeError () {
    this.$refs.errorDialog.close()
  }
}
</script>
