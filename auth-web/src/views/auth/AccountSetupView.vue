<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1 class="mb-5">Create Account</h1>
        <p class="intro-text">Please follow the steps below to create your account.</p>
        <v-card class="profile-card">
          <v-stepper vertical v-model="currentStepNumber">
            <v-row>
              <v-col :cols="2">
                <v-stepper-step
                  v-for="step in steps"
                  :key="step.order"
                  :complete="currentStepNumber > step.order"
                  :step="step.order">
                  {{ step.title }}
                </v-stepper-step>
              </v-col>
              <v-col>
                <v-stepper-content :step="currentStepNumber">
                  <component :is="steps[currentStepNumber - 1].component" keep-alive transition="fade" mode="out-in" />
                </v-stepper-content>
              </v-col>
            </v-row>
          </v-stepper>
        </v-card>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import AccountInfo from '@/components/auth/AccountInfo.vue'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import LoginBCSC from '@/components/auth/LoginBCSC.vue'
import { RouteConfig } from 'vue-router'
import { SessionStorageKeys } from '@/util/constants'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import { getRoutes } from '@/router'

export interface StepConfiguration {
  title: string;
  order: number;
  component: string
  skipIf?: () => boolean
}

@Component({
  components: {
    AccountInfo,
    LoginBCSC,
    UserProfileForm
  },
  computed: {
    ...mapState('user', ['userProfile', 'userContact'])
  }
})
export default class AccountSetupView extends Vue {
  @Prop({ default: null }) stepConfiguration!: Array<StepConfiguration>
  private readonly userProfile!: User
  private readonly userContact!: Contact
  private steps: Array<StepConfiguration>

  private get defaultSteps (): Array<StepConfiguration> {
    return [
      {
        title: 'Log In',
        order: 1,
        component: 'LoginBCSC',
        skipIf: () => { return !!ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken) }
      },
      {
        title: 'User Profile',
        order: 2,
        component: 'UserProfileForm',
        skipIf: () => { return (this.userContact && this.userProfile?.userTerms?.isTermsOfUseAccepted) }
      },
      {
        title: 'Account Type',
        order: 3,
        component: null
      },
      {
        title: 'Account Settings',
        order: 4,
        component: 'AccountInfo'
      }
    ]
  }

  private currentStepNumber = 1

  private async beforeMount () {
    this.steps = this.stepConfiguration || this.defaultSteps

    // Check whether to skip , depending on whether user is logged in already, already has a profile.
    if (this.steps && this.steps.length > 0) {
      let currentStep = this.steps[this.currentStepNumber - 1]
      while (currentStep.skipIf && currentStep.skipIf()) {
        this.currentStepNumber++
        currentStep = this.steps[this.currentStepNumber - 1]
      }
    }
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  article {
    padding: 0;
  }
</style>
