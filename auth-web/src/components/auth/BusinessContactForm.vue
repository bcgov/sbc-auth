<template>
  <v-form ref="form" lazy-validation>
    <v-expand-transition>
      <div class="business-contact-form__alert-container" v-show="formError">
        <v-alert type="error" class="mb-0"
          :value="true"
        >{{formError}}
        </v-alert>
      </div>
    </v-expand-transition>
    <v-row>
      <v-col cols="12">
        <v-text-field
          filled
          label="Email Address"
          req
          persistent-hint
          :rules="emailRules"
          v-model="emailAddress"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-text-field
          filled
          label="Confirm Email Address"
          req
          persistent-hint
          :error-messages="emailMustMatch()"
          v-model="confirmedEmailAddress"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field
          filled
          label="Phone Number"
          persistent-hint
          hint="Example: (555) 555-5555"
          type="tel"
          v-mask="['(###) ###-####']"
          v-model="phoneNumber"
          :rules="phoneRules"
        >
        </v-text-field>
      </v-col>
      <v-col cols="3">
        <v-text-field
          filled label="Extension"
          persistent-hint
          :rules="extensionRules"
          v-mask="'###'"
          v-model="extension"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" class="form__btns pb-0">
        <v-btn large color="default" v-show="editing" @click="cancel">
          Cancel
        </v-btn>
        <v-btn large color="primary" @click="save" :disabled='!isFormValid()'>
          Save and Continue
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import BusinessModule from '../../store/modules/business'
import configHelper from '../../util/config-helper'
import { mask } from 'vue-the-mask'
import { Contact } from '../../models/contact'
import { SessionStorageKeys } from '../../util/constants'

@Component({
  directives: {
    mask
  }
})
export default class BusinessContactForm extends Vue {
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
    this.businessStore.loadBusiness(configHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)).then(() => {
      if (this.businessStore.currentBusiness.contacts && this.businessStore.currentBusiness.contacts.length > 0) {
      // TODO: For now grab first contact as the business contact.  Post MVP, we should check the contact type, grab the correct one.
        const contact = this.businessStore.currentBusiness.contacts[0]
        this.emailAddress = this.confirmedEmailAddress = contact.email
        this.phoneNumber = contact.phone
        this.extension = contact.phoneExtension
      }
    })
  }

  save () {
    if (this.isFormValid()) {
      let result: Promise<void>
      const contact: Contact = {
        email: this.emailAddress.toLowerCase(),
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
        window.location.href = configHelper.getCoopsURL()
      })
    }
  }

  cancel () {
    window.location.href = configHelper.getCoopsURL()
  }

  skip () {
    // Mark store as having skipped contact entry for this session
    this.businessStore.setSkippedContactEntry(true)

    // Go directly to co-op UI without saving
    window.location.href = configHelper.getCoopsURL()
  }
}
</script>

<style lang="scss" scoped>
  @import '../../assets/scss/theme.scss';

  // Tighten up some of the spacing between rows
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }

  .business-contact-form__alert-container {
    margin-bottom: 2.25rem;
  }
</style>
