<template>
  <v-form ref="createAccountInfoForm" lazy-validation data-test="form-stepper-premium-wrapper" >
    <h3 class="mt-n1 mb-5" v-display-mode>Link with an existing BC Online account</h3>

    <div v-show="!linked" v-display-mode>
      <p class="mb-4">Linking accounts will import your organization’s contact and drawdown account information. Linking accounts <strong>will not import</strong> your existing users or any businesses you manage. You can invite team members and add businesses once your account is set up successfully.</p>
      <p class="mb-8">You must be the <strong>Prime Contact</strong> to link this account with your existing BC Online account.</p>
      <BcolLogin @account-link-successful="onLink"></BcolLogin>
    </div>

    <div v-if="linked" v-display-mode>
      <p class="mb-8">
        The following information will be imported from your existing BC Online account. Review your account <br> information below and update if needed.
      </p>
      <LinkedBCOLBanner class="mb-9"
        :bcolAccountName="currentOrganization.bcolAccountName"
        :bcolAccountDetails="currentOrganization.bcolAccountDetails"
        :showUnlinkAccountBtn="true"
        @unlink-account="unlinkAccount"
      ></LinkedBCOLBanner>

      <fieldset class="org-business-type">
        <account-business-type
        :saving="saving"
        :premiumLinkedAccount="true"
        :bcolDuplicateNameErrorMessage="bcolDuplicateNameErrorMessage"
        @update:org-business-type="updateOrgBusinessType"
        @valid="checkOrgBusinessTypeValid"
        @update:org-name-clear-errors="updateOrgNameAndClearErrors">
        </account-business-type>
      </fieldset>

      <fieldset>
        <legend class="mb-3">Mailing Address</legend>
        <base-address-form
          ref="mailingAddress"
          :editing="true"
          :schema="baseAddressSchema"
          :address="address"
          @update:address="updateAddress"
          @valid="checkBaseAddressValidity"
        />
      </fieldset>

      <fieldset>
        <legend>Authorization</legend>
        <v-checkbox
          color="primary"
          class="bcol-auth ml-2"
          v-model="grantAccess"
          data-test="check-premium-auth"
          >
          <template v-slot:label>
            <div class="bcol-auth__label" v-html="grantAccessText"></div>
          </template>
        </v-checkbox>
      </fieldset>

      <v-alert type="error" class="mb-6" v-show="errorMessage" data-test="div-premium-error">
        {{ errorMessage }}
      </v-alert>
    </div>

    <v-divider class="mt-4 mb-10"></v-divider>

    <v-row>
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
          data-test="btn-stepper-premium-back">
          <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
          Back
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn class="mr-3" large depressed color="primary" :loading="saving"
        :disabled="!grantAccess || saving || !isFormValid()"
        @click="save"
         data-test="btn-stepper-premium-save">
          <span >Next
            <v-icon right class="ml-1">mdi-arrow-right</v-icon>
          </span>

        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="linked"
          :target-route="cancelUrl"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>

  </v-form>
</template>

