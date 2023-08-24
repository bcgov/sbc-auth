<template>
  <v-form
    ref="form"
    lazy-validation
  >
    <v-expand-transition>
      <div
        v-show="formError"
        class="business-contact-form__alert-container"
      >
        <v-alert
          type="error"
          class="mb-0"
          :value="true"
        >
          {{ formError }}
        </v-alert>
      </div>
    </v-expand-transition>

    <!-- Business Contact Information Fields -->
    <fieldset>
      <legend class="mb-4">
        Business Contact Information
      </legend>
      <v-text-field
        v-model="emailAddress"
        filled
        label="Email Address"
        req
        persistent-hint
        :rules="emailRules"
      />
      <v-text-field
        v-model="confirmedEmailAddress"
        filled
        label="Confirm Email Address"
        req
        persistent-hint
        :error-messages="emailMustMatch()"
      />
      <v-row>
        <v-col cols="6">
          <v-text-field
            v-model="phoneNumber"
            v-mask="['(###) ###-####']"
            filled
            label="Phone Number"
            persistent-hint
            hint="Example: (555) 555-5555"
            type="tel"
          />
        </v-col>
        <v-col cols="4">
          <v-text-field
            v-model="extension"
            v-mask="'#####'"
            filled
            label="Extension"
            persistent-hint
            :rules="extensionRules"
          />
        </v-col>
      </v-row>
    </fieldset>

    <v-divider class="mt-6 mb-9" />

    <!-- Folio / Reference Number Fields -->
    <fieldset>
      <legend class="mb-4">
        Folio / Reference Number (optional)
      </legend>
      <p class="mb-8">
        If you file forms for a number of companies, you may want to enter a folio or reference number to help you keep track of your transactions.
      </p>
      <v-text-field
        v-model="folioNumber"
        filled
        label="Folio or Reference Number"
        persistent-hint
        :maxlength="50"
      />
    </fieldset>

    <v-divider class="my-2 mb-10" />

    <div class="form__btns">
      <v-btn
        large
        color="primary"
        :disabled="!isFormValid()"
        @click="save"
      >
        Update
      </v-btn>
      <v-btn
        large
        depressed
        color="default"
        @click="cancel"
      >
        Cancel
      </v-btn>
    </div>
  </v-form>
</template>

<script lang="ts">
import { Business, FolioNumberload } from '@/models/business'
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'pinia'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { Organization } from '@/models/Organization'
import { mask } from 'vue-the-mask'
import { useBusinessStore } from '@/stores/business'
import { useOrgStore } from '@/stores/org'

@Component({
  directives: {
    mask
  },
  computed: {
    ...mapState(useBusinessStore, ['currentBusiness']),
    ...mapState(useOrgStore, ['currentOrganization'])
  },
  methods: {
    ...mapActions(useBusinessStore, ['saveContact', 'updateFolioNumber'])
  }
})
export default class BusinessContactForm extends Vue {
  private emailAddress = ''
  private confirmedEmailAddress = ''
  private phoneNumber = ''
  private extension = ''
  private folioNumber = ''
  private formError = ''
  private editing = false
  private readonly currentBusiness!: Business
  private readonly saveContact!: (contact: Contact) => void
  private readonly updateFolioNumber!: (folioNumberload: FolioNumberload) => void
  private readonly currentOrganization!: Organization

  private emailRules = [
    v => !!v || 'Email address is required',
    v => {
      const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return pattern.test(v) || 'Valid email is required'
    }
  ]

  private extensionRules = [
    v => !v || (v.length >= 0 && v.length <= 5) || 'Extension is invalid'
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

  private redirectToNext () {
    if (this.$route.query.redirect) {
      this.$router.push({ path: `/account/${this.currentOrganization.id}` })
    } else {
      window.location.href = `${ConfigHelper.getBusinessURL()}${this.currentBusiness.businessIdentifier}`
    }
  }

  async mounted () {
    if (this.currentBusiness.contacts && this.currentBusiness.contacts.length > 0) {
      const contact = this.currentBusiness.contacts[0]
      this.emailAddress = this.confirmedEmailAddress = contact.email
      this.phoneNumber = contact.phone
      this.extension = contact.phoneExtension
    }
    this.folioNumber = this.currentBusiness.folioNumber
  }

  async save () {
    if (this.isFormValid()) {
      const contact: Contact = {
        email: this.emailAddress.toLowerCase(),
        phone: this.phoneNumber,
        phoneExtension: this.extension
      }
      await this.saveContact(contact)
      await this.updateFolioNumber({
        businessIdentifier: this.currentBusiness.businessIdentifier.trim().toUpperCase(),
        folioNumber: this.folioNumber
      })
      this.redirectToNext()
    }
  }

  cancel () {
    this.redirectToNext()
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  // Tighten up some of the spacing between rows
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;

    .v-btn + .v-btn {
      margin-left: 0.5rem;
    }
  }

  .business-contact-form__alert-container {
    margin-bottom: 2.25rem;
  }
</style>
