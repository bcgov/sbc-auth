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
                  <component
                    :is="currentStep.component"
                    v-bind="currentStep.componentProps"
                    v-dynamic-events="currentStep.eventsToListenFor"
                    keep-alive
                    transition="fade"
                    mode="out-in" />
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
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import CreateAccountInfoForm from '@/components/auth/CreateAccountInfoForm.vue'
import LoginBCSC from '@/components/auth/LoginBCSC.vue'
import { Organization } from '@/models/Organization'
import { RouteConfig } from 'vue-router'
import { SessionStorageKeys } from '@/util/constants'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import { getRoutes } from '@/router'

export interface StepConfiguration {
  title: string;
  order: number;
  component: string
  componentProps: Record<string, any>
  skipIf?: () => boolean
  eventsToListenFor?: string[]
}

const DynamicEvents = {
  bind: (el, binding, vnode) => {
    const allEvents = binding.value
    allEvents.forEach((event) => {
      vnode.componentInstance.$on(event, (eventData) => {
        vnode.context.proxyEvent(event, eventData)
      })
    })
  },
  unbind: (el, binding, vnode) => {
    vnode.componentInstance.$off()
  }
}

@Component({
  components: {
    CreateAccountInfoForm,
    LoginBCSC,
    UserProfileForm
  },
  computed: {
    ...mapState('user', ['userProfile', 'userContact']),
    ...mapState('org', ['currentOrganization'])
  },
  directives: {
    DynamicEvents
  }
})
export default class AccountSetupView extends Vue {
  @Prop({ default: null }) stepConfiguration!: Array<StepConfiguration>
  private readonly currentOrganization!: Organization
  private readonly userProfile!: User
  private readonly userContact!: Contact
  private steps: Array<StepConfiguration>

  private get defaultSteps (): Array<StepConfiguration> {
    return [
      {
        title: 'Log In',
        order: 1,
        component: 'LoginBCSC',
        componentProps: {},
        skipIf: () => { return !!ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken) }
      },
      {
        title: 'User Profile',
        order: 2,
        component: 'UserProfileForm',
        componentProps: { redirectOnSave: false }, // We want to stay on the stepper view after save
        skipIf: () => { return (this.userContact && this.userProfile?.userTerms?.isTermsOfUseAccepted) },
        eventsToListenFor: ['profile-saved']
      },
      {
        title: 'Account Settings',
        order: 3,
        component: 'CreateAccountInfoForm',
        componentProps: {},
        eventsToListenFor: ['account-saved']
      }
    ]
  }

  private get currentStep (): StepConfiguration {
    return this.steps.find(step => step.order === this.currentStepNumber)
  }

  private currentStepNumber = 1

  // Handle completed steps
  private proxyEvent (eventName: string, eventData: any) {
    if (this.currentStepNumber >= this.steps.length) {
      this.$router.push({ path: `/account/${this.currentOrganization.id}/` })
    } else {
      this.currentStepNumber++
    }
  }

  private async beforeMount () {
    this.steps = this.stepConfiguration || this.defaultSteps

    // Check whether to skip
    if (this.steps && this.steps.length > 0) {
      while (this.currentStep.skipIf && this.currentStep.skipIf()) {
        this.currentStepNumber++
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
