<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">Change Your BC Registries Account</h1>
      <p class="mt-3 mb-0">Change your existing BC Registries account type and information.</p>
    </div>
    <v-card flat>
      <Stepper :stepper-configuration="stepperConfig"></Stepper>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import { mapActions, mapState } from 'vuex'
import AccountCreateBasic from '@/components/auth/create-account/AccountCreateBasic.vue'
import AccountCreatePremium from '@/components/auth/create-account/AccountCreatePremium.vue'
import AccountTypeSelector from '@/components/auth/create-account/AccountTypeSelector.vue'
import ConfigHelper from '@/util/config-helper'
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import PremiumChooser from '@/components/auth/create-account/PremiumChooser.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'

@Component({
  components: {
    CreateAccountInfoForm,
    UserProfileForm,
    AccountTypeSelector,
    AccountCreateBasic,
    AccountCreatePremium,
    PremiumChooser,
    Stepper
  }
})
export default class AccountChangeView extends Vue {
  private stepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Select Account Type',
        stepName: 'Select Account Type',
        component: AccountTypeSelector,
        componentProps: { 'isAccountChange': true, 'cancelUrl': ConfigHelper.accountSettingsRoute() }
      },
      {
        title: 'Account Information',
        stepName: 'Account Information',
        component: AccountCreateBasic,
        componentProps: { 'isAccountChange': true, 'cancelUrl': ConfigHelper.accountSettingsRoute() },
        alternate: {
          title: 'Account Information',
          stepName: 'Account Information',
          component: PremiumChooser,
          componentProps: { 'isAccountChange': true, 'cancelUrl': ConfigHelper.accountSettingsRoute() }
        }
      }
    ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
