<template>
      <v-form ref="createAccountInfoForm" lazy-validation>
        <div class="view-container">
            <h1 class="mb-5">Account Settings</h1>
            <p class="intro-text">You must be the Prime Contact to link this account with your existing BC Online account.</p>
          <BcolLogin v-on:account-link-successful="onLink" v-show="!linked"></BcolLogin>
           <v-container v-if="linked">
            <v-alert type="text" v-model="linked"  outlined icon="mdi-check">
                <v-row>
                    <v-col cols="8">
                    ACCOUNT LINKED!
                    </v-col>
                    <v-col cols="4">
                        <v-btn large color="primary" @click="unlinkAccounts()" data-test="dialog-save-button">Remove Linked Accounts</v-btn>
                    </v-col>
                </v-row>
                <v-row v-if="bcolAccountDetails">
                    <v-col cols="6">
                        <h3>MY BCOL Account</h3>
                        Account No: {{bcolAccountDetails.accountNumber}}   |   Authorizing User ID: {{bcolAccountDetails.userId}}
                    </v-col>
                </v-row>

            </v-alert>
            <v-checkbox
                    v-model="grantAccess" class="mt-5 pt-5">
               <template v-slot:label>
                   <span v-html="grantAccessText"></span>
               </template>
            </v-checkbox>
            <div v-if="grantAccess">
               <v-row>
                   <v-col cols="12" class="pb-0 mb-2">
                       <h4 class="mb-2">Account Name</h4>
                   </v-col>
               </v-row>
               <v-row>
                   <v-col cols="12" class="">
                       <v-text-field
                               filled
                               label="Account Name"
                               v-model.trim="bcolAccountDetails.orgName"
                               :rules="accountNameRules"
                               persistent-hint
                               disabled
                               data-test="account-name"
                       >
                       </v-text-field>
                   </v-col>
               </v-row>
                <base-address :address="bcolAccountDetails.address">
                </base-address>
               </div>
           </v-container>

        </div>

      </v-form>
</template>

<script lang="ts">

import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import BaseAddress from '@/components/auth/BaseAddress.vue'
import BcolLogin from '@/components/auth/BcolLogin.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BcolLogin, BaseAddress
  },
  computed: {
    ...mapState('org', ['currentOrganization']),
    ...mapState('user', ['userProfile', 'currentUser'])
  },
  methods: {
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization'])
  }
})
export default class CreateAccountInfoForm extends Vue {
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
    private linked = false
    private bcolAccountDetails:BcolAccountDetails
    private grantAccess:boolean = false
    private grantAccessText:string

    $refs: {
      createAccountInfoForm: HTMLFormElement
    }

    private readonly teamNameRules = [
      v => !!v || 'An account name is required']

    private isFormValid (): boolean {
      return !!this.username && !!this.password
    }
    private onLink (bcolAccountDetails:BcolAccountDetails) {
      debugger
      this.linked = true
      this.bcolAccountDetails = bcolAccountDetails
      this.grantAccessText = `I ,<b></b> ${this.currentUser.fullName} </b>, confirm that I am authorized to grant access to the account <b>${bcolAccountDetails.accountNumber}</b>`
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
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }
</style>
