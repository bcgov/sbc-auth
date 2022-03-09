<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-6">
      <h2 class="view-header__title" data-test="account-settings-title">
        Payment Methods
      </h2>
      <p class="mt-3 payment-page-sub">
        Manage your payment method for this account.
      </p>
    </div>
    <PaymentMethods
      v-if="selectedPaymentMethod"
      :currentOrgType="savedOrganizationType"
      :currentOrganization="currentOrganization"
      :currentSelectedPaymentMethod="selectedPaymentMethod"
      :isChangeView="true"
      :isAcknowledgeNeeded="isAcknowledgeNeeded"
      @payment-method-selected="setSelectedPayment"
      @get-PAD-info="getPADInfo"
      @emit-bcol-info="getBcolInfo"
      @is-pad-valid="isPADValid"
      isTouchedUpdate="true"
      :isInitialTOSAccepted="isTOSandAcknowledgeCompleted"
      :isInitialAcknowledged="isTOSandAcknowledgeCompleted"
    ></PaymentMethods>
    <v-slide-y-transition>
      <div class="pb-2" v-show="errorMessage">
        <v-alert type="error" icon="mdi-alert-circle-outline" data-test="alert-bcol-error">
          {{errorMessage}}
        </v-alert>
      </div>
    </v-slide-y-transition>
    <v-divider class="my-10"></v-divider>
    <div class="form__btns d-flex">
      <v-btn
        large
        class="save-btn"
        v-bind:class="{ 'disabled': isBtnSaved }"
        :color="isBtnSaved ? 'success' : 'primary'"
        :disabled="isDisableSaveBtn"
        v-can:CHANGE_PAYMENT_METHOD.disable
        @click="save"
        :loading="isLoading"
      >
        <v-expand-x-transition>
          <v-icon v-show="isBtnSaved">mdi-check</v-icon>
        </v-expand-x-transition>
        <span class="save-btn__label">{{ (isBtnSaved) ? 'Saved' : 'Save' }}</span>
      </v-btn>
      <v-btn
        large
        depressed
        @click="cancel"
        data-test="cancel-button"
        class="cancel-button ml-2"
      > Cancel
      </v-btn>
    </div>
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
          color="primary"
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
import { AccessType, Account, LoginSource, Pages, PaymentTypes, Permission } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, MembershipType, OrgPaymentDetails, Organization, PADInfo, PADInfoValidation } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { Address } from '@/models/address'
import { BcolProfile } from '@/models/bcol'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'

@Component({
  components: {
    PaymentMethods,
    ModalDialog
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentOrgPaymentType',
      'currentMembership',
      'permissions',
      'currentOrgAddress'
    ]),
    ...mapState('user', ['currentUser'])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationPaymentType'
    ]),
    ...mapActions('org', [
      'validatePADInfo',
      'getOrgPayments',
      'updateOrg',
      'syncAddress'
    ])
  }
})
export default class AccountPaymentMethods extends Mixins(AccountChangeMixin) {
  private readonly setCurrentOrganizationPaymentType!: (paymentType: string) => void
  private readonly getOrgPayments!: () => any
  private readonly updateOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly currentOrgPaymentType!: string
  private readonly validatePADInfo!: () => Promise<PADInfoValidation>
  private readonly permissions!: string[]
  private readonly currentUser!: KCUserProfile
  private readonly currentOrgAddress!: Address
  private readonly syncAddress!: () => Address
  private savedOrganizationType: string = ''
  private selectedPaymentMethod: string = ''
  private padInfo: PADInfo = {} as PADInfo
  private isBtnSaved = false
  private disableSaveBtn = false
  private errorMessage: string = ''
  private errorTitle = 'Payment Update Failed'
  private bcolInfo: BcolProfile = {} as BcolProfile
  private errorText = ''
  private isLoading: boolean = false
  private padValid: boolean = false
  private paymentMethodChanged:boolean = false
  private isFuturePaymentMethodAvailable: boolean = false // set true if in between 3 days cooling period
  private isTOSandAcknowledgeCompleted:boolean = false // sert true if TOS already accepted

  $refs: {
      errorDialog: ModalDialog
    }

  private setSelectedPayment (payment) {
    this.errorMessage = ''
    this.selectedPaymentMethod = payment.selectedPaymentMethod
    this.isBtnSaved = (this.isBtnSaved && !payment.isTouched) || false
    this.paymentMethodChanged = payment.isTouched || false
  }

  private get isDisableSaveBtn () {
    let disableSaveBtn = false

    if (this.isBtnSaved) {
      disableSaveBtn = false
    } else if ((this.selectedPaymentMethod === PaymentTypes.PAD && !this.padValid) || (!this.paymentMethodChanged) || (this.selectedPaymentMethod === PaymentTypes.EJV)) {
      disableSaveBtn = true
    }

    return disableSaveBtn
  }

  private getPADInfo (padInfo: PADInfo) {
    this.padInfo = padInfo
  }

