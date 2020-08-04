<template>
  <v-container>
    <v-form ref="createAccountInfoForm" lazy-validation>
      <p class="mb-6">
        You must be the Prime Contact to link this account with your existing BC Online account.
      </p>
      <p class="mb-6">
        Linking accounts imports your organization’s contact and drawdown account information.
      </p>
      <p class="mb-10">
        Linking accounts <strong>does not</strong> import your existing users or any businesses you manage. You can invite team members and add businesses once your account is set up successfully.
      </p>
      <BcolLogin @account-link-successful="onLink" v-show="!linked"></BcolLogin>
      <template v-if="linked">
        <v-alert dark color="primary" icon="mdi-check" class="py-4 pr-8 pl-4" v-model="linked">
          <div class="bcol-acc d-flex justify-space-between align-center">
            <div v-if="currentOrganization.bcolAccountDetails">
              <div class="bcol-acc__link-status mb-3">Account Linked!</div>
              <div class="bcol-acc__name">
                {{ currentOrganization.name }}
              </div>
              <ul class="bcol-acc__meta">
                <li>
                  Account No: {{ currentOrganization.bcolAccountDetails.accountNumber }}
                </li>
                <li>
                  Prime Contact ID: {{ currentOrganization.bcolAccountDetails.userId }}
                </li>
              </ul>
            </div>
            <div>
              <v-btn
                large
                outlined
                class="font-weight-bold"
                @click="unlinkAccounts()"
                data-test="dialog-save-button"
              >
                Unlink Account
              </v-btn>
            </div>
          </div>
        </v-alert>
        <v-checkbox color="primary" v-model="grantAccess" class="bcol-auth mt-8 ml-3">
          <template v-slot:label>
            <div class="bcol-auth__label" v-html="grantAccessText"></div>
          </template>
        </v-checkbox>
        <v-expand-transition>
          <div v-if="grantAccess">
            <v-divider class="mt-4 mb-10"></v-divider>
            <template>
              <v-row class="mt-6">
                <v-col cols="12">
                  <h3 class="mb-3">Account Information</h3>
                  <p class="mb-10">
                    The following information will be imported from your existing BC Online account. Review your account <br> information below and update if needed.
                  </p>
                </v-col>
              </v-row>
              <ul class="nv-list mb-2">
                <li class="nv-list-item mb-10">
                  <div class="name" id="accountType">Account Name</div>
                  <div class="value" aria-labelledby="accountType">
                    <div class="value__title">
                      <div class="mb-1">{{ currentOrganization.name }}</div>
                      <div class="text--secondary subtitle-2">Linked accounts will use your existing BC Online Account name</div>
                    </div>
                  </div>
                </li>
              </ul>
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
          </div>
        </v-expand-transition>

        <v-alert type="error" class="mb-6" v-show="errorMessage">
          {{ errorMessage }}
        </v-alert>
      </template>

      <v-divider class="mt-4 mb-10"></v-divider>

      <v-row>
        <v-col cols="12" class="form__btns py-0 d-inline-flex">
          <v-btn
            large
            depressed
            color="default"
            @click="goBack">
            <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
            Back
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn class="mr-3" large depressed color="primary" :loading="saving" :disabled="!grantAccess || saving || !isBaseAddressValid" @click="save">
            <span v-if="!isAccountChange">Next
             <v-icon right class="ml-1">mdi-arrow-right</v-icon>
            </span>
            <span v-if="isAccountChange">Change Account</span>

          </v-btn>
          <ConfirmCancelButton
            :showConfirmPopup="linked"
            :clear-current-org="!isAccountChange"
            :target-route="cancelUrl"
          ></ConfirmCancelButton>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { Account, Actions, LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import BcolLogin from '@/components/auth/BcolLogin.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
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
      'setCurrentOrganization',
      'setCurrentOrganizationAddress',
      'setGrantAccess',
      'resetBcolDetails'
    ]),
    ...mapActions('org', [
      'createOrg',
      'syncMembership',
      'syncOrganization',
      'changeOrgType'
    ])
  }
})
export default class AccountCreatePremium extends Mixins(Steppable) {
  private orgStore = getModule(OrgModule, this.$store)
  private username = ''
  private password = ''
  private errorMessage: string = ''
  private saving = false
  private isBaseAddressValid: boolean = true
  private readonly createOrg!: () => Promise<Organization>
  private readonly currentOrgAddress!: Address
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly currentOrganization!: Organization
  private readonly currentUser!: KCUserProfile
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private readonly setCurrentOrganizationAddress!: (address: Address) => void
  private readonly resetBcolDetails!: () => void
  private readonly setGrantAccess!: (grantAccess: boolean) => void
  private readonly changeOrgType!: (action:Actions) => Promise<Organization>
  @Prop() cancelUrl: string
  @Prop() isAccountChange: boolean

  private baseAddressSchema: {} = addressSchema

  private get isExtraProvUser () {
    return this.$store.getters['auth/currentLoginSource'] === LoginSource.BCEID
  }

  get grantAccessText () {
    // https://github.com/bcgov/entity/issues/4178
    // TODO once above ticket is in pace , remove the if checks
    const username = this.isExtraProvUser ? '' : `, ${this.currentUser?.fullName},`
    return `I ${username} confirm that I am authorized to grant access to the account ${this.currentOrganization?.bcolAccountDetails?.orgName}`
  }

  get grantAccess () {
    return this.currentOrganization?.grantAccess
  }
  set grantAccess (grantAccess: boolean) {
    this.setGrantAccess(grantAccess)
  }
  $refs: {
    createAccountInfoForm: HTMLFormElement
  }

  private readonly teamNameRules = [v => !!v || 'An account name is required']

  private isFormValid (): boolean {
    return !!this.username && !!this.password
  }

  private get address () {
    return this.currentOrgAddress
  }

  private unlinkAccounts () {
    this.resetBcolDetails()
  }

  private get linked () {
    return !!this.currentOrganization?.bcolAccountDetails
  }

  private updateAddress (address: Address) {
    this.setCurrentOrganizationAddress(address)
  }

  private async save () {
    // TODO Handle edit mode as well here
    this.goNext()
  }

  private onLink (details: {
    bcolProfile: BcolProfile
    bcolAccountDetails: BcolAccountDetails
  }) {
    var org: Organization = {
      id: this.currentOrganization.id,
      name: details.bcolAccountDetails.orgName,
      accessType: this.currentOrganization.accessType,
      bcolProfile: details.bcolProfile,
      bcolAccountDetails: details.bcolAccountDetails,
      grantAccess: false,
      orgType: Account.PREMIUM
    }
    this.setCurrentOrganization(org)
    this.setCurrentOrganizationAddress(details.bcolAccountDetails.address)
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
    if (this.isAccountChange) {
      try {
        this.saving = true
        const organization = await this.changeOrgType('upgrade')
        await this.syncOrganization(organization.id)
        // await this.syncMembership(organization.id)
        this.$store.commit('updateHeader')
        this.$router.push('/change-account-success')
        return
      } catch (err) {
        this.saving = false
        this.errorMessage =
                    'An error occurred while attempting to create your account.'
      }
    } else {
      this.stepForward()
    }
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
  }

  private checkBaseAddressValidity (isValid) {
    this.isBaseAddressValid = !!isValid
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

  ::v-deep {
    .v-input__slot {
      align-items: flex-start;
    }
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
