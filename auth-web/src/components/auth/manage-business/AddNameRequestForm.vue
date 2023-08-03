<template>
  <div class="add-namerequest-form">
    <v-form ref="addNRForm" lazy-validation>
      <fieldset>
        <legend hidden>Name Request Number and Applicant Phone Number or Email Address</legend>
        <div class="d-flex align-items-center">
          <div class="font-weight-bold mr-2">Requested Name(s):</div>
          <div>
            <div v-for='(name, i) in requestNames' :key='`nrName: ${i}`' class='pb-1 names-block d-flex align-items-center'>
              <v-icon v-if='isRejectedName(name)' color='red' class='names-text pr-1' small>mdi-close</v-icon>
              <v-icon v-else-if='isApprovedName(name)' color='green' class='names-text pr-1' small>mdi-check</v-icon>
              <v-icon v-else color='transparent' class='names-text pr-1' small>mdi-close</v-icon><!-- spacer icon -->
              <span class='names-text font-weight-bold'>{{ name.name }}</span>
            </div>
          </div>
        </div>
        <div class="font-weight-bold mr-2 float-left">Name Request Number:</div>
        <div>{{businessIdentifier}}</div><br>
        <div class="my-4">
            Enter either the applicant phone number OR applicant email that were used when the name was requested:
        </div>
        <v-text-field
          filled persistent-hint
          label="Enter the Applicant Phone Number"
          hint="Example: 555-555-5555"
          :rules="applicantPhoneNumberRules"
          v-model="applicantPhoneNumber"
          type="tel"
          data-test="applicant-phone-number"
        />
        <div class="font-weight-bold ml-3 mb-2">or</div>
        <v-text-field
          filled persistent-hint
          label="Enter the Applicant Email Address"
          hint="Example: name@email.com"
          :rules="applicantEmailRules"
          v-model="applicantEmail"
          data-test="applicant-email"
        />
      </fieldset>

      <div class="form__btns mt-8">
        <v-btn
          large text
          class="pl-2 pr-2 mr-auto"
          data-test="forgot-button"
          @click.stop="openHelp()"
        >
          <v-icon>mdi-help-circle-outline</v-icon>
          <span>I lost or forgot my Name Request (NR) Number</span>
        </v-btn>
        <v-btn
          large outlined color="primary"
          data-test="cancel-button"
          @click="resetForm('close-add-nr-modal')"
        >
          <span>Cancel</span>
        </v-btn>
        <v-btn
          large color="primary"
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
      :helpDialogBlurb="helpDialogBlurb"
      ref="helpDialog"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import { CreateNRAffiliationRequestBody } from '@/models/affiliation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { Names } from '@/models/business'
import { NrState } from '@/util/constants'
import { Organization } from '@/models/Organization'
import { StatusCodes } from 'http-status-codes'
import { readonly } from '@vue/composition-api'

@Component({
  components: {
    HelpDialog
  },
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('business', [
      'addNameRequest'
    ])
  }
})
export default class AddNameRequestForm extends Vue {
  @Prop({ default: '' }) readonly requestNames: Names[]
  @Prop({ default: '' }) readonly businessIdentifier: string

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

  nrNumberKey = 0
  applicantPhoneNumber = ''
  applicantEmail = ''
  isLoading = false

  get nrNumber () {
    return this.businessIdentifier
  }

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
    const phoneValid = this.applicantPhoneNumber && CommonUtils.validatePhoneNumber(this.applicantPhoneNumber)
    const emailValid = this.applicantEmail && CommonUtils.validateEmailFormat(this.applicantEmail)
    return phoneValid || emailValid
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
          this.$emit('add-success', this.nrNumber)
        } else {
          this.$emit('add-unknown-error')
        }
      } catch (exception) {
        if (exception.response?.status === StatusCodes.BAD_REQUEST) {
          this.$emit('add-failed-show-msg', exception.response?.data?.message || '')
        } else if (exception.response?.status === StatusCodes.NOT_FOUND) {
          this.$emit('add-failed-no-nr')
        } else {
          this.$emit('add-unknown-error')
        }
      } finally {
        this.resetForm('')
      }
    }
  }

  resetForm (event: string): void {
    this.applicantEmail = ''
    this.applicantPhoneNumber = ''
    this.$refs.addNRForm.resetValidation()
    this.isLoading = false
    if (event) {
      this.$emit('close-add-nr-modal')
    }
  }

  openHelp (): void {
    this.$refs.helpDialog.open()
  }

  /** Returns true if the name is rejected. */
  isRejectedName = (name: Names): boolean => {
    return (name.state === NrState.REJECTED)
  }

  /** Returns true if the name is approved. */
  isApprovedName = (name: Names): boolean => {
    return (name.state === NrState.APPROVED)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.form__btns {
  display: flex;
  // justify-content: flex-end;

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
