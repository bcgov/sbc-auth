<template>
  <v-container class="view-container">
    <template v-if="!inviteError">
      <!-- Loading status -->
      <v-fade-transition>
        <div class="loading-container" v-if="isLoading">
          <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
        </div>
      </v-fade-transition>
      <div class="user-profile-container" v-if="!isLoading">
        <v-container class="view-container">
          <div class="view-header flex-column mb-10">
            <h1 class="view-header__title">Log in to BC Registries using BCeID</h1>
            <p class="mt-5 mb-3">There are a couple of things you'll need to do before logging into BC Registries using BCeID.</p>
          </div>
          <v-card
                  class="step-card my-6"
                  flat
                  v-for="step in steps"
                  :key="step.number"
          >
            <v-card-text class="pt-4 pb-4 pb-lg-5 px-6 px-lg-8 d-inline-flex align-center">
              <v-icon x-large color="blue-grey darken-1" class="step-icon mt-1 mr-12 ml-5">
                {{step.icon}}
              </v-icon>
              <div>
                <h2 class="mt-2 mb-4">{{step.number}}.  {{step.stepTitle}}</h2>
                <div v-html="step.stepDescription"></div>
              </div>
            </v-card-text>
          </v-card>
          <v-divider class="my-9"></v-divider>
          <div class="d-flex justify-center align-center">
            <v-btn
                    large
                    color="primary"
                    class="next-btn font-weight-bold"
                    @click="registerForBceid()"
            >
              Register
              <v-icon class="ml-2">
                mdi-arrow-right
              </v-icon>
            </v-btn>
            OR
            <v-btn
                    large
                    color="primary"
                    class="next-btn font-weight-bold"
                    @click="loginWithBceid"
            >
              Login
              <v-icon class="ml-2">
                mdi-arrow-right
              </v-icon>
            </v-btn>
          </div>
        </v-container>
      </div>
    </template>
    <div v-else>
      <interim-landing :summary="$t('errorOccurredTitle')" :description="$t('invitationProcessingErrorMsg')" icon="mdi-alert-circle-outline" iconColor="error">
      </interim-landing>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import CreateUserProfileForm from '@/components/auth/CreateUserProfileForm.vue'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import { SessionStorageKeys } from '@/util/constants'
import Vue from 'vue'

@Component({
  components: {
    CreateUserProfileForm,
    InterimLanding
  }
})
export default class BceidInviteLanding extends Vue {
  private isLoading = true
  private inviteError = false
  private readonly steps = [
    {
      number: 1,
      stepTitle: 'Register or use an existing BCeID account',
      stepDescription: '<p>A BCeID account provides secure access to online government services in British Columbia.\n' +
              'You can register a new BCeID or use an existing BCeID account to log into BC Registries.</p>',
      icon: 'mdi-account-circle-outline'
    },
    {
      number: 2,
      stepTitle: 'Use a 2-factor authentication app',
      stepDescription: '<p>Secure your account using a 2-factor authentication app with your BCeID when you log in. Download a 2-factor authentication app to your smartphone such as FreeOTP, Google Authenticator or Microsoft Authenticator.</p>',
      icon: 'mdi-cellphone-arrow-down'
    }
  ]

  @Prop() token: string
  @Prop({ default: '' }) orgName: string

  private registerForBceid () {
    ConfigHelper.addToSession(SessionStorageKeys.InvitationToken, this.token)
    window.location.href = ConfigHelper.getBceIdOsdLink()
  }
  private loginWithBceid () {
    ConfigHelper.addToSession(SessionStorageKeys.InvitationToken, this.token)
    this.$router.push('/signin/bceid/')
  }

  private async mounted () {
    this.isLoading = false
  }

  private showErrorOccured () {
    this.inviteError = true
  }
}
</script>

<style lang="scss" scoped>
   @import '$assets/scss/theme.scss';

  .v-card__title {
    font-weight: 700;
    letter-spacing: -0.02rem;
  }

  .user-profile-header {
    flex-direction: column;
  }
</style>
