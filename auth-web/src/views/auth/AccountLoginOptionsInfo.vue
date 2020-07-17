<template>
    <v-container class="view-container">
        <div class="view-header flex-column mb-10">
            <h1 class="view-header__title">Before you get started</h1>
            <p class="mt-2 mb-3">It's important to understand the basic rules for users on your BC Registries
                account.</p>
        </div>
        <v-card
                class="step-card my-6"
                flat
                v-for="step in steps"
                :key="step.number"
        >
            <v-card-text class="pt-4 pb-4 pb-lg-5 px-6 px-lg-8 d-inline-flex align-center">
                <v-icon x-large color="blue-grey darken-1" class="step-icon mt-1 mr-7 ml-3">
                    {{step.icon}}
                </v-icon>
                <div>
                    <h2 class="mt-2 mb-4">{{step.stepTitle}}</h2>
                    <div v-html="step.stepDescription"></div>
                </div>
            </v-card-text>
        </v-card>
        <div class="d-flex justify-center mt-12 mb-4">
            <v-btn
              min-width="90"
              color="primary"
              class="font-weight-bold"
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
        stepTitle: 'Account administrators must log in with their BC Services Card',
        stepDescription: `<p>All account administrators are required to use the BC Services Card to verify their identity.
                            We do this to ensure that no one is impersonating you or committing identity theft.<p>`,
        icon: 'mdi-shield-account-outline'
      },
      {
        number: 2,
        stepTitle: 'Team Member Login Methods',
        stepDescription: `<p>As the preferred method of authentication, your team members do not need to remember passwords with the BC Services Card. 
                    Alternatively you can choose to have them login with a BCeID username and password, combined with a third-party authenticator app. 
                    These options are explained on the following page.</p>`,
        icon: 'mdi-account-group-outline'
      },
      {
        number: 3,
        stepTitle: 'Secure your account',
        stepDescription: '<p>Secure your account from fraudsters with 2-factor authentication.</p>',
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
