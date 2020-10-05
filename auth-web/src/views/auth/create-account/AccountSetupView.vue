<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">{{$t('createBCRegistriesAccount')}}</h1>
      <p class="mt-3 mb-0">Create an account to access BC Registries products and services.</p>
    </div>
    <v-card flat>
      <Stepper :stepper-configuration="stepperConfig"></Stepper>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import AccountTypeSelector from '@/components/auth/create-account/AccountTypeSelector.vue'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import PaymentMethodSelector from '@/components/auth/create-account/PaymentMethodSelector.vue'

import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'

  @Component({
    components: {
      CreateAccountInfoForm,
      UserProfileForm,
      AccountTypeSelector,
      AccountCreateBasic,
      AccountCreatePremium,
      PaymentMethodSelector,
      Stepper
    }
  })
export default class AccountSetupView extends Vue {
  private stepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Select Account Type',
        stepName: 'Select Account Type',
        component: AccountTypeSelector,
        componentProps: {}
      },
      {
        title: 'Account Settings',
        stepName: 'Account Settings',
        component: AccountCreateBasic,
        componentProps: {},
        alternate: {
          title: 'Account Settings',
          stepName: 'Account Settings',
          component: AccountCreatePremium,
          componentProps: {}
        }
      },
      {
        title: 'User Profile',
        stepName: 'User Profile',
        component: UserProfileForm,
        componentProps: {
          isStepperView: true
        }
      },
      {
        title: 'Select payment method',
        stepName: 'Payment Method',
        component: PaymentMethodSelector,
        componentProps: {}
      }
    ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
