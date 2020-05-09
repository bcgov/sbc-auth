<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">Create a BC Registries Account</h1>
      <p class="mb-0">Create an account to access BC Registries products and services.</p>
    </div>
    <v-card flat>
      <Stepper :stepper-configuration="stepperConfig"></Stepper>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import Stepper, { StepConfiguration } from '@/components/auth/stepper/Stepper.vue'
import { mapActions, mapState } from 'vuex'
import AccountCreateBasic from '@/components/auth/CreateAccount/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/CreateAccount/AccountCreatePremium.vue'
import AccountTypeSelector from '@/components/auth/CreateAccount/AccountTypeSelector.vue'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import CreateAccountInfoForm from '@/components/auth/CreateAccount/CreateAccountInfoForm.vue'
import LoginBCSC from '@/components/auth/LoginBCSC.vue'
import { Organization } from '@/models/Organization'
import { RouteConfig } from 'vue-router'
import { SessionStorageKeys } from '@/util/constants'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import { getRoutes } from '@/router'
import { mount } from '@vue/test-utils'

@Component({
  components: {
    CreateAccountInfoForm,
    UserProfileForm,
    AccountTypeSelector,
    AccountCreateBasic,
    AccountCreatePremium,
    Stepper
  }
})
export default class AccountSetupView extends Vue {
  private stepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Select Account Type',
        component: AccountTypeSelector,
        componentProps: { 'isAccountChange': true }
      },
      {
        title: 'Account Settings',
        component: AccountCreateBasic,
        componentProps: {},
        alternate: {
          title: 'Account Settings',
          component: AccountCreatePremium,
          componentProps: {}
        }
      }
    ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
