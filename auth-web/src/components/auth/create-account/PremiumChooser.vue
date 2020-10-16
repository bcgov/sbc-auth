<template>
<v-container>
  <v-form ref="premiumAccountChooser" lazy-validation>
    <p class="mt-3">Do you want to link this account with an existing BC Online Account? <a href="">Learn more</a></p>
    <v-radio-group class="mb-3" @change="loadComponent" v-model="premiumSelected">
      <v-radio label="Yes" value="yes" />
      <v-radio label="No" value="no" />
    </v-radio-group>
    <v-divider />
    <component
      ref="activeComponent"
      class="pl-0"
      :is="currentComponent"
      :step-back="stepBack"
    />
    <v-divider />
    <v-row class="my-5" v-if="!premiumSelected">
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
        <v-btn class="mr-3" large depressed color="primary" :loading="saving" :disabled="saving || !premiumSelected" @click="save">
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
    <v-alert type="error" class="mb-6" v-show="errorMessage">
      {{ errorMessage }}
    </v-alert>
  </v-form>
</v-container>

</template>

<script lang="ts">

import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import { Actions } from '@/util/constants'
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
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
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
  private premiumSelected = null
  private currentComponent = null
  private saving = false
  private errorMessage: string = ''
  private readonly changeOrgType!: (action: Actions) => Promise<Organization>
  private readonly syncOrganization!: (orgId: number) => Promise<Organization>

  $refs: {
    activeComponent: AccountCreatePremium | AccountCreateBasic
  }

  private loadComponent () {
    if (this.premiumSelected === 'yes') {
      this.currentComponent = AccountCreatePremium
    } else if (this.premiumSelected === 'no') {
      this.currentComponent = AccountCreateBasic
    } else {
      this.currentComponent = null
    }
  }

  private async goNext () {
    if (this.isAccountChange) {
      try {
        this.saving = true
        const organization = await this.changeOrgType('upgrade')
        await this.syncOrganization(organization.id)
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

  private goBack () {
    this.stepBack()
  }

  private cancel () {
    if (this.stepBack) {
      this.stepBack()
    } else {
      this.$router.push({ path: '/home' })
    }
  }

  private async save () {
    if (this.premiumSelected === 'no') {
      await (this.$refs.activeComponent as AccountCreateBasic).save()
    }
    this.goNext()
  }
}
</script>

<style lang="scss" scoped>

</style>
