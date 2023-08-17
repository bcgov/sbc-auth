<template>
    <v-container class="view-container">
        <div class="view-header flex-column mb-10">
          <h1 class="view-header__title">Before you get started</h1>
          <p class="mt-3 mb-3">It's important to understand the basic rules for users on your BC Registries account.</p>
        </div>
        <v-card flat class="pt-10 py-11 px-10">
          <section
            v-for="step in steps"
            :key="step.number"
          >
            <div class="d-flex">
              <div class="step-icon-container pr-6 text-center">
                <v-icon
                  x-large
                  color="blue-grey darken-1"
                  class="step-icon">
                  {{step.icon}}
                </v-icon>
              </div>
              <div>
                <h2 class="mb-4" v-html="step.stepTitle"></h2>
                <p class="mb-0" v-html="step.stepDescription"></p>
              </div>
            </div>
            <v-divider class="mt-10 mb-9"/>
          </section>
        </v-card>
        <div class="d-flex justify-center mt-12 mb-4">
          <v-btn
            large
            color="primary"
            class="action-btn font-weight-bold"
            to="/account-login-options-chooser"
          >
            OK
          </v-btn>
        </div>
    </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import { Pages } from '@/util/constants'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['currentOrganization'])
  }
})
export default class AccountLoginOptionsInfo extends Vue {
  private readonly steps = [
    {
      number: 1,
      stepTitle: 'Account administrators must log in with their <span class="lb">BC Services Card.</span>',
      stepDescription: `All account administrators are required to use the BC Services Card to verify their identity.
                          <span class="lb">We do this to ensure that no one is impersonating you or committing identity theft.</span>`,
      icon: 'mdi-shield-account-outline'
    },
    {
      number: 2,
      stepTitle: 'Team Member Login Methods',
      stepDescription: `As the preferred method of authentication, your team members do not need to remember passwords with the BC Services Card. 
                          Alternatively you can choose to have them login with a BCeID username and password, combined with a third-party authenticator app. 
                          These options are explained on the following page.`,
      icon: 'mdi-account-group-outline'
    },
    {
      number: 3,
      stepTitle: 'Secure your account',
      stepDescription: 'Secure your account from fraudsters with 2-factor authentication.',
      icon: 'mdi-two-factor-authentication'
    }
  ]

  private goToDownload () {
    this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_DOWNLOAD}`)
    window.scrollTo(0, 0)
  }

  private goBack () {
    this.$router.push(`/${Pages.HOME}`)
    window.scrollTo(0, 0)
  }
}
</script>

<style lang="scss" scoped>
  .view-container {
    max-width: 60rem;
  }

  .step-icon-container {
    flex: 0 0 auto;
    width: 7rem;
  }

  .step-icon {
    align-self: flex-start;
    font-size: 3rem !important;
  }

  h2 {
    line-height: 1.4;
  }

  @media (max-width: 599px) {
    .step-icon,
    .next-btn span {
      display: none !important;
    }

    .step-card h2 {
      font-size: 1.25rem;
    }
  }

  @media (min-width: 600px) {
    .lb {
        display: block;
    }
  }

  .action-btn {
    width: 6rem;
  }

  ::v-deep .lb {
    display: block;
  }

  section:last-child .v-divider {
    display: none;
  }
</style>
