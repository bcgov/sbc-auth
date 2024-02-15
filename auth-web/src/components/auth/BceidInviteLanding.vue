<template>
  <v-container class="view-container">
    <template v-if="!inviteError">
      <!-- Loading status -->
      <v-fade-transition>
        <div
          v-if="isLoading"
          class="loading-container"
        >
          <v-progress-circular
            size="50"
            width="5"
            color="primary"
            :indeterminate="isLoading"
          />
        </div>
      </v-fade-transition>
      <div
        v-if="!isLoading"
        class="mt-2"
      >
        <div class="view-header flex-column mb-10">
          <h1 class="view-header__title">
            Log in to BC Registries using BCeID
          </h1>
          <p class="my-3">
            There are a couple of things you'll need to do before logging into BC Registries using BCeID.
          </p>
        </div>
        <v-card
          class="step-card my-6"
          flat
        >
          <div
            v-for="step in steps"
            :key="step.number"
          >
            <v-card-text
              class="pt-4 pb-4 pb-lg-5 px-6 px-lg-8 d-inline-flex align-start"
            >
              <v-icon class="step-icon mr-8 ml-3">
                {{ step.icon }}
              </v-icon>
              <div>
                <h2 class="mt-2 mb-4">
                  {{ step.stepTitle }}
                </h2>
                <div v-html="step.stepDescription" />
              </div>
            </v-card-text>
            <div class="d-flex flex-row mx-9 align-center">
              <v-divider class="" />
              <v-icon class="divider-icon mx-2 mt-1">
                mdi-arrow-down
              </v-icon>
              <v-divider class="" />
            </div>
          </div>
          <div class="d-flex justify-center align-center pt-8 pb-10">
            <v-btn
              min-width="100"
              color="primary"
              class="next-btn font-weight-bold"
              @click="registerForBceid()"
            >
              Register
            </v-btn>
            <div class="mx-4 font-weight-bold">
              OR
            </div>
            <v-btn
              min-width="100"
              color="primary"
              class="next-btn font-weight-bold"
              @click="loginWithBceid"
            >
              Login
            </v-btn>
          </div>
        </v-card>
      </div>
    </template>
    <div v-else>
      <InterimLanding
        :summary="$t('errorOccurredTitle')"
        :description="$t('invitationProcessingErrorMsg')"
        icon="mdi-alert-circle-outline"
        iconColor="error"
      />
    </div>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { SessionStorageKeys } from '@/util/constants'

export default defineComponent({
  name: 'BceidInviteLanding',
  components: {
    InterimLanding
  },
  props: {
    token: {
      type: String,
      default: null
    },
    orgName: {
      type: String,
      default: ''
    }
  },
  setup (props, { root }): any {
    const isLoading = ref(true)
    const inviteError = ref(false)
    const steps = ref([
      {
        number: 1,
        stepTitle: 'Register or use an existing BCeID account',
        stepDescription: '<p>A BCeID account provides secure access to online government services in British Columbia.\n' +
                'You can register a new BCeID or use an existing BCeID account to log into BC Registries.</p>',
        icon: 'mdi-account-plus-outline'
      },
      {
        number: 2,
        stepTitle: 'Use a 2-factor mobile or desktop authentication app',
        stepDescription: `<p>Secure your account using a 2-factor authentication app with your BCeID when you log in. 
        Download a 2-factor authentication app to your smartphone such as FreeOTP, Google Authenticator or 
        Microsoft Authenticator or Desktop options such as: 
        <a href="https://authy.com/" target="_sbc">Authy</a> or 
        <a href="https://chrome.google.com/webstore/detail/gauth-authenticator/` +
        `ilgcnhelpchnceeipipijaljkblbcobl?hl=en" target="_sbc_google">GAuth</a>.</p>`,
        icon: 'mdi-two-factor-authentication'
      }
    ])

    function registerForBceid () {
      setStorage()
      window.location.href = ConfigHelper.getBceIdOsdLink()
    }

    function loginWithBceid () {
      setStorage()
      root.$router.push('/signin/bceid/')
    }

    function setStorage () {
      ConfigHelper.addToSession(SessionStorageKeys.InvitationToken, props.token)
    }

    const showErrorOccured = () => {
      inviteError.value = true
    }

    onMounted(() => {
      isLoading.value = false
    })

    return {
      isLoading,
      inviteError,
      steps,
      registerForBceid,
      loginWithBceid,
      setStorage,
      showErrorOccured
    }
  }
})
</script>

<style lang="scss" scoped>
   @import '$assets/scss/theme.scss';

  .view-container {
    max-width: 60rem;
  }

  .v-card__title {
    font-weight: 700;
    letter-spacing: -0.02rem;
  }

  .step-icon {
    font-size: 3.6rem !important;
    color: $BCgovBlue4 !important;
  }

  .divider-icon {
    color: $BCgovBlue4 !important;
  }

  .user-profile-header {
    flex-direction: column;
  }
</style>
