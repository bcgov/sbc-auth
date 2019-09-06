<template>
  <div class="passcode-form">
    <v-form ref="form" lazy-validation>
      <v-expand-transition>
        <div class="passcode-form__alert-container" v-show="loginError">
          <v-alert
            :value="true"
            color="error"
            icon="warning"
          >{{loginError}}
          </v-alert>
        </div>
      </v-expand-transition>
      <div class="passcode-form__row">
        <v-text-field
          filled
          label="Enter your Incorporation Number"
          hint="Example: CP1234567"
          req
          persistent-hint
          :rules="entityNumRules"
          v-model="businessNumber"
        ></v-text-field>
      </div>
      <div class="passcode-form__row">
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
      </div>
      <div class="passcode-form__row passcode-form__form-btns">
        <v-btn class="recovery-btn" color="primary" text large @click.stop="noPasscodeDialog = true">
          Don't have a Passcode?
        </v-btn>
        <v-btn class="sign-in-btn" @click="login" color="primary" large>
          <v-progress-circular :indeterminate="true" size="20" width="2" v-if="showSpinner"></v-progress-circular>
          <span>{{showSpinner ? 'Signing in' : 'Sign In'}}</span>
          <v-icon dark right v-if="!showSpinner">arrow_forward</v-icon>
        </v-btn>
      </div>
    </v-form>
    <v-dialog width="50rem" v-model="noPasscodeDialog">
      <v-card>
        <v-card-title>Don't have a Passcode?</v-card-title>
        <v-divider></v-divider>
        <v-card-text>
          If you have not received, or have lost your Passcode, please contact us at:
          <ul class="contact-list">
            <li class="contact-list__row">
              <v-icon color="primary">phone</v-icon>
              <span class="contact-info__value">{{ $t('techSupportPhone') }}</span>
            </li>
            <li class="contact-list__row">
              <v-icon color="primary">email</v-icon>
              <span class="contact-info__value"><a v-bind:href="'mailto:' + $t('techSupportEmail')">{{ $t('techSupportEmail') }}</a></span>
            </li>
          </ul>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            text
            @click="noPasscodeDialog = false"
          >Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Prop } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import BusinessModule from '../../store/modules/business'
import configHelper from '../../util/config-helper'
import iframeServices from '../../services/iframe.services'

@Component
export default class PasscodeForm extends Vue {
  showPasscode = false
  showSpinner = false
  noPasscodeDialog = false
  loginError = ''
  valid = false
  VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  entityNumRules = [
    v => !!v || 'Incorporation Number is required'
  ]
  entityPasscodeRules = [
    v => !!v || 'Passcode is required',
    v => v.length >= 9 || 'Passcode must be exactly 9 digits'
  ]
  businessStore = getModule(BusinessModule, this.$store)

  businessNumber: string = ''
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
      setTimeout(() => {
        window.location.href = this.VUE_APP_COPS_REDIRECT_URL
      }, 500)
    } else {
      // transition to business contact UI
      setTimeout(() => {
        this.$router.push('/businessprofile')
      }, 500)
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
      this.businessStore.login({ businessNumber: this.businessNumber, passCode: this.passcode })
        .then(response => {
          // set token and store in storage
          sessionStorage.KEYCLOAK_TOKEN = response.data.access_token
          sessionStorage.KEYCLOAK_REFRESH_TOKEN = response.data.refresh_token
          sessionStorage.REGISTRIES_TRACE_ID = response.data['registries-trace-id']
          sessionStorage.LOGIN_TYPE = 'passcode'

          // attempt to load business
          this.businessStore.loadBusiness(this.businessNumber)
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

.passcode-form__row{
  margin-top: 1rem;
}

.passcode-form__form-btns{
  margin-top: 2rem;
  display: flex;
}

.v-btn{
  margin: 0;
}

.v-btn.recovery-btn{
  margin-right: auto;
  padding-right: 0.7rem;
  padding-left: 0.7rem;
  text-decoration: underline;
  font-size: 1rem;
}

.v-btn.sign-in-btn{
  font-weight: 700;
}

.v-input{
  max-width: 25rem;
}

.passcode-form__alert-container{
  margin-bottom: 2rem;
}

.v-alert{
  margin: 0;
}

@media (max-width: 600px){
  .passcode-form__form-btns{
    flex-flow: column nowrap;
  }

  .v-btn.recovery-btn{
    order: 1;
    margin-top: 0.5rem;
    margin-left: auto;
  }

  .v-btn.sign-in-btn{
    width: 100%;
  }
}

@media (min-width: 960px){
  .v-btn.recovery-btn{
    font-size: 0.875rem;
  }
}

// Contact List
.contact-list{
  margin-top: 1.5rem;
  padding: 0;
  font-weight: 500;
  list-style-type: none;
}

.contact-list__row{
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.contact-list__row .v-icon{
    vertical-align: middle;
    margin-top: -0.2rem;
    margin-right: 1.25rem;
}

.contact-list__row + .contact-list__row{
  margin-top: 0.5rem;
}

// Passcode Dialog
.v-dialog{
  margin: 2rem;
}

.v-card__title{
  padding: 1.25rem 1.5rem;
  color: $BCgovFontColorInverted;
  background: $BCgovBlue5;
  font-size: 1.5em;
  font-weight: 400;
}

.v-card__text{
  padding: 1.5rem;
  font-weight: 300;
}
</style>
