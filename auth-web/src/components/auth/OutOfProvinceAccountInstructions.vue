<template>
  <div class="d-flex justify-center pa-4">
    <div class="non-bc-instructions-container">
      <h1 class="my-5">
        In order to create a BC Registries account,
        we need to verify your identity.
      </h1>
      <p class="mb-5 mt-7">
        We do this to ensure that no one is impersonating you or committing identity theft.
      </p>
      <p class="mb-8">
        There are three steps to verifying and protecting your identity when creating a BC Registries account.
      </p>
      <v-card
        class="my-4"
        flat
        v-for="step in steps"
        :key="step.number"
      >
        <v-card-text class="d-inline-flex align-center">
          <div class="px-6 py-2">
            <v-icon x-large color="blue-grey darken-1">
              {{step.icon}}
            </v-icon>
          </div>
          <div class="px-2">
            <h4>
              {{step.number}}.  {{step.stepTitle}}
            </h4>
            <p class="mb-0">
              {{step.stepDescription}}
            </p>
          </div>
        </v-card-text>
      </v-card>
      <div class="d-flex mt-12 mb-6">
        <v-btn
          class="font-weight-bold"
          color="grey lighten-2"
          depressed
          large
          @click="goBack"
        >
          <v-icon class="mr-2">
            mdi-arrow-left
          </v-icon>
          Back
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          class="font-weight-bold"
          color="primary"
          depressed
          large
          @click="goToDownload"
        >
          Continue: Download Affidavit
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Pages } from '@/util/constants'

@Component
export default class OutOfProvinceAccountInstructions extends Vue {
  private readonly steps = [
    {
      number: 1,
      stepTitle: 'Get an identity affidavit notarized',
      stepDescription: 'Visit your local notary or lawyer to have this document notarized.',
      icon: 'mdi-scale-balance'
    },
    {
      number: 2,
      stepTitle: 'Create a BCeID',
      stepDescription: 'A username and password that provides secure access to online government services in British Columbia.',
      icon: 'mdi-account-circle-outline'
    },
    {
      number: 3,
      stepTitle: 'Use a 2-factor authentication app',
      stepDescription: 'Download and use an app, such as Google or Microsoft Authenticator.',
      icon: 'mdi-cellphone-iphone'
    }
  ]

  private goToDownload () {
    this.$router.push(`/${Pages.SETUP_ACCOUNT_OUT_OF_PROVINCE}/${Pages.SETUP_ACCOUNT_OUT_OF_PROVINCE_DOWNLOAD}`)
  }

  private goBack () {
    this.$router.push(`/${Pages.HOME}`)
  }
}
</script>

<style lang="scss" scoped>
.non-bc-instructions-container {
  max-width: 660px;
}
</style>