  private isPADValid (isValid) {
    this.padValid = isValid
  }

  private async mounted () {
    this.setAccountChangedHandler(await this.initialize)
    await this.initialize()
  }

  private get isAcknowledgeNeeded () {
    // isAcknowledgeNeeded should show if isFuturePaymentMethodAvailable (3 days cooling period)
    return (this.selectedPaymentMethod !== this.currentOrgPaymentType || this.isFuturePaymentMethodAvailable)
  }

  @Emit('emit-bcol-info')
  private getBcolInfo (bcolProfile: BcolProfile) {
    this.bcolInfo = bcolProfile
  }

  private async initialize () {
    this.errorMessage = ''
    this.bcolInfo = {}
    // check if address info is complete if not redirect user to address page
    const isNotAnonUser = this.currentUser?.loginSource !== LoginSource.BCROS
    if (isNotAnonUser) {
      // do it only if address is not already fetched.Or else try to fetch from DB
      if (!this.currentOrgAddress || Object.keys(this.currentOrgAddress).length === 0) {
        // sync and try again
        await this.syncAddress()
        if (!this.currentOrgAddress || Object.keys(this.currentOrgAddress).length === 0) {
          await this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
          return
        }
      }
    }

    if (this.isPaymentViewAllowed) {
      this.savedOrganizationType =
      ((this.currentOrganization?.orgType === Account.PREMIUM) && !this.currentOrganization?.bcolAccountId && this.currentOrganization?.accessType !== AccessType.GOVM)
        ? Account.UNLINKED_PREMIUM : this.currentOrganization.orgType
      this.selectedPaymentMethod = ''
      const orgPayments: OrgPaymentDetails = await this.getOrgPayments()
      // TODO : revisit  if need
      // if need to add more logic -> move to store
      // now setting flag for futurePaymentMethod and TOS to show content and TOS checkbox
      this.isFuturePaymentMethodAvailable = !!orgPayments.futurePaymentMethod || false
      this.isTOSandAcknowledgeCompleted = orgPayments.padTosAcceptedBy !== null || false
      this.selectedPaymentMethod = this.currentOrgPaymentType || ''

      // Rare cases where GOVN account has payment switched from PAD to BCOL in the backend
      if (this.currentOrganization.accessType === AccessType.GOVN && orgPayments.paymentMethod === PaymentTypes.BCOL) {
        this.savedOrganizationType = this.currentOrganization.orgType
      }
    } else {
      // if the account switing happening when the user is already in the transaction page,
      // redirect to account info if its a basic account
      this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
    }
  }

  private get isPaymentViewAllowed (): boolean {
    // checking permission instead of roles to give access for staf
    return [Permission.VIEW_PAYMENT_METHODS, Permission.MAKE_PAYMENT].some(per => this.permissions.includes(per))
  }

  private async verifyPAD () {
    const verifyPad: PADInfoValidation = await this.validatePADInfo()
    if (!verifyPad || verifyPad?.isValid) {
      // proceed to update payment even if the response is empty or valid account info
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

  private cancel () {
    this.initialize()
  }

  private async save () {
    this.isBtnSaved = false
    this.isLoading = true
    let isValid = false

    let createRequestBody: CreateRequestBody

    if (this.selectedPaymentMethod === PaymentTypes.PAD) {
      isValid = await this.verifyPAD()
      createRequestBody = {
        paymentInfo: {
          paymentMethod: PaymentTypes.PAD,
          bankTransitNumber: this.padInfo.bankTransitNumber,
          bankInstitutionNumber: this.padInfo.bankInstitutionNumber,
          bankAccountNumber: this.padInfo.bankAccountNumber
        }
      }
    } if (this.selectedPaymentMethod === PaymentTypes.BCOL) {
      isValid = true
      createRequestBody = {
        paymentInfo: {
          paymentMethod: PaymentTypes.BCOL
        },
        bcOnlineCredential: this.bcolInfo
      }
    } else {
      isValid = true
      createRequestBody = {
        paymentInfo: {
          paymentMethod: this.selectedPaymentMethod
        }
      }
    }

    if (isValid) {
      try {
        await this.updateOrg(createRequestBody)
        this.isBtnSaved = true
        this.isLoading = false
        this.paymentMethodChanged = false
        this.initialize()
        this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error(error)
        this.isLoading = false
        this.isBtnSaved = false
        this.paymentMethodChanged = false
        switch (error.response.status) {
          case 409:
            this.errorMessage = error.response.data.message
            break
          case 400:
            this.errorMessage = error.response.data.message
            break
          default:
            this.errorMessage = 'An error occurred while attempting to create your account.'
        }
      }
    }
  }
  private closeError () {
    this.$refs.errorDialog.close()
  }
}
</script>

<style lang="scss" scoped>
.form__btns {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;

  .v-btn {
    width: 6rem;
  }
}

.save-btn.disabled {
  pointer-events: none;
}
</style>
