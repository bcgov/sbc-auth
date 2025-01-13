<template>
  <v-form
    ref="createAccountInfoForm"
    lazy-validation
    data-test="form-stepper-premium-wrapper"
  >
    <div
      v-display-mode
    >
      <fieldset class="org-business-type">
        <account-business-type
          :saving="saving"
          :premiumLinkedAccount="true"
          :bcolDuplicateNameErrorMessage="bcolDuplicateNameErrorMessage"
          @update:org-business-type="updateOrgBusinessType"
          @valid="checkOrgBusinessTypeValid"
          @update:org-name-clear-errors="updateOrgNameAndClearErrors"
        />
      </fieldset>

      <fieldset>
        <legend class="mb-3">
          Mailing Address
        </legend>
        <base-address-form
          ref="mailingAddress"
          :editing="true"
          :schema="baseAddressSchema"
          :address="address"
          @update:address="updateAddress"
          @valid="checkBaseAddressValidity"
        />
      </fieldset>

      <v-alert
        v-show="errorMessage"
        type="error"
        class="mb-6"
        data-test="div-premium-error"
      >
        {{ errorMessage }}
      </v-alert>
    </div>

    <v-divider class="mt-4 mb-10" />
    <v-row>
      <v-col
        cols="12"
        class="form__btns py-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-stepper-premium-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2 ml-n2"
          >
            mdi-arrow-left
          </v-icon>
          Back
        </v-btn>
        <v-spacer />
        <v-btn
          class="mr-3"
          large
          depressed
          color="primary"
          :loading="saving"
          :disabled="!grantAccess || saving || !isFormValid()"
          data-test="btn-stepper-premium-save"
          @click="save"
        >
          <span>Next
            <v-icon
              right
              class="ml-1"
            >mdi-arrow-right</v-icon>
          </span>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="false"
          :target-route="cancelUrl"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { CreateRequestBody, Member, OrgBusinessType, Organization } from '@/models/Organization'
import AccountBusinessType from '@/components/auth/common/AccountBusinessType.vue'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import BcolLogin from '@/components/auth/create-account/BcolLogin.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { LoginSource } from '@/util/constants'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { User } from '@/models/user'
import { addressSchema } from '@/schemas'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

@Component({
  components: {
    AccountBusinessType,
    BcolLogin,
    BaseAddressForm,
    ConfirmCancelButton

  }
})
export default class AccountCreatePremium extends Mixins(Steppable) {
  username = ''
  password = ''
  errorMessage: string = ''
  // hav to indroduce a new var since it shud show as an error for text field.
  // the errorMessage field is used for full form and network errors.
  bcolDuplicateNameErrorMessage = ''
  saving = false
  isBaseAddressValid: boolean = true

  @State(useOrgStore) public currentOrganization!: Organization
  @State(useOrgStore) public currentOrgAddress!: Address

  @State(useUserStore) public userProfile!: User
  @State(useUserStore) public currentUser!: KCUserProfile

  @Action(useOrgStore) readonly syncMembership!: (orgId: number) => Promise<Member>
  @Action(useOrgStore) readonly syncOrganization!: (orgId: number) => Promise<Organization>
  @Action(useOrgStore) readonly isOrgNameAvailable!: (requestBody: CreateRequestBody) => Promise<boolean>

  @Action(useOrgStore) readonly setCurrentOrganization!: (organization: Organization) => void
  @Action(useOrgStore) readonly setCurrentOrganizationAddress!: (address: Address) => void
  @Action(useOrgStore) readonly setCurrentOrganizationName!: (name: string) => void
  @Action(useOrgStore) readonly setCurrentOrganizationPaymentType!: (paymentType: string) => void
  @Action(useOrgStore) readonly resetBcolDetails!: () => void
  @Action(useOrgStore) readonly setGrantAccess!: (grantAccess: boolean) => void
  @Action(useOrgStore) readonly setCurrentOrganizationBusinessType!: (orgBusinessType: OrgBusinessType) => void

  @Prop() cancelUrl: string
  @Prop({ default: false }) readOnly: boolean

  orgNameReadOnly = true
  static readonly DUPL_ERROR_MESSAGE = 'An account with this name already exists. Try a different account name.'

  baseAddressSchema = addressSchema

  readonly orgNameRules = [v => !!v || 'An account name is required']

  orgBusinessTypeLocal: OrgBusinessType = {}
  isOrgBusinessTypeValid = false

  get isExtraProvUser () {
    // Remove Vuex with Vue 3
    return this.$store.getters['auth/currentLoginSource'] === LoginSource.BCEID
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

  readonly teamNameRules = [v => !!v || 'An account name is required']

  isFormValid (): boolean {
    return !!this.isOrgBusinessTypeValid && !this.errorMessage && !!this.isBaseAddressValid
  }

  get address () {
    return this.currentOrgAddress
  }

  unlinkAccount () {
    this.resetBcolDetails()
  }

  updateAddress (address: Address) {
    this.setCurrentOrganizationAddress(address)
  }

  updateOrgNameAndClearErrors () {
    this.bcolDuplicateNameErrorMessage = ''
    this.errorMessage = ''
  }

  async save () {
    // TODO Handle edit mode as well here
    this.goNext()
  }

  async validateAccountNameUnique () {
    const available = await this.isOrgNameAvailable(
      { 'name': this.orgBusinessTypeLocal.name, 'branchName': this.orgBusinessTypeLocal.branchName })
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

  goBack () {
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

  checkBaseAddressValidity (isValid) {
    this.isBaseAddressValid = !!isValid
  }

  updateOrgBusinessType (orgBusinessType: OrgBusinessType) {
    this.orgBusinessTypeLocal = orgBusinessType
    this.setCurrentOrganizationBusinessType(this.orgBusinessTypeLocal)
  }

  checkOrgBusinessTypeValid (isValid) {
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
