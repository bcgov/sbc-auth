<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">Create a BC Registries Account</h1>
      <p class="mt-3 mb-0">Create an account to access BC Registries products and services.</p>
    </div>
    <v-card flat>
      <Stepper :stepper-configuration="stepperConfig"></Stepper>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import Stepper, { StepConfiguration } from '@/components/auth/stepper/Stepper.vue'
import AccountCreateBasic from '@/components/auth/CreateAccount/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/CreateAccount/AccountCreatePremium.vue'
import AccountTypeSelector from '@/components/auth/CreateAccount/AccountTypeSelector.vue'
import CreateAccountInfoForm from '@/components/auth/CreateAccount/CreateAccountInfoForm.vue'

import UserProfileForm from '@/components/auth/UserProfileForm.vue'

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
        componentProps: {}
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
      },
      {
        title: 'User Profile',
        component: UserProfileForm,
        componentProps: {
          isStepperView: true
        }
      }
    ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
