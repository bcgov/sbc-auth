<template>
  <div>
    <v-form ref="form" lazy-validation>
      <v-expand-transition>
        <div class="business-contact-form_alert-container" v-show="formError">
          <v-alert
            :value="true"
            color="error"
            icon="warning"
          >{{formError}}
          </v-alert>
        </div>
      </v-expand-transition>
    <div class="business-contact-form_row">
      <v-text-field
        box
        label="Email Address"
        req
        persistent-hint
        :rules="emailRules"
        v-model="emailAddress"
      >
      </v-text-field>
    </div>
    <div class="business-contact-form_row">
      <v-text-field
        box
        label="Confirm Email Address"
        req
        persistent-hint
        :error-messages="emailMustMatch()"
        v-model="confirmedEmailAddress"
      >
      </v-text-field>
    </div>
    <div class="business-contact-form_row">
      <v-layout wrap>
        <v-flex xs6 class="mr-5">
          <v-text-field
            box
            label="Phone e.g. (555)-555-5555"
            persistent-hint
            type="tel"
            v-mask="['(###)-###-####']"
            v-model="phoneNumber"
            :rules="phoneRules"
          >
          </v-text-field>
        </v-flex>
        <v-flex xs3>
          <v-text-field
            box label="Extension"
            persistent-hint
            :rules="extensionRules"
            v-mask="'###'"
            v-model="extension"
          >
          </v-text-field>
        </v-flex>
      </v-layout>
    </div>
    <div class="business-contact-form_row">
      <v-layout wrap>
        <v-spacer></v-spacer>
        <v-btn class=".save-continue-button" @click="save" color="primary" large>
          <span>Save and Continue</span>
        </v-btn>
        <v-btn class=".skip-button mr-0" @click="skip" color="secondary" large>
          <span>Skip</span>
        </v-btn>
      </v-layout>
    </div>
    </v-form>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import BusinessModule from '../../store/modules/business'
import configHelper from '../../util/config-helper'
import { mask } from 'vue-the-mask'

@Component({
  directives: {
    mask
  }
})
export default class BusinessContactForm extends Vue {
  private VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private businessStore = getModule(BusinessModule)
  private emailAddress = ''
  private confirmedEmailAddress = ''
  private phoneNumber = ''
  private extension = ''
  private formError = ''

  private emailRules = [
    v => !!v || 'Email address is required',
    v => {
      const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return pattern.test(v) || 'Valid email is required'
    }
  ]

  private phoneRules = [
    v => (v.length === 0 || v.length === 14) || 'Phone number is invalid'
  ]

  private extensionRules = [
    v => (v.length >= 0 || v.length <= 3) || 'Extension is invalid'
  ]

  private emailMustMatch (): string {
    return (this.emailAddress === this.confirmedEmailAddress) ? '' : 'Emails addresses must match'
  }

  private isFormValid (): boolean {
    return (this.$refs.form as Vue & { validate: () => boolean }).validate()
  }

  mounted () {
    const contact = this.businessStore.currentBusiness.contact1
    if (contact) {
      this.emailAddress = this.confirmedEmailAddress = contact.emailAddress
      this.phoneNumber = contact.phoneNumber
      this.extension = contact.extension
    }
  }

  save () {
    if (this.isFormValid()) {
      this.businessStore.updateContact({
        emailAddress: this.emailAddress,
        phoneNumber: this.phoneNumber,
        extension: this.extension
      })
        .then(response => {
          // TODO: Change this to transition to entity dashboard once complete
          setTimeout(() => {
            window.location.href = this.VUE_APP_COPS_REDIRECT_URL
          }, 500)
        })
    }
  }

  skip () {
    // Go directly to co-op UI without saving
    setTimeout(() => {
      window.location.href = this.VUE_APP_COPS_REDIRECT_URL
    }, 500)
  }
}
</script>

<style lang="stylus" scoped>
  @import '../../assets/styl/theme.styl';

  .business-contact-form_row
    margin-top 1rem

  .business-contact-form_alert-container
    margin-bottom 2rem

  .v-alert
    margin 0

  .v-btn
    font-weight: 700
</style>
