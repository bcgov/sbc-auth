<template>
<v-container>
  <v-form ref="premiumAccountChooser" lazy-validation>
    <p class="mt-3">Do you want to link this account with an existing BC Online Account? <a href="">Learn more</a></p>
    <v-radio-group class="mb-3" @change="loadComponent" v-model="isBcolSelected">
      <v-radio label="Yes" value="yes" />
      <v-radio label="No" value="no" />
    </v-radio-group>
    <v-divider />
    <component
      ref="activeComponent"
      class="pl-0"
      :is="currentComponent"
      :step-back="stepBack"
      :step-forward="stepForward"
    />
    <template v-if="!isBcolSelected">
      <v-divider />
      <v-row class="my-5">
        <v-col cols="12" class="form__btns py-0 d-inline-flex">
          <v-btn
            large
            depressed
            color="default"
            @click="stepBack">
            <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
            Back
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn class="mr-3" large depressed color="primary" :loading="saving" :disabled="saving || !isBcolSelected">
            <span v-if="!isAccountChange">Next
              <v-icon right class="ml-1">mdi-arrow-right</v-icon>
            </span>
            <span v-if="isAccountChange">Change Account</span>

          </v-btn>
          <ConfirmCancelButton
            :clear-current-org="!isAccountChange"
            :target-route="cancelUrl"
          />
        </v-col>
      </v-row>
    </template>
  </v-form>
</v-container>

</template>

<script lang="ts">

import { Account, Actions } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import Vue from 'vue'

@Component({
  components: {
    AccountCreateBasic,
    ConfirmCancelButton
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentOrganizationType'
    ])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationType'
    ]),
    ...mapActions('org', [
      'createOrg',
      'syncMembership',
      'syncOrganization',
      'changeOrgType'
    ])
  }
})
export default class PremiumChooser extends Mixins(Steppable) {
  @Prop() isAccountChange: boolean
  @Prop() cancelUrl: string
  private readonly currentOrganizationType!: string
  private readonly currentOrganization!: Organization
  private isBcolSelected = null
  private currentComponent = null
  private saving = false
  private errorMessage: string = ''
  private readonly setCurrentOrganizationType!: (orgType: string) => void
  private readonly changeOrgType!: (action: Actions) => Promise<Organization>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>

  $refs: {
    activeComponent: AccountCreatePremium | AccountCreateBasic
  }

  private mounted () {
    if (!this.isAccountChange) {
      this.isBcolSelected = ((this.currentOrganizationType === Account.PREMIUM) && this.currentOrganization?.bcolProfile) ? 'yes' : null
      this.isBcolSelected = (this.currentOrganizationType === Account.UNLINKED_PREMIUM && this.currentOrganization?.name) ? 'no' : this.isBcolSelected
      this.loadComponent()
    }
  }

  private loadComponent () {
    if (this.isBcolSelected === 'yes') {
      this.setCurrentOrganizationType(Account.PREMIUM)
      this.currentComponent = AccountCreatePremium
    } else if (this.isBcolSelected === 'no') {
      this.setCurrentOrganizationType(Account.UNLINKED_PREMIUM)
      this.currentComponent = AccountCreateBasic
    } else {
      this.currentComponent = null
    }
  }

  private cancel () {
    if (this.stepBack) {
      this.stepBack()
    } else {
      this.$router.push({ path: '/home' })
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
