<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-9">
      <h1 class="view-header__title" data-test="account-settings-title">Create a BC Registries and Online Services
        Account</h1>
      <div class="mt-4 view-header__subtitle">Choose how you want to log into your BC Registries account.</div>
    </div>
    <span text @click="showHelp = !showHelp" class="help-btn">
      <v-icon class="mr-1" color="primary">mdi-help-circle-outline</v-icon>
      <span v-if="!showHelp">Help me Choose</span>
      <span v-else>Hide Help</span>
    </span>
    <v-slide-y-transition>
      <div v-if="showHelp" class="help-info mb-10 mt-5 pb-16 pt-6">
        <div class="help-info__content mx-auto">
          <div class="help-info__header">Help with Choosing Login Option</div>
          <p class="mt-5">
            There are two ways to log into a BC Registries account:
          </p>

          <div class="bold-text">1) The BC Services Card</div>
          <div class="mt-4">
            The BC Services Card is a means of logging into BC government online services with a verified identity.
            You can use the BC Services Card app on a mobile device, or a username and password with the BC Services
            Card token (available at a
            <a :href="serviceBCURL" target="_blank" class="learn-more-link" rel="noopener noreferrer">
              Service BC location
              <v-icon color="primary" class="small-icon">mdi-open-in-new</v-icon>
            </a>).
          </div>
          <ul class="mt-4">
            <li>BC Services Card requires a one-time verification and can then be used for multiple government services.
            </li>
            <li>BC Services Card app is available to anyone with a Canadian-issued identification.</li>
            <li>Identity verification with a BC Services Card is performed through an online video call with a Service
              BC
              agent, or submission of a video recording to Service BC.</li>
            <li>If you don't have a mobile device, a BC Services Card token can be issued at a Service BC location.</li>
            <li>If you have already verified your identity with your services card, you can log in directly using the
              app or
              token.</li>
          </ul>
          <div class="mt-4">
            <a :href="serviceCardURL" target="_blank" class="learn-more-link" rel="noopener noreferrer">
              Learn more about the BC Services card
              <v-icon color="primary" class="small-icon">mdi-open-in-new</v-icon>
            </a>
          </div>

          <div class="bold-text mt-4">2) A BCeID</div>
          <div class="mt-4">
            A BCeID is an account that provides a username and password to allow secure electronic access to online
            government
            services.
          </div>
          <ul class="mt-4">
            <li>You can sign up for a BCeID when creating your BC Registries account or use an existing BCeID if you
              already have one.
            </li>
            <li>Your identity will need to be verified by obtaining a notorized affidavit from a notary or lawyer before
              you can
              access BC Registry services. Note: Most notaries and lawyers charge a fee for this service; fees will
              vary.</li>
            <li>The affidavit will need to be reviewed by BC Registries staff before it can be used.</li>
            <li>Logging in with a BCeID will require the use of a 3rd party application for 2-factor authentication
              (2FA).</li>
          </ul>
          <div class="mt-4">
            <a :href="bceIdURL" target="_blank" class="learn-more-link" rel="noopener noreferrer">
              Learn more about BCeID
              <v-icon color="primary" class="small-icon">mdi-open-in-new</v-icon>
            </a>
          </div>
        </div>

        <div class="bold-text mt-4">Canadian Government Agency (other than B.C. provincial)</div>
        <div class="mt-4 mb-6">
          If you are a member of a Canadian government agency (other than B.C. provincial), select the method you will
          use to login, and then check the box "I am a Canadian government agency". Once this has been reviewed by
          staff, you account will be authorized for government access.
        </div>

        <div class="help-info__close-btn-section">
          <span class="help-info__close-btn my-5" @click="showHelp = false">Hide help</span>
        </div>

      </div>
    </v-slide-y-transition>
    <div>
      <v-row>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card flat outlined hover class="account-card text-center pa-10 elevation-2 d-flex"
            @click="selectBCSCAuth()" :class="{'active': authType == 'BCSC'}">
            <div class="account-type d-flex flex-column">
              <div class="account-type__icon mb-4">
                <v-icon color="primary" class="account-card-icon">mdi-account-card-details-outline</v-icon>
              </div>
              <div class="account-type__title mb-6">
                BC Services Card
              </div>
              <div class="account-type__details mb-6">
                All Canadian citizens can use the BC Services Card app or token to log in.
                <div class="mt-6">
                  BC Services Card is the most common method of logging into a BC Registries account.
                </div>
              </div>
              <div class="mb-4">
                <a :href="serviceCardURL" target="_blank"
                  class="learn-more-link" rel="noopener noreferrer">
                  Learn more about the BC Services card
                  <v-icon color="primary" class="small-icon">mdi-open-in-new</v-icon>
                </a>
              </div>
              <div v-if="!disableGovnAccountCreation" class="mb-6">
                <v-checkbox color="primary" class="py-0 mt-2 align-checkbox-label--top" v-model="isGovNBCSC"
                  @click="openGovnWarningModal('BCSC')" hide-details>
                  <template v-slot:label>
                    I am a Canadian government agency (other than B.C. provincial)
                  </template>
                </v-checkbox>
                <div v-if="isGovNBCSC" class="gov-sccount-description mt-2"> {{ govnAccountDescription }} </div>
              </div>
              <!-- State Button (Create Account) -->
              <div class="mb-4">
                <v-btn large depressed block color="primary" class="font-weight-bold" :outlined="authType != 'BCSC'">
                  {{ authType == 'BCSC' ? 'Selected' : 'Select' }}
                </v-btn>
              </div>
              <!--<div class="notary-link">
                <router-link class="caption"  v-on:click.native="linkToNext" to="/nonbcsc-info">Verify with a notary instead</router-link>
              </div>-->
            </div>
          </v-card>
        </v-col>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card flat outlined hover class="account-card text-center pa-10 elevation-2 d-flex"
            @click="selectBCEIDAuth()" :class="{'active': authType == 'BCEID'}">
            <div class="account-type d-flex flex-column">
              <div class="account-type__icon mb-4">
                <v-icon color="primary" class="account-card-icon">mdi-certificate-outline</v-icon>
              </div>
              <div class="account-type__title mb-6">
                BCeID + 2FA
              </div>
              <div class="account-type__details mb-6">
                If you do not qualify to use the BC Services Card, you can use a BCeID to log into your BC Registries
                account.

                <div class="mt-6">
                  <span class="bold-text">Note:</span> Using a BCeID requires you to verify your identity with a
                  notarized affidavit, and to log in with
                  2-factor authentication (2FA).
                </div>
              </div>
              <div class="mb-4">
                <a :href="bceIdURL" target="_blank" class="learn-more-link" rel="noopener noreferrer">
                  Learn more about BCeID
                  <v-icon color="primary" class="small-icon">mdi-open-in-new</v-icon>
                </a>
              </div>
              <div v-if="!disableGovnAccountCreation" class="mb-6">
                <v-checkbox color="primary" class="py-0 mt-2 align-checkbox-label--top" v-model="isGovNBCeID"
                  @click="openGovnWarningModal('BCEID')" hide-details>
                  <template v-slot:label>
                    I am a Canadian government agency (other than B.C. provincial)
                  </template>
                </v-checkbox>
                <div v-if="isGovNBCeID" class="gov-sccount-description mt-2"> {{ govnAccountDescription }} </div>
              </div>
              <!-- State Button (Create Account) -->
              <div class="mb-4">
                <v-btn large depressed block color="primary" class="font-weight-bold" :outlined="authType != 'BCEID'">
                  {{ authType == 'BCEID' ? 'Selected' : 'Select' }}
                </v-btn>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>
    <v-divider class="mb-6 mt-1"></v-divider>
    <div class="form__btns d-flex mt-8">
      <v-btn color="primary" outlined @click="goPrevious()">
        Cancel
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn large color="primary" class="next-btn font-weight-bold" :disabled="authType ==''" @click="goNext()">
        Next
        <v-icon class="ml-2">
          mdi-arrow-right
        </v-icon>
      </v-btn>
    </div>
    <!-- Open GovN Account Modal -->
    <ModalDialog ref="govnConfirmModal" :title="govnConfirmModalTitle" :text="govnConfirmModalText"
      dialog-class="notify-dialog" max-width="680" :isPersistent="true" data-test="modal-govn-confirm">
      <template v-slot:icon>
        <v-icon large color="primary">mdi-help-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="confirmGovnCreateAccount()" data-test="btn-govn-confirm" class="mr-5 px-4">
          Confirm</v-btn>
        <v-btn large @click="closeConfirmModal()" data-test="btn-close-dialog" class="px-4">Cancel</v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { LDFlags, LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import ConfigHelper from '@/util/config-helper'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { mapGetters } from 'vuex'

@Component({
  components: {
    ModalDialog
  },
  computed: {
    ...mapGetters('auth', [
      'isAuthenticated',
      'currentLoginSource'
    ])
  }
})

export default class ChooseAuthMethodView extends Vue {
  private readonly isAuthenticated!: boolean
  private readonly currentLoginSource!: string
  private authType = ''
  private isGovNBCSC = false
  private isGovNBCeID = false
  private currCheckBox = ''
  private showHelp = false
  private govnConfirmModalTitle = 'Create Government Agency Account?'
  private govnConfirmModalText = this.$t('govnConfirmText')
  private govnAccountDescription = this.$t('govnAccountDescription')

  $refs: {
    govnConfirmModal: ModalDialog
  }

  private get serviceCardURL (): string {
    return 'https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card'
  }

  private get bceIdURL (): string {
    return 'https://www.bceid.ca/'
  }

  private get serviceBCURL (): string {
    return 'https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations/ministries/citizens-services/servicebc'
  }

  private get disableGovnAccountCreation (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.DisableGovNAccountCreation) || false
  }

  private selectBCSCAuth () {
    this.authType = LoginSource.BCSC
    if (this.isGovNBCeID) {
      this.isGovNBCeID = false
    }
  }

  private selectBCEIDAuth () {
    this.authType = LoginSource.BCEID
    if (this.isGovNBCSC) {
      this.isGovNBCSC = false
    }
  }

  private linkToNext () {
    ConfigHelper.addToSession(SessionStorageKeys.GOVN_USER, (this.isGovNBCSC || this.isGovNBCeID))
    ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'false')
  }

  private goPrevious () {
    this.$router.go(-1)
  }

  private goNext () {
    ConfigHelper.addToSession(SessionStorageKeys.GOVN_USER, (this.isGovNBCSC || this.isGovNBCeID))
    // TODO might need to set some session variables
    switch (this.authType) {
      case LoginSource.BCEID:
        ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'true')
        this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_INSTRUCTIONS}`)
        window.scrollTo(0, 0)
        break
      case LoginSource.BCSC:
        ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'false') // this flag shouldnt be used for bcsc users.still setting the right value
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

  private openGovnWarningModal (selection: string): void {
    this.currCheckBox = selection
    this.$refs.govnConfirmModal.open()
  }

  private confirmGovnCreateAccount (): void {
    this.$refs.govnConfirmModal.close()
    if (this.currCheckBox === LoginSource.BCSC) {
      this.isGovNBCSC = true
      this.isGovNBCeID = false
    } else if (this.currCheckBox === LoginSource.BCEID) {
      this.isGovNBCSC = false
      this.isGovNBCeID = true
    }
    this.currCheckBox = ''
  }

  private closeConfirmModal (): void {
    this.$refs.govnConfirmModal.close()
    // Set isGovn flag back to false
    if (this.currCheckBox === LoginSource.BCSC) {
      this.isGovNBCSC = false
      this.isGovNBCeID = false
    } else if (this.currCheckBox === LoginSource.BCEID) {
      this.isGovNBCeID = false
      this.isGovNBCSC = false
    }
    this.currCheckBox = ''
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.view-container {
  max-width: 60rem;
}

.col {
  padding: 1rem !important;
}

.account-card {
  display: flex;
  flex-direction: column;
  position: relative;
  background-color: #ffffff !important;
  transition: all ease-out 0.2s;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.active {
    box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0, 0, 0, .2), 0 2px 2px 0 rgba(0, 0, 0, .14), 0 1px 5px 0 rgba(0, 0, 0, .12) !important;
  }
}

.theme--light.v-card.v-card--outlined.active {
  border-color: var(--v-primary-base);
}

.account-card-icon {
  color: var(--v-grey-lighten1) !important;
  font-size: 3rem !important;
}

.account-card.active .v-icon {
  color: var(--v-primary-base) !important;
}

.account-type {
  flex: 1 1 auto;
}

.account-type__icon {
  flex: 0 0 auto;
}

.account-type__title {
  flex: 0 0 auto;
  line-height: 1.75rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: $gray9
}

.account-type__details {
  flex: 1 1 auto;
  font-size: $px-16;
  color: $gray7
}

.notary-link {
  position: absolute;
  left: 0;
  bottom: 1.5rem;
  width: 100%;
}

.lb {
  display: block;
}

.gov-sccount-description {
  color: $TextColorGray !important;
}

.learn-more-link {
  color: $app-blue;
  text-decoration: none;
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