<script lang="ts">
import { Account, LoginSource, PaymentTypes } from '@/util/constants'
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { CreateRequestBody, Member, OrgBusinessType, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import BcolLogin from '@/components/auth/create-account/BcolLogin.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { User } from '@/models/user'
import { addressSchema } from '@/schemas'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const UserModule = namespace('user')

@Component({
  components: {
    AccountBusinessType,
    BcolLogin,
    BaseAddressForm,
    ConfirmCancelButton,
    LinkedBCOLBanner
  }
})
export default class AccountCreatePremium extends Mixins(Steppable) {
  // private orgStore = getModule(OrgModule, this.$store)
  private username = ''
  private password = ''
  private errorMessage: string = ''
  // hav to indroduce a new var since it shud show as an error for text field.
  // the errorMessage field is used for full form and network errors.
  private bcolDuplicateNameErrorMessage = ''
  private saving = false
  private isBaseAddressValid: boolean = true

  @OrgModule.State('currentOrganization') public currentOrganization!: Organization
  @OrgModule.State('currentOrgAddress') public currentOrgAddress!: Address

  @UserModule.State('userProfile') public userProfile!: User
  @UserModule.State('currentUser') public currentUser!: KCUserProfile

  @OrgModule.Action('syncMembership') private readonly syncMembership!: (orgId: number) => Promise<Member>
  @OrgModule.Action('syncOrganization') private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  @OrgModule.Action('isOrgNameAvailable') private readonly isOrgNameAvailable!: (requestBody: CreateRequestBody) => Promise<boolean>

  @OrgModule.Mutation('setCurrentOrganization') private readonly setCurrentOrganization!: (organization: Organization) => void
  @OrgModule.Mutation('setCurrentOrganizationAddress') private readonly setCurrentOrganizationAddress!: (address: Address) => void
  @OrgModule.Mutation('setCurrentOrganizationName') private readonly setCurrentOrganizationName!: (name: string) => void
  @OrgModule.Mutation('setCurrentOrganizationPaymentType') private readonly setCurrentOrganizationPaymentType!: (paymentType: string) => void
  @OrgModule.Mutation('resetBcolDetails') private readonly resetBcolDetails!: () => void
  @OrgModule.Mutation('setGrantAccess') private readonly setGrantAccess!: (grantAccess: boolean) => void
  @OrgModule.Mutation('setCurrentOrganizationBusinessType') private readonly setCurrentOrganizationBusinessType!: (orgBusinessType: OrgBusinessType) => void

  @Prop() cancelUrl: string
  @Prop({ default: false }) readOnly: boolean

  private orgNameReadOnly = true
  private static readonly DUPL_ERROR_MESSAGE = 'An account with this name already exists. Try a different account name.'

  private baseAddressSchema: {} = addressSchema

  private readonly orgNameRules = [v => !!v || 'An account name is required']

  private orgBusinessTypeLocal: OrgBusinessType = {}
  private isOrgBusinessTypeValid = false

  private get isExtraProvUser () {
    return this.$store.getters['auth/currentLoginSource'] === LoginSource.BCEID
  }

  get grantAccessText () {
    // https://github.com/bcgov/entity/issues/4178
    // TODO once above ticket is in pace , remove the if checks
    const username = this.isExtraProvUser ? '' : `, ${this.currentUser?.fullName},`
    // on re-upload we will not have currentOrganization?.bcolAccountDetails since we are not making connection call which will be avaialble on saved deteails
    // so on re-upload check and set account name
    const accountName = this.readOnly
      ? this.currentOrganization.bcolAccountName
      : (this.currentOrganization?.bcolAccountDetails?.orgName ||
        this.currentOrganization.bcolAccountName)
    return `I ${username} confirm that I am authorized to grant access to the account ${accountName}`
  }

  get grantAccess () {
    return this.readOnly ? true : this.currentOrganization?.grantAccess
  }
  set grantAccess (grantAccess: boolean) {
    this.setGrantAccess(grantAccess)
  }
  $refs: {
    createAccountInfoForm: HTMLFormElement
  }

  private readonly teamNameRules = [v => !!v || 'An account name is required']

  private isFormValid (): boolean {
    return !!this.isOrgBusinessTypeValid && !this.errorMessage && !!this.isBaseAddressValid
  }

  private get address () {
    return this.currentOrgAddress
  }

  private unlinkAccount () {
    this.resetBcolDetails()
  }

  private get linked () {
    return !!this.currentOrganization?.bcolAccountDetails
  }

  private updateAddress (address: Address) {
    this.setCurrentOrganizationAddress(address)
  }

  private updateOrgNameAndClearErrors () {
    this.bcolDuplicateNameErrorMessage = ''
    this.errorMessage = ''
  }

  private async save () {
    // TODO Handle edit mode as well here
    this.goNext()
  }

  private async onLink (details: {
    bcolProfile: BcolProfile
    bcolAccountDetails: BcolAccountDetails
  }) {
    // sync local tracking object and update child AccountBusinessType with new org name
    const orgName = details.bcolAccountDetails.orgName
    this.orgBusinessTypeLocal.name = orgName
    var org: Organization = {
      id: this.currentOrganization.id,
      name: details.bcolAccountDetails.orgName,
      accessType: this.currentOrganization.accessType,
      bcolProfile: details.bcolProfile,
      bcolAccountDetails: details.bcolAccountDetails,
      grantAccess: false,
      orgType: Account.PREMIUM,
      bcolAccountName: details.bcolAccountDetails.orgName
    }
    this.setCurrentOrganization(org)
    this.setCurrentOrganizationPaymentType(PaymentTypes.BCOL)
    this.setCurrentOrganizationAddress(details.bcolAccountDetails.address)
    await this.validateAccountNameUnique()
  }

  private async validateAccountNameUnique () {
    const available = await this.isOrgNameAvailable({ 'name': this.orgBusinessTypeLocal.name, 'branchName': this.orgBusinessTypeLocal.branchName })
    if (!available) {
      this.bcolDuplicateNameErrorMessage = AccountCreatePremium.DUPL_ERROR_MESSAGE
      this.orgNameReadOnly = false
      return false
    } else {
      this.orgNameReadOnly = true
      return true
    }
  }

  private cancel () {
    if (this.stepBack) {
      this.stepBack()
    } else {
      this.$router.push({ path: '/home' })
    }
  }

  private goBack () {
    this.stepBack()
  }

  private async goNext () {
    const isValidName = this.readOnly ? true : await this.validateAccountNameUnique()
    if (isValidName) {
      this.stepForward()
    } else {
      this.errorMessage = AccountCreatePremium.DUPL_ERROR_MESSAGE
    }
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
  }

  private checkBaseAddressValidity (isValid) {
    this.isBaseAddressValid = !!isValid
  }

  private updateOrgBusinessType (orgBusinessType: OrgBusinessType) {
    this.orgBusinessTypeLocal = orgBusinessType
    this.setCurrentOrganizationBusinessType(this.orgBusinessTypeLocal)
  }

  private checkOrgBusinessTypeValid (isValid) {
    this.isOrgBusinessTypeValid = !!isValid
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Tighten up some of the spacing between rows
[class^='col'] {
  padding-top: 0;
  padding-bottom: 0;
}

.form__btns {
  display: flex;
  justify-content: flex-end;
}

.bcol-acc__link-status {
  text-transform: uppercase;
  font-size: 0.9375rem;
}

.bcol-acc {
  margin-top: 1px;
  margin-bottom: 2px;
}

.bcol-acc__name {
  font-size: 1.125rem;
  font-weight: 700;
}

.bcol-acc__meta {
  margin: 0;
  padding: 0;
  list-style-type: none;

  li {
    position: relative;
    display: inline-block
  }

  li + li {
    &:before {
      content: ' | ';
      display: inline-block;
      position: relative;
      top: -2px;
      width: 2rem;
      vertical-align: top;
      text-align: center;
    }
  }
}

.bcol-auth {
  max-width: 40rem;

  ::v-deep .v-input__slot{
    align-items: flex-start;
  }
}

.bcol-auth__label {
  margin-left: 0.5rem;
  line-height: 1.5;
  color: var(--v-grey-darken4) !important;
}

.nv-list {
  margin: 0;
  padding: 0;
  list-style-type: none;
}

.nv-list-item {
  vertical-align: top;

  .name, .value {
    display: inline-block;
    vertical-align: top;
  }

  .name {
    min-width: 10rem;
    font-weight: 700;
  }
}

</style>
