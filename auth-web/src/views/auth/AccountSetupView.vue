<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1 class="mb-5">Create Account</h1>
        <p class="intro-text">Please follow the steps below to create your account.</p>
        <v-card flat>
          <Stepper :stepper-configuration="stepperConfig"></Stepper>
        </v-card>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import Stepper, { StepConfiguration } from '@/components/auth/stepper/Stepper.vue'
import { mapActions, mapState } from 'vuex'
import AccountTypeSelector from '@/components/auth/CreateAccount/AccountTypeSelector.vue'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import CreateAccountInfoForm from '@/components/auth/CreateAccount/CreateAccountInfoForm.vue'
import LoginBCSC from '@/components/auth/LoginBCSC.vue'
import { Organization } from '@/models/Organization'
import { RouteConfig } from 'vue-router'
import { SessionStorageKeys } from '@/util/constants'
import StepperStub from '@/components/auth/stepper/StepperStub.vue'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import { getRoutes } from '@/router'
import { mount } from '@vue/test-utils'

@Component({
  components: {
    CreateAccountInfoForm,
    UserProfileForm,
    StepperStub,
    AccountTypeSelector,
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
        component: CreateAccountInfoForm,
        componentProps: {}
      },
      {
        title: 'User Profile',
        component: UserProfileForm,
        componentProps: {}
      }
    ]
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";
</style>
