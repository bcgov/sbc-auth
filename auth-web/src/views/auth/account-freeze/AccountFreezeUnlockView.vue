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
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { mapActions, mapState } from 'vuex'
import AccountOverview from '@/components/auth/account-freeze/AccountOverview.vue'
import ConfigHelper from 'sbc-common-components/src/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { Pages } from '@/util/constants'
import { Payment } from '@/models/Payment'
import PaymentReview from '@/components/auth/account-freeze/PaymentReview.vue'
import ReviewBankInformation from '@/components/auth/account-freeze/ReviewBankInformation.vue'

@Component({
  components: {
    AccountOverview,
    ReviewBankInformation,
    PaymentReview,
    Stepper,
    ModalDialog
  },
  methods: {
    ...mapActions('org', [
      'createAccountPayment'
    ])
  },
  computed: {
    ...mapState('user', [
      'userContact'
    ])
  }
})
export default class AccountFreezeUnlockView extends Vue {
  private readonly currentUser!: KCUserProfile
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
    const payment:Payment = await this.createAccountPayment()
    const returnUrl = `${ConfigHelper.getAuthContextPath()}/${Pages.MAIN}/${this.currentOrganization.id}/${Pages.ACCOUNT_SETTINGS}?tryOrgRefresh=true`
    const encodedUrl = encodeURIComponent(returnUrl)
    // redirect to make payment UI
    await this.$router.push(`${Pages.MAKE_PAD_PAYMENT}${payment.id}/transactions/${encodedUrl}`)
  }

  private closeError () {
    this.$refs.errorDialog.close()
  }
}
</script>
