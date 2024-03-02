<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-9">
      <h1
        class="view-header__title"
        data-test="account-settings-title"
      >
        Create a BC Registries and Online Services
        Account
      </h1>
      <div class="mt-4 view-header__subtitle">
        You can log into your BC Registries account by using:
      </div>
    </div>
    <div class="mb-9">
      <v-card class="service-container">
        <header class="d-flex align-center">
          <div class="login-icon-container mt-n2">
            <v-icon
              x-large
              class="account-card-icon"
            >
              mdi-account-card-details
            </v-icon>
          </div>
          <div class="pr-8">
            <h3 class="title font-weight-bold payment-title mt-n1">
              BC Service Card
            </h3>
            <div>Easy and secure way to access your account</div>
          </div>
          <v-btn
            id="bcsc-login"
            large
            width="120"
            class="action-btn px-5 ml-auto"
            color="primary"
            :depressed="true"
            @click="goNext(LoginSource.BCSC)"
          >
            <span>Login</span>
            <v-icon class="pl-1">
              mdi-chevron-right
            </v-icon>
          </v-btn>
        </header>
      </v-card>
    </div>
    <div class="mb-6">
      No BC Services Card account? <a
        :href="bcTokenURL"
        target="_blank"
        class="learn-more-link"
        rel="noopener noreferrer"
      >Learn how to set up a BC Services Card account<v-icon
        color="primary"
        class="small-icon"
      > mdi-open-in-new</v-icon></a><br>
      If you have <a
        :href="bcscInfoURL"
        target="_blank"
        class="learn-more-link"
        rel="noopener noreferrer"
      >ID issued in Canada<v-icon
        color="primary"
        class="small-icon"
      > mdi-open-in-new</v-icon></a> this login method is an easy and secure way to access your account.
    </div>
    <div class="mb-9">
      <span
        text
        class="help-btn"
        @click="showHelpBCSC = !showHelpBCSC"
      >
        <v-icon
          class="mr-1"
          color="primary"
        >mdi-help-circle-outline</v-icon>
        <span v-if="!showHelpBCSC">More Help</span>
        <span v-else>Hide Help</span>
      </span>
    </div>
    <v-slide-y-transition>
      <div
        v-if="showHelpBCSC"
        class="help-info mb-10 mt-5 pb-16 pt-6"
      >
        <div class="help-info__content mx-auto">
          <div class="help-info__header">
            BC Services Card Login
          </div>
          <div class="mt-4">
            The BC Services Card login is a means of logging into BC government online services with a verified identity. You can
            use the BC Services Card mobile app, or an email and password with the BC token (available to BC Residents).
          </div>
          <ul class="mt-4">
            <li>
              BC Services Card login requires a one-time verification and can then
              be used for multiple government services.
            </li>
            <li>
              BC Services Card app is available to anyone with a <a
                :href="idURL"
                target="_blank"
                class="learn-more-link"
                rel="noopener noreferrer"
              >Canadian-issued identification<v-icon
                color="primary"
                class="small-icon"
              >mdi-open-in-new</v-icon></a>.
            </li>
            <li>
              Identity verification for the BC Services Card app is performed through an online video call with a
              Service BC agent, or submission of a video recording to Service BC.
            </li>
            <li>
              The only personal information shared with BC Registries is your first and last name which
              is used for digital signatures when you submit filings.
            </li>
            <li>
              If you don't have a mobile device, or prefer not to use one, a BC Token can be issued at a Service BC
              location (available to BC Residents). Identity verification for the BC token is performed in person.
            </li>
            <li>If you have already verified your identity, you can log in directly using the app or token.</li>
          </ul>
          <div class="mt-4">
            <a
              :href="serviceCardURL"
              target="_blank"
              class="learn-more-link"
              rel="noopener noreferrer"
            >
              Learn more about the BC Services Card Login
              <v-icon
                color="primary"
                class="small-icon"
              >mdi-open-in-new</v-icon>
            </a>
          </div>
        </div>
        <div class="help-info__close-btn-section">
          <span
            class="help-info__close-btn my-5"
            @click="showHelpBCSC = false"
          >Hide help</span>
        </div>
      </div>
    </v-slide-y-transition>
    <v-divider class="mb-6 mt-1" />
    <div>
      <header class="d-flex align-center">
        <span>Other login options if you do not have ID issued in Canada</span>
        <v-btn
          depressed
          color="primary"
          width="120"
          class="font-weight-bold ml-auto"
          text
          @click="showBCeIDOption = !showBCeIDOption"
        >
          <span
            v-if="showBCeIDOption"
          > View Less
            <v-icon
              meduim
              color="primary"
            >mdi-chevron-up</v-icon>
          </span>
          <span
            v-else
          >View More<v-icon
            meduim
            color="primary"
          >mdi-chevron-down</v-icon></span>
        </v-btn>
      </header>

      <v-expand-transition v-if="showBCeIDOption">
        <div class="mt-9">
          <div class="mb-9">
            <v-card class="service-container">
              <header class="d-flex align-center">
                <div class="login-icon-container mt-n2">
                  <v-icon
                    x-large
                    class="account-card-icon"
                  >
                    mdi-certificate
                  </v-icon>
                </div>
                <div class="pr-8">
                  <h3 class="title font-weight-bold payment-title mt-n1">
                    BCeID Login + Two-Factor Authentication
                  </h3>
                  <div>
                    <v-icon
                      small
                      class="account-type__details mt-n1"
                    >
                      mdi-clock-outline
                    </v-icon>
                    Require identity verification, the approximate processing time is 8-10 days
                  </div>
                </div>
                <v-btn
                  id="bceid-login"
                  large
                  width="120"
                  class="action-btn px-5 ml-auto"
                  color="primary"
                  :depressed="true"
                  @click="goNext(LoginSource.BCEID)"
                >
                  <span>Next</span>
          <v-icon class="pl-1">
                  mdi-chevron-right
                  </v-icon>
                </v-btn>
              </header>
            </v-card>
          </div>
          <div class="mb-9">
            <a
              :href="bceIdURL"
              target="_blank"
              class="learn-more-link"
              rel="noopener noreferrer"
            >
              Learn more about BCeID
              <v-icon
                color="primary"
                class="small-icon"
              >mdi-open-in-new</v-icon>
            </a>
          </div>
          <div class="mb-6">
            <span
              text
              class="help-btn"
              @click="showHelpBCeID = !showHelpBCeID"
            >
              <v-icon
                class="mr-1"
                color="primary"
              >mdi-help-circle-outline</v-icon>
              <span v-if="!showHelpBCeID">More Help</span>
              <span v-else>Hide Help</span>
            </span>
          </div>
          <v-slide-y-transition>
            <div
              v-if="showHelpBCeID"
              class="help-info mb-10 mt-5 pb-16 pt-6"
            >
              <div class="help-info__content mx-auto">
                <div class="help-info__header">
                  BCeID Login + Two-Factor Authentication
                </div>
                <div class="mt-4">
                  A BCeID is an account that provides a username and password to allow secure electronic access to online
                  government services.
                </div>
                <ul class="mt-4">
                  <li>
                    You can sign up for a BCeID when creating your BC Registries account or use an existing BCeID if you
                    already have one.
                  </li>
                  <li>
                    Your identity will need to be verified by obtaining a notarized affidavit from a notary or lawyer before
                    you can access BC Registry services. Note: Most notaries and lawyers charge a fee for this service; fees will
                    vary.
                  </li>
                  <li>The affidavit will need to be reviewed by BC Registries staff before it can be used.</li>
                  <li>
                    Logging in with a BCeID will require the use of a 3rd party application for 2-factor authentication (2FA) on a
                    mobile device or on a desktop computer.
                  </li>
                </ul>
                <div class="mt-4">
                  <a
                    :href="bceIdURL"
                    target="_blank"
                    class="learn-more-link"
                    rel="noopener noreferrer"
                  >
                    Learn more about BCeID
                    <v-icon
                      color="primary"
                      class="small-icon"
                    >mdi-open-in-new</v-icon>
                  </a>
                </div>
              </div>
              <div class="help-info__close-btn-section">
                <span
                  class="help-info__close-btn my-5"
                  @click="showHelpBCeID = false"
                >Hide help</span>
              </div>
            </div>
          </v-slide-y-transition>
        </div>
      </v-expand-transition>
      <div />
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import ConfigHelper from '@/util/config-helper'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
// Remove with Vue3 upgrade.
import { mapGetters } from 'vuex'

