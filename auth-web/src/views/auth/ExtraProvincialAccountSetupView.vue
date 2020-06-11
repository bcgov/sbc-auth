<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">{{$t('createBCRegistriesAccount')}}</h1>
      <p class="mt-3 mb-0">Manage account settings, team members, and view account transactions</p>
    </div>
    <v-card flat>
      <Stepper :stepper-configuration="accountStepperConfig"></Stepper>
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
import UploadAffidavitStep from '@/components/auth/ExtraProv/UploadAffidavitStep.vue'
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
export default class ExtraProvincialAccountSetupView extends Vue {
  private accountStepperConfig: Array<StepConfiguration> =
    [
      {
        title: 'Select Account Type',
        stepName: 'Select Account Type',
        component: AccountTypeSelector,
        componentProps: {}
      },
      {
        title: 'Upload your notarized affidavit',
        stepName: 'Upload Affidavit',
        component: UploadAffidavitStep,
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
      }
    ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
