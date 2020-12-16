<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-6">
      <h2 class="view-header__title" data-test="account-settings-title">
        Payment Methods
      </h2>
      <p class="mt-3 payment-page-sub">
        Manage your pre-authorized debit payments for this account.
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
      @is-pad-valid="isPADValid"
    ></PaymentMethods>
    <v-divider class="my-10"></v-divider>
    <div class="form__btns d-flex">
      <v-btn
        large
        class="save-btn"
        v-bind:class="{ 'disabled': isBtnSaved }"
        :color="isBtnSaved ? 'success' : 'primary'"
        :disabled="isDisableSaveBtn"
        @click="save"
        :loading="isLoading"
      >
        <v-expand-x-transition>
          <v-icon v-show="isBtnSaved">mdi-check</v-icon>
        </v-expand-x-transition>
        <span class="save-btn__label">{{ (isBtnSaved) ? 'Saved' : 'Save' }}</span>
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
import { Account, Pages, PaymentTypes } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, MembershipType, OrgPaymentDetails, Organization, PADInfo, PADInfoValidation } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    PaymentMethods,
    ModalDialog
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentOrgPaymentType',
      'currentMembership'
    ])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationPaymentType'
    ]),
    ...mapActions('org', [
      'validatePADInfo',
      'getOrgPayments',
      'updateOrg'
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
  private savedOrganizationType: string = ''
  private selectedPaymentMethod: string = ''
  private padInfo: PADInfo = {} as PADInfo
  private isBtnSaved = false
  private disableSaveBtn = false
  private errorTitle = 'Payment update failed'
  private errorText = ''
  private isLoading: boolean = false
  private padValid: boolean = false

  $refs: {
      errorDialog: ModalDialog
    }

  private setSelectedPayment (payment) {
    this.selectedPaymentMethod = payment
    this.isBtnSaved = false
  }

  private get isDisableSaveBtn () {
    let disableSaveBtn = false

    if ((this.selectedPaymentMethod === PaymentTypes.PAD && !this.padValid) || (this.selectedPaymentMethod === this.currentOrgPaymentType)) {
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
    return (this.selectedPaymentMethod !== this.currentOrgPaymentType)
  }

  private async initialize () {
    if (this.isPaymentViewAllowed) {
      this.savedOrganizationType =
      ((this.currentOrganization?.orgType === Account.PREMIUM) && !this.currentOrganization?.bcolAccountId)
        ? Account.UNLINKED_PREMIUM : this.currentOrganization.orgType
      this.selectedPaymentMethod = ''
      const orgPayments: OrgPaymentDetails = await this.getOrgPayments()
      this.selectedPaymentMethod = this.currentOrgPaymentType || ''
    } else {
      // if the account switing happening when the user is already in the transaction page,
      // redirect to account info if its a basic account
      this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
    }
  }

  private get isPaymentViewAllowed (): boolean {
    return (this.currentMembership.membershipTypeCode === MembershipType.Admin)
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
        this.initialize()
        this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error(error)
        this.isLoading = false
        this.isBtnSaved = false
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