@Component({
  components: {
    ModalDialog
  },
  computed: {
    ...mapGetters('auth', [
      'isAuthenticated',
      'currentLoginSource'
    ]),
    LoginSource: () => LoginSource
  }
})
export default class ChooseAuthMethodView extends Vue {
  private readonly isAuthenticated!: boolean
  private readonly currentLoginSource!: string
  authType = ''
  currCheckBox = ''
  showHelpBCSC = false
  showHelpBCeID = false
  showBCeIDOption = false

  $refs: {
    govnConfirmModal: InstanceType<typeof ModalDialog>
  }

  get serviceCardURL (): string {
    return 'https://id.gov.bc.ca/'
  }

  get bceIdURL (): string {
    return 'https://www.bceid.ca/'
  }

  get idURL (): string {
    return 'https://www2.gov.bc.ca/gov/content?id=5F8782A92E464066885149242E050814'
  }

  get bcTokenURL (): string {
    return 'https://id.gov.bc.ca/account/setup-instruction'
  }

  get serviceCardLearnMoreURL (): string {
    return 'https://id.gov.bc.ca/'
  }

  get bcscInfoURL (): string {
    return 'https://www2.gov.bc.ca/gov/content/governments/government-id/bcservicescardapp/id'
  }

  goNext (authType: LoginSource) {
    switch (authType) {
      case LoginSource.BCEID:
        ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'true')
        this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_INSTRUCTIONS}`)
        window.scrollTo(0, 0)
        break
      case LoginSource.BCSC:
        // this flag shouldnt be used for bcsc users.still setting the right value
        ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'false')
        if (this.isAuthenticated) {
          if (this.currentLoginSource === LoginSource.BCEID) {
            this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}`)
          } else {
            this.$router.push(`/${Pages.CREATE_ACCOUNT}`)
          }
        } else {
          this.$router.push(`/signin/bcsc/${Pages.CREATE_ACCOUNT}`)
        }
        break
    }
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.service-container {
  border-left: 3px solid transparent;
  cursor: pointer;
  max-width: none;
  padding: 24px;

  &:hover {
    border-left: 3px solid $app-blue !important;
    box-shadow: 1px 1px 6px 0px $gray6;
  }
}
.login-icon-container {
  flex: 0 0 auto;
  width: 4.5rem;
}

