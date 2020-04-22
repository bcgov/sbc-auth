<template>
  <v-form ref="createAccountInfoForm" lazy-validation>
    <pre v-if="debug">{{currentOrganization|json}}</pre>
    <div class="view-container">
      <h1 class="mb-5">Account Settings</h1>
      <p class="intro-text mb-8">
        You must be the Prime Contact to link this account with your existing BC
        Online account.
      </p>
      <BcolLogin
        v-on:account-link-successful="onLink"
        v-show="!linked"
      ></BcolLogin>
      <v-container v-if="linked">
        <v-alert v-model="linked" dark color="info" icon="mdi-check">
          <v-row>
            <v-col cols="8">
              <div class="text-uppercase mb-3">Account Linked!</div>
              <div v-if="currentOrganization.bcolAccountDetails">
                <div class="bcol-acc-label">
                  {{ currentOrganization.name }}
                </div>
                Account No: {{ currentOrganization.bcolAccountDetails.accountNumber }} | Authorizing
                User ID: {{ currentOrganization.bcolAccountDetails.userId }}
              </div>
            </v-col>
            <v-col cols="4" align-self="center">
              <v-btn
                large
                outlined
                @click="unlinkAccounts()"
                data-test="dialog-save-button"
              >
                <strong>Remove Linked Accounts</strong></v-btn
              >
            </v-col>
          </v-row>
        </v-alert>
        <v-checkbox v-model="grantAccess" class="mt-5">
          <template v-slot:label>
            <span class="grant-access" v-html="grantAccessText"></span>
          </template>
        </v-checkbox>
        <template v-if="grantAccess">
          <v-row class="mt-6">
            <v-col cols="12">
              <h3 class="mb-4">Account Information</h3>
              <p class="mb-0">
                The following information will be imported from your existing BC
                Online account.
              </p>
              <p class="mb-8">
                Review your account information below and update if needed.
              </p>
            </v-col>
          </v-row>
          <v-row class="mb-1">
            <v-col cols="12" class="">
              <h4 class="mb-2">Account Name</h4>
              <v-text-field
                filled
                label="Account Name"
                v-model.trim="currentOrganization.name"
                :rules="accountNameRules"
                persistent-hint
                disabled
                data-test="account-name"
              >
              </v-text-field>
            </v-col>
          </v-row>
          <BaseAddress :address="currentOrganization.bcolAccountDetails.address"> </BaseAddress>
        </template>
      </v-container>
      <v-row>
        <v-col cols="12" class="d-inline-flex">
          <v-btn large color="grey lighten-3" class="mx-1">
            <v-icon left class="mr-1">mdi-arrow-left</v-icon>
            Back
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn large color="primary" :disabled="!grantAccess">
            Next
            <v-icon right class="ml-1">mdi-arrow-right</v-icon>
          </v-btn>
          <v-btn large color="grey lighten-3" class="mx-5">
            Cancel
          </v-btn>
        </v-col>
      </v-row>
    </div>
  </v-form>
</template>

<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Prop, Vue } from 'vue-property-decorator'
import {
  CreateRequestBody,
  Member,
  Organization
} from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Account } from '@/util/constants'
import BaseAddress from '@/components/auth/BaseAddress.vue'
import BcolLogin from '@/components/auth/BcolLogin.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BcolLogin,
    BaseAddress
  },
  computed: {
    ...mapState('org', ['currentOrganization']),
    ...mapState('user', ['userProfile', 'currentUser'])
  },
  methods: {
    ...mapMutations('org', ['setCurrentOrganization']),
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization', ''])
  }
})
export default class AccountCreatePremium extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private username = ''
  private password = ''
  private errorMessage: string = ''
  private saving = false
  private readonly createOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly currentOrganization!: Organization
  private readonly currentUser!: KCUserProfile
  @Prop() stepForward!: () => void
  @Prop() stepBack!: () => void
  private grantAccess: boolean = false
  private grantAccessText: string
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private debug = false

  async mounted () {
    this.setCurrentOrganization(undefined)
  }

  $refs: {
    createAccountInfoForm: HTMLFormElement
  }

  private readonly teamNameRules = [v => !!v || 'An account name is required']

  private isFormValid (): boolean {
    return !!this.username && !!this.password
  }

  private unlinkAccounts () {
    // eslint-disable-next-line no-console
    console.log('uni' + JSON.stringify(this.currentOrganization))
  }
  private get linked () {
    return !!this.currentOrganization?.bcolAccountDetails
  }
  private onLink (details: { bcolProfile: BcolProfile, bcolAccountDetails: BcolAccountDetails }) {
    this.grantAccessText = `I ,<strong>${this.currentUser.fullName} </strong>, confirm that I am authorized to grant access to the account <strong>${details.bcolAccountDetails.orgName}</strong>`
    debugger
    if (!this.currentOrganization) {
      var org: Organization = {
        name: details.bcolAccountDetails.orgName,
        accessType: Account.PREMIUM,
        bcolProfile: details.bcolProfile,
        bcolAccountDetails: details.bcolAccountDetails
      }
      this.setCurrentOrganization(org)
    }
  }
  private cancel () {
    if (this.stepBack) {
      this.stepBack()
    } else {
      this.$router.push({ path: '/home' })
    }
  }

  private redirectToNext (organization?: Organization) {
    this.$router.push({ path: `/account/${organization.id}/` })
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
