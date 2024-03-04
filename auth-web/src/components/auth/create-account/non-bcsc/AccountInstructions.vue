<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-10">
      <h1 class="view-header__title">
        How to verify your identity by a notary
      </h1>
      <p class="mt-5 mb-3">
        There are three steps to verifying and protecting your identity when creating a BC Registries account.
      </p>
    </div>
    <v-card
      v-for="step in steps"
      :key="step.number"
      class="step-card my-6"
      flat
    >
      <v-card-text class="pt-4 pb-4 pb-lg-5 px-6 px-lg-8 d-inline-flex align-center">
        <v-icon
          x-large
          color="blue-grey darken-1"
          class="step-icon mt-1 mr-12 ml-5"
        >
          {{ step.icon }}
        </v-icon>
        <div>
          <h2 class="mt-2 mb-4">
            {{ step.number }}.  {{ step.stepTitle }}
          </h2>
          <div v-html="step.stepDescription" />
        </div>
      </v-card-text>
    </v-card>
    <v-divider class="my-9" />
    <div class="d-flex">
      <v-btn
        large
        color="grey lighten-2"
        class="font-weight-bold"
        to="/choose-authentication-method"
      >
        <v-icon class="mr-2">
          mdi-arrow-left
        </v-icon>
        Back
      </v-btn>
      <v-spacer />
      <v-btn
        large
        color="primary"
        class="next-btn font-weight-bold"
        @click="goToDownload"
      >
        Next: Download Affidavit
        <v-icon class="ml-2">
          mdi-arrow-right
        </v-icon>
      </v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Pages } from '@/util/constants'

@Component
export default class AccountInstructions extends Vue {
  readonly steps = [
    {
      number: 1,
      stepTitle: 'Get an identity affidavit notarized',
      stepDescription: '<p>Visit your local notary or lawyer to have this document notarized. This is to ensure that ' +
        'no one is impersonating you or committing identity theft.</p><p><em>Only account administrators are ' +
        'required to verify their identity with a notary.</em><p>',
      icon: 'mdi-scale-balance'
    },
    {
      number: 2,
      stepTitle: 'Create a BCeID',
      stepDescription: '<p>A username and password that provides secure access to online government services in British Columbia.</p>',
      icon: 'mdi-account-circle-outline'
    },
    {
      number: 3,
      stepTitle: 'Use a 2-factor mobile or desktop authentication app',
      stepDescription: `<p>Mobile options such as: Google or Microsoft Authenticator<br />
      Desktop option such as: <a href="https://chrome.google.com/webstore/detail/gauth-authenticator/ilgcnhelpchnceeipipijaljkblbcobl?hl=en"` +
      `target="_sbc_google">GAuth</a></p>`,
      icon: 'mdi-cellphone-arrow-down'
    }
  ]

  goToDownload () {
    this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_DOWNLOAD}`)
    window.scrollTo(0, 0)
  }

  goBack () {
    this.$router.push(`/${Pages.HOME}`)
    window.scrollTo(0, 0)
  }
}
</script>

<style lang="scss" scoped>
  .view-container {
    max-width: 60rem;
  }

  .step-icon {
    align-self: flex-start;
    font-size: 3rem !important;
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
</style>