.view-container {
  max-width: 60rem;
}

.col {
  padding: 1rem !important;
}

.theme--light.v-card.v-card--outlined.active {
  border-color: var(--v-primary-base);
}

.account-card-icon {
  color: $app-dk-blue !important;
}

.account-type__details {
  flex: 1 1 auto;
  font-size: $px-16;
  color: $gray7 !important;
  top:0;
}

.learn-more-link {
  color: $app-blue;
  text-decoration: none;
  text-decoration: underline;
}

.small-icon {
  font-size: 18px !important
}

.bold-text {
  font-weight: bold
}

.help-info {
  border-bottom: 1px dotted $gray7;
  border-top: 1px dotted $gray7;
  padding-bottom: 1rem;

  &__content {
    &__link {
      color: $app-blue;
      white-space: nowrap;
      text-decoration: none;

      &__icon {
        font-size: 1rem;
        color: $app-blue;
      }
    }
  }

  &__header {
    text-align: center;
    font-weight: bold;
    color: $gray9;
  }

  &__close-btn-section {
    text-align: end;
  }

  &__close-btn {
    color: $app-blue;
    cursor: pointer;
    font-size: .875rem;
    text-decoration: underline;
    white-space: nowrap;
  }
}

.help-btn {
  font-size: $px-16;
  cursor: pointer;
  text-align: right;
  color: $app-blue;
}
</style>
