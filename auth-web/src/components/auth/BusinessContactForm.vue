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
        filled
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
        filled
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
            filled
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
            filled label="Extension"
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
        <v-btn v-show="editing" class=".cancel-button" @click="cancel" color="secondary" large>
          <span>Cancel</span>
        </v-btn>
        <v-btn class=".save-continue-button" @click="save" :disabled='!isFormValid()' color="primary" large>
          <span>Save and Continue</span>
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
import { Contact } from '../../models/contact'

@Component({
  directives: {
    mask
  }
})
export default class BusinessContactForm extends Vue {
  private VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private businessStore = getModule(BusinessModule, this.$store)
  private emailAddress = ''
  private confirmedEmailAddress = ''
  private phoneNumber = ''
  private extension = ''
  private formError = ''
  private editing = false

  private emailRules = [
    v => !!v || 'Email address is required',
    v => {
      const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return pattern.test(v) || 'Valid email is required'
    }
  ]

  private phoneRules = [
    v => !v || (v.length === 0 || v.length === 14) || 'Phone number is invalid'
  ]

  private extensionRules = [
    v => !v || (v.length >= 0 || v.length <= 3) || 'Extension is invalid'
  ]

  private emailMustMatch (): string {
    return (this.emailAddress === this.confirmedEmailAddress) ? '' : 'Email addresses must match'
  }

  private isFormValid (): boolean {
    if (!this.$refs || !this.$refs.form) {
      return false
    }

    return (this.$refs.form as Vue & { validate: () => boolean }).validate() &&
      this.emailAddress === this.confirmedEmailAddress
  }

  mounted () {
    if (this.businessStore.currentBusiness.contacts && this.businessStore.currentBusiness.contacts.length > 0) {
      // TODO: For now grab first contact as the business contact.  Post MVP, we should check the contact type, grab the correct one.
      const contact = this.businessStore.currentBusiness.contacts[0]
      this.emailAddress = this.confirmedEmailAddress = contact.email
      this.phoneNumber = contact.phone
      this.extension = contact.phoneExtension
    }
  }

  save () {
    if (this.isFormValid()) {
      let result: Promise<void>
      const contact: Contact = {
        email: this.emailAddress,
        phone: this.phoneNumber,
        phoneExtension: this.extension
      }

      if (!this.businessStore.currentBusiness.contacts || this.businessStore.currentBusiness.contacts.length === 0) {
        result = this.businessStore.addContact(contact)
      } else {
        result = this.businessStore.updateContact(contact)
      }

      result.then(response => {
        // TODO: Change this to transition to entity dashboard once complete
        setTimeout(() => {
          window.location.href = this.VUE_APP_COPS_REDIRECT_URL
        }, 500)
      })
    }
  }

  cancel () {
    window.location.href = this.VUE_APP_COPS_REDIRECT_URL
  }

  skip () {
    // Mark store as having skipped contact entry for this session
    this.businessStore.setSkippedContactEntry(true)

    // Go directly to co-op UI without saving
    setTimeout(() => {
      window.location.href = this.VUE_APP_COPS_REDIRECT_URL
    }, 500)
  }
}
</script>

<style lang="scss" scoped>
  @import '../../assets/scss/theme.scss';

  .business-contact-form_row{
    margin-top: 1rem;
  }

  .business-contact-form_alert-container{
    margin-bottom: 2rem;
  }

  .v-alert{
    margin: 0;
  }

  .v-btn{
    font-weight: 700;
  }
</style>
