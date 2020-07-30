<template>
  <v-form class="pt-5" ref="createAccountInfoForm">
    <fieldset>
      <legend class="mb-3">Enter an Account Name</legend>
      <v-slide-y-transition>
        <div v-show="errorMessage">
          <v-alert type="error" icon="mdi-alert-circle-outline">{{ errorMessage }}</v-alert>
        </div>
      </v-slide-y-transition>
      <v-text-field
        filled
        label="Account Name"
        v-model.trim="orgName"
        :rules="orgNameRules"
        :disabled="saving"
      />
    </fieldset>
    <template v-if="isExtraProvUser">
      <h4 class="mb-4">Mailing Address</h4>
      <base-address-form
        ref="mailingAddress"
        :editing="true"
        :schema="baseAddressSchema"
        :address="address"
        @update:address="updateAddress"
        @valid="checkBaseAddressValidity"
      />
    </template>

    <v-divider class="my-10"></v-divider>

    <v-row>
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          @click="goBack">
          <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          class="mr-3"
          :loading="saving"
          :disabled="!isFormValid() || saving  || !isBaseAddressValid"
          @click="save"
          data-test="save-button"
        >
          <span v-if="!isAccountChange">Next
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>
          <span v-if="isAccountChange">Change Account</span>
        </v-btn>
        <ConfirmCancelButton
          :disabled="saving"
          :clear-current-org="!isAccountChange"
          :target-route="cancelUrl"
          :showConfirmPopup="false"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Account, Actions, LoginSource, SessionStorageKeys } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import BcolLogin from '@/components/auth/BcolLogin.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import OrgModule from '@/store/modules/org'
import Steppable from '@/components/auth/stepper/Steppable.vue'
import { addressSchema } from '@/schemas'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BcolLogin,
    BaseAddressForm,
    ConfirmCancelButton
  },
  computed: {
    ...mapState('org', ['currentOrganization', 'currentOrgAddress']),
    ...mapState('user', ['userProfile', 'currentUser'])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganization', 'setOrgName', 'setCurrentOrganizationAddress'
    ]),
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization', 'isOrgNameAvailable', 'changeOrgType'])
  }
})
export default class AccountCreateBasic extends Mixins(Steppable) {
  private orgStore = getModule(OrgModule, this.$store)
  private errorMessage: string = ''
  private saving = false
  private readonly createOrg!: () => Promise<Organization>
  private readonly changeOrgType!: (action:Actions) => Promise<Organization>
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly isOrgNameAvailable!: (orgName: string) => Promise<boolean>
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private readonly currentOrganization!: Organization
  private orgName: string = ''
  @Prop() isAccountChange: boolean
  @Prop() cancelUrl: string
  private isBaseAddressValid: boolean = !this.isExtraProvUser
  private readonly currentOrgAddress!: Address
  private readonly setCurrentOrganizationAddress!: (address: Address) => void

  private baseAddressSchema: {} = addressSchema

  $refs: {
    createAccountInfoForm: HTMLFormElement
  }

  private readonly orgNameRules = [v => !!v || 'An account name is required']
  private isFormValid (): boolean {
    return !!this.orgName
  }

  private async mounted () {
    if (this.currentOrganization) {
      this.orgName = this.currentOrganization.name
    }
  }
  private get address () {
    return this.currentOrgAddress
  }
  private updateAddress (address: Address) {
    this.setCurrentOrganizationAddress(address)
  }

  private checkBaseAddressValidity (isValid) {
    this.isBaseAddressValid = !!isValid
  }

  private get isExtraProvUser () {
    return this.$store.getters['auth/currentLoginSource'] === LoginSource.BCEID
  }

  private async save () {
    // Validate form, and then create an team with this user a member
    if (this.isFormValid()) {
      // if its not account change , do check for duplicate
      // if its account change , check if user changed the already existing name
      const checkNameAVailability = !this.isAccountChange || (this.orgName !== this.currentOrganization?.name)
      if (checkNameAVailability) {
        const available = await this.isOrgNameAvailable(this.orgName)
        if (!available) {
          this.errorMessage =
                'An account with this name already exists. Try a different account name.'
          return
        }
      }
      if (this.isAccountChange) {
        try {
          const org: Organization = { name: this.orgName, orgType: Account.BASIC, id: this.currentOrganization.id }
          this.setCurrentOrganization(org)
          this.saving = true
          const organization = await this.changeOrgType('downgrade')
          await this.syncOrganization(organization.id)
          // await this.syncMembership(organization.id)
          this.$store.commit('updateHeader')
          this.$router.push('/change-account-success')
          return
        } catch (err) {
          this.saving = false
          this.errorMessage = 'An error occurred while attempting to create your account.'
        }
      } else {
        const org: Organization = { name: this.orgName, orgType: Account.BASIC }
        this.setCurrentOrganization(org)
        // check if the name is avaialble
        this.stepForward()
      }
    }
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
  }

  private goBack () {
    this.stepBack()
  }

  private goNext () {
    this.stepForward()
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

.bcol-acc-label {
  font-size: 1.35rem;
  font-weight: 600;
}

.grant-access {
  font-size: 1rem !important;
}
</style>
