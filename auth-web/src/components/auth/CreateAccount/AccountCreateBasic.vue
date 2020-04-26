<template>
  <v-container>
    <v-form ref="createAccountInfoForm" class="mt-8">
      <v-alert type="error" v-show="errorMessage">{{ errorMessage }}</v-alert>
      <h4 class="mb-2">Enter an Account Name</h4>
      <v-text-field
        filled
        label="Account Name"
        v-model.trim="orgName"
        :rules="orgNameRules"
        persistent-hint
        :disabled="saving"
        hint="Example: Your Business Name"
      />
      <v-row>
        <v-col cols="12" class="d-inline-flex">
          <v-btn large depressed color="grey lighten-3" class="mx-1" @click="goBack">
            <v-icon left class="mr-1">mdi-arrow-left</v-icon>
            Back
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn
            large
            color="primary"
            class="mr-2"
            :loading="saving"
            :disabled="!isFormValid() || saving"
            @click="save"
            depressed
            data-test="save-button"
          >
            Save and Continue
          </v-btn>
          <ConfirmCancelButton
            :disabled="saving"
          ></ConfirmCancelButton>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script lang="ts">

import { Component, Mixins } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Account } from '@/util/constants'
import BaseAddress from '@/components/auth/BaseAddress.vue'
import BcolLogin from '@/components/auth/BcolLogin.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import OrgModule from '@/store/modules/org'
import Steppable from '@/components/auth/stepper/Steppable.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BcolLogin,
    BaseAddress,
    ConfirmCancelButton
  },
  computed: {
    ...mapState('org', ['currentOrganization']),
    ...mapState('user', ['userProfile', 'currentUser'])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganization', 'setOrgName'
    ]),
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization', 'isOrgNameAvailable'])
  }
})
export default class AccountCreateBasic extends Mixins(Steppable) {
  private orgStore = getModule(OrgModule, this.$store)
  private errorMessage: string = ''
  private saving = false
  private readonly createOrg!: () => Promise<Organization>
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private readonly isOrgNameAvailable!: (orgName: string) => Promise<boolean>
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private readonly currentOrganization!: Organization
  private orgName: string = ''

  $refs: {
    createAccountInfoForm: HTMLFormElement
  }

  private readonly orgNameRules = [v => !!v || 'An account name is required']
  private isFormValid (): boolean {
    return !!this.orgName
  }

  private async save () {
    // Validate form, and then create an team with this user a member
    if (this.isFormValid()) {
      const org:Organization = { name: this.orgName, orgType: Account.BASIC }
      this.setCurrentOrganization(org)
      if (!this.stepForward) {
        try {
          this.saving = true
          const organization = await this.createOrg()
          await this.syncOrganization(organization.id)
          await this.syncMembership(organization.id)
          this.$store.commit('updateHeader')
          this.redirectToNext(organization)
        } catch (err) {
          this.saving = false
          switch (err.response.status) {
            case 409:
              this.errorMessage =
                      'An account with this name already exists. Try a different account name.'
              break
            case 400:
              if (err.response.data.code === 'MAX_NUMBER_OF_ORGS_LIMIT') {
                this.errorMessage = 'Maximum number of accounts reached'
              } else {
                this.errorMessage = 'Invalid account name'
              }
              break
            default:
              this.errorMessage =
                      'An error occurred while attempting to create your account.'
          }
        }
      } else {
        // check if the name is avaialble
        const avaialble = await this.isOrgNameAvailable(this.orgName)
        if (avaialble) {
          this.stepForward()
        } else {
          this.errorMessage =
                  'An account with this name already exists. Try a different account name.'
        }
      }
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
