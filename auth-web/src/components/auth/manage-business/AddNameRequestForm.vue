<template>
  <div class="add-namerequest-form">
    <v-form
      ref="addNRForm"
      lazy-validation
    >
      <fieldset>
        <legend hidden>
          Name Request Number and Applicant Phone Number or Email Address
        </legend>
        <v-text-field
          ref="nrNumber"
          :key="nrNumberKey"
          filled
          persistent-hint
          label="Enter a Name Request Number"
          hint="Example: NR 1234567"
          :rules="nrNumberRules"
          :value="nrNumber"
          data-test="nr-number"
          autofocus
          @input="nrNumber = formatNrNumber($event)"
        />
        <v-text-field
          v-model="applicantPhoneNumber"
          filled
          persistent-hint
          label="Enter the Applicant Phone Number"
          hint="Example: 555-555-5555"
          :rules="applicantPhoneNumberRules"
          type="tel"
          data-test="applicant-phone-number"
        />
        <div class="font-weight-bold ml-3 mb-2">
          or
        </div>
        <v-text-field
          v-model="applicantEmail"
          filled
          persistent-hint
          label="Enter the Applicant Email Address"
          hint="Example: name@email.com"
          :rules="applicantEmailRules"
          data-test="applicant-email"
        />
      </fieldset>

      <div class="form__btns mt-8">
        <v-btn
          large
          text
          class="pl-2 pr-2 mr-auto"
          data-test="forgot-button"
          @click.stop="openHelp()"
        >
          <v-icon>mdi-help-circle-outline</v-icon>
          <span>I lost or forgot my Name Request (NR) Number</span>
        </v-btn>
        <v-btn
          large
          outlined
          color="primary"
          data-test="cancel-button"
          @click="resetForm('on-cancel')"
        >
          <span>Cancel</span>
        </v-btn>
        <v-btn
          large
          color="primary"
          data-test="add-button"
          max-width="100"
          :disabled="!isFormValid()"
          :loading="isLoading"
          @click="add()"
        >
          <span>Add</span>
        </v-btn>
      </div>
    </v-form>

    <HelpDialog
      ref="helpDialog"
      :helpDialogBlurb="helpDialogBlurb"
    />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'pinia'
import CommonUtils from '@/util/common-util'
import { CreateNRAffiliationRequestBody } from '@/models/affiliation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { Organization } from '@/models/Organization'
import { StatusCodes } from 'http-status-codes'
import { useBusinessStore } from '@/store/business'
import { useOrgStore } from '@/store/org'

@Component({
  components: {
    HelpDialog
  },
  computed: {
    ...mapState(useOrgStore, ['currentOrganization'])
  },
  methods: {
    ...mapActions(useBusinessStore, [
      'addNameRequest'
    ])
  }
})
export default class AddNameRequestForm extends Vue {
  readonly currentOrganization!: Organization
  readonly addNameRequest!: (requestBody: CreateNRAffiliationRequestBody) => any

  readonly helpDialogBlurb = 'If you have lost your receipt and name results email and ' +
    'need assistance finding your Name Request (NR) Number, please contact use at:'

  readonly nrNumberRules = [
    v => !!v || 'Name Request Number is required',
    v => this.isValidNrNumber(v) || 'Name Request Number is invalid'
  ]

  readonly applicantPhoneNumberRules = [
    v => this.isInputEntered(v, 'phone') || 'Phone number is required',
    v => CommonUtils.validatePhoneNumber(v) || 'Phone number is invalid'
  ]

  readonly applicantEmailRules = [
    v => this.isInputEntered(v, 'email') || 'Email is required',
    v => this.isValidateEmail(v) || 'Email is Invalid'
  ]

  VALID_NR_FORMAT = new RegExp(/^(NR)?\s*(\d{7})$/)

  nrNumber = ''
  nrNumberKey = 0
  applicantPhoneNumber = ''
  applicantEmail = ''
  isLoading = false

  formatNrNumber (value): string {
    let formattedNrNumber = value?.toUpperCase()
    if (this.VALID_NR_FORMAT.test(formattedNrNumber)) {
      formattedNrNumber = 'NR ' + this.VALID_NR_FORMAT.exec(formattedNrNumber)[2]
    }
    // Force a re-render when the content is the same (reactivity issue)
    if (formattedNrNumber === this.nrNumber) {
      this.nrNumberKey++
    }
    return formattedNrNumber
  }

  $refs: {
    addNRForm: HTMLFormElement,
    nrNumber: HTMLFormElement,
    helpDialog: HelpDialog
  }

  isFormValid (): boolean {
    return !!this.nrNumber &&
      (!!this.applicantPhoneNumber || !!this.applicantEmail) &&
      this.isValidNrNumber(this.nrNumber)
  }

  isInputEntered (value: any, inputType: string): boolean {
    return (!!((inputType === 'email')
      ? this.applicantPhoneNumber
      : this.applicantEmail) || !!value)
  }

  isValidateEmail (value: any): boolean {
    return ((!!this.applicantPhoneNumber && !!value) ||
      !!CommonUtils.validateEmailFormat(value))
  }

  isValidNrNumber (value: any): boolean {
    return this.VALID_NR_FORMAT.test(value)
  }

  async add (): Promise<void> {
    if (this.isFormValid()) {
      this.isLoading = true
      try {
        // attempt to add business
        const nrResponse = await this.addNameRequest({
          businessIdentifier: this.nrNumber,
          phone: this.applicantPhoneNumber.replace(/-/g, ''),
          email: this.applicantEmail
        })
        if (nrResponse?.status === 201) {
          // emit event to let parent know business added
          this.$emit('add-success')
        } else {
          this.$emit('add-unknown-error')
        }
      } catch (exception) {
        if (exception.response?.status === StatusCodes.BAD_REQUEST) {
          this.$emit('add-failed-show-msg', exception.response?.data?.message || '')
        } else if (exception.response?.status === StatusCodes.NOT_FOUND) {
          this.$emit('add-failed-no-entity')
        } else {
          this.$emit('add-unknown-error')
        }
      } finally {
        this.resetForm('')
      }
    }
  }

  resetForm (event: string): void {
    this.nrNumber = ''
    this.applicantEmail = ''
    this.applicantPhoneNumber = ''
    this.$refs.addNRForm.resetValidation()
    this.isLoading = false
    if (event) {
      this.$emit('on-cancel')
    }
  }

  openHelp (): void {
    this.$refs.helpDialog.open()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.form__btns {
  display: flex;
  justify-content: flex-end;

  .v-btn + .v-btn {
    margin-left: 0.5rem;
  }

  .v-btn[data-test="cancel-button"],
  .v-btn[data-test="add-button"] {
    min-width: unset !important;
    width: 100px;
  }

  .v-btn[disabled]:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
    color: white !important;
    background-color: $app-blue !important;
    opacity: 0.4;
  }
}
</style>
