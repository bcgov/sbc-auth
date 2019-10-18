<template>
  <div class="passcode-form">
    <v-form ref="form" lazy-validation>
      <v-expand-transition>
        <div class="passcode-form__alert-container" v-show="loginError">
          <v-alert type="error" class="mb-0" :value="true"
          >{{loginError}}
          </v-alert>
        </div>
      </v-expand-transition>
      <v-text-field
        filled
        label="Enter your Incorporation Number"
        hint="Example: CP1234567"
        req
        persistent-hint
        :rules="entityNumRules"
        v-model="businessIdentifier"
      ></v-text-field>
      <v-text-field
        :append-icon="showPasscode ? 'visibility' : 'visibility_off'"
        :type="showPasscode ? 'text' : 'password'"
        @click:append="showPasscode = !showPasscode"
        filled
        label="Enter your Passcode"
        hint="Passcode must be exactly 9 digits"
        persistent-hint
        :rules="entityPasscodeRules"
        :maxlength="9"
        v-model="passcode"
      ></v-text-field>
      <div class="form__btns mt-6">
        <v-btn text large color="primary" class="recovery-btn" @click.stop="noPasscodeDialog = true">
          Don't have a Passcode?
        </v-btn>
        <v-btn large color="primary" class="sign-in-btn" @click="login"
          :loading="showSpinner"
          :disabled="showSpinner">
          <span>{{showSpinner ? 'Signing in' : 'Sign In'}}</span>
          <v-icon dark right v-if="!showSpinner">arrow_forward</v-icon>
        </v-btn>
      </div>
    </v-form>
    <v-dialog max-width="640" v-model="noPasscodeDialog">
      <v-card>
        <v-card-title>Don't have a Passcode?</v-card-title>
        <v-card-text class="pt-8">
          <p>If you have not received, or have lost your Passcode, please contact us at:</p>
          <ul class="contact-info">
            <li class="contact-info__row">
              <span class="contact-info__type">Phone:</span>
              <span class="contact-info__value">{{ $t('techSupportPhone') }}</span>
            </li>
            <li class="contact-info__row">
              <span class="contact-info__type">Email:</span>
              <span class="contact-info__value"><a v-bind:href="'mailto:' + $t('techSupportEmail')">{{ $t('techSupportEmail') }}</a></span>
            </li>
          </ul>
        </v-card-text>
        <v-card-actions>
          <v-btn text color="primary"
            @click="noPasscodeDialog = false"
          >Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import BusinessModule from '@/store/modules/business'
import ConfigHelper from '@/util/config-helper'
import { SessionStorageKeys } from '@/util/constants'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component
export default class PasscodeForm extends Vue {
  showPasscode = false
  showSpinner = false
  noPasscodeDialog = false
  loginError = ''
  valid = false
  VUE_APP_COPS_REDIRECT_URL = ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  entityNumRules = [
    v => !!v || 'Incorporation Number is required'
  ]
  entityPasscodeRules = [
    v => !!v || 'Passcode is required',
    v => v.length >= 9 || 'Passcode must be exactly 9 digits'
  ]
  businessStore = getModule(BusinessModule, this.$store)

  businessIdentifier: string = ''
  passcode: string = ''

  private isFormValid (): boolean {
    return (this.$refs.form as Vue & { validate: () => boolean }).validate()
  }

  private getIFrameContent (): Window {
    return (this.$refs.iframeContent as Vue & { contentWindow: Window }).contentWindow
  }

  private redirectToNext (): void {
    if ((this.businessStore.currentBusiness.contacts &&
         this.businessStore.currentBusiness.contacts.length > 0) || this.businessStore.skippedContactEntry) {
      // transition to co-ops UI as we already have a contact set (or user has opted to skip already in this session)
      window.location.href = configHelper.getCoopsURL()
    } else {
      // transition to business contact UI
      this.$router.push('/businessprofile')
    }
  }

  mounted () {
    if (sessionStorage.getItem('KEYCLOAK_TOKEN')) {
      this.redirectToNext()
    }
  }

  login () {
    if (this.isFormValid()) {
      this.showSpinner = true
      this.businessStore.login({ businessIdentifier: this.businessIdentifier, passCode: this.passcode })
        .then(response => {
          // set token and store in storage
          ConfigHelper.addToSession(SessionStorageKeys.KeyCloakToken, response.data.access_token)
          ConfigHelper.addToSession(SessionStorageKeys.KeyCloakRefreshToken, response.data.refresh_token)
          sessionStorage.REGISTRIES_TRACE_ID = response.data['registries-trace-id']
          sessionStorage.LOGIN_TYPE = 'passcode'
          ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, this.businessIdentifier)

          // attempt to load business
          this.businessStore.createBusinessIfNotFound(this.businessIdentifier)
            .then(() => {
              this.redirectToNext()
            })
        })
        .catch(response => {
          this.loginError = response.response.data.message
          this.showSpinner = false
        })
    }
  }
}
</script>

<style lang="scss" scoped>
  @import '../../assets/scss/theme.scss';

  .form__btns {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
  }

  .v-btn.recovery-btn {
    margin-right: auto;
    padding-right: 0.7rem;
    padding-left: 0.7rem;
    text-decoration: underline;
  }

  .v-btn.sign-in-btn {
    min-width: 10rem;
    font-weight: 700;
  }

  .v-input {
    max-width: 25rem;
  }

  .passcode-form__alert-container {
    margin-bottom: 2.25rem;
  }

  @media (max-width: 600px) {
    .passcode-form__form-btns {
      flex-flow: column nowrap;
    }

    .v-btn.recovery-btn {
      order: 1;
      margin-top: 0.5rem;
      margin-left: auto;
    }

    .v-btn.sign-in-btn {
      width: 100%;
    }
  }

  // Passcode Dialog
  .v-card__title {
    padding: 1.25rem 1.5rem;
    color: $BCgovFontColorInverted;
    background: $BCgovBlue5;
    font-size: 1.5em;
    font-weight: 400;
  }

  .v-card__text {
    padding: 1.5rem;
    font-weight: 300;
  }

  .v-card__actions {
    justify-content: flex-end;
  }

  // Contact Info
  .contact-info {
    margin-top: 1.5rem;
    padding: 0;
    font-weight: 500;
    list-style-type: none;
  }

  .contact-info__row {
    display: flex;
    align-items: flex-start;
  }

  .contact-info__type {
    flex: 0 0 auto;
    min-width: 4rem;
    overflow: hidden;
    letter-spacing: -0.02rem;
    font-weight: 700;
  }

  .contact-info__value {
    flex: 1 1 auto;
    overflow: hidden;
  }
</style>
