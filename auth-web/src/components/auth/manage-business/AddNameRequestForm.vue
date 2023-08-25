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
        <div class="d-flex align-items-center">
          <div class="font-weight-bold mr-2">
            Requested Name(s):
          </div>
          <div>
            <div
              v-for="(name, i) in requestNames"
              :key="`nrName: ${i}`"
              class="pb-1 names-block d-flex align-items-center"
            >
              <v-icon
                v-if="isRejectedName(name)"
                color="red"
                class="names-text pr-1"
                small
              >
                mdi-close
              </v-icon>
              <v-icon
                v-else-if="isApprovedName(name)"
                color="green"
                class="names-text pr-1"
                small
              >
                mdi-check
              </v-icon>
              <v-icon
                v-else
                color="transparent"
                class="names-text pr-1"
                small
              >
                mdi-close
              </v-icon><!-- spacer icon -->
              <!-- TODO 16722 change to {{ name.name when BE fix (able to send with status) }} -->
              <span class="names-text">{{ name }}</span>
            </div>
          </div>
        </div>
        <div class="font-weight-bold mr-2 float-left">
          Name Request Number:
        </div>
        <div>{{ businessIdentifier }}</div><br>
        <div class="my-4">
          Enter either the applicant phone number OR applicant email that were used when the name was requested:
        </div>
        <v-text-field
          :key="nrNumberKey"
          v-model="applicantPhoneNumber"
          filled
          persistent-hint
          label="Applicant Phone Number"
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
          label="Applicant Email Address"
          hint="Example: name@email.com"
          :rules="applicantEmailRules"
          data-test="applicant-email"
        />
      </fieldset>

      <div class="form__btns mt-8">
        <v-btn
          large
          text
          class="mr-auto pl-0 help-text"
          data-test="forgot-button"
          @click.stop="openHelp()"
        >
          <v-icon>mdi-help-circle-outline</v-icon>
          <span>Help</span>
        </v-btn>
        <v-btn
          large
          outlined
          color="primary"
          data-test="cancel-button"
          @click="resetForm('close-add-nr-modal')"
        >
          <span>Cancel</span>
        </v-btn>
        <v-btn
          large
          color="primary"
          data-test="add-button"
          min-width="80"
          :disabled="!isFormValid()"
          :loading="isLoading"
          @click="add()"
        >
          <span>Manage This Name Request</span>
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
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'pinia'
import CommonUtils from '@/util/common-util'
import { CreateNRAffiliationRequestBody } from '@/models/affiliation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { NameRequestIF } from '@/models/business-nr-lookup'
import { NrState } from '@/util/constants'
import { Organization } from '@/models/Organization'
import { StatusCodes } from 'http-status-codes'
import { useBusinessStore } from '@/stores/business'
import { useOrgStore } from '@/stores/org'

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
  @Prop({ default: '' }) readonly requestNames: NameRequestIF[]
  @Prop({ default: '' }) readonly businessIdentifier: string
  @Prop({ default: false }) readonly isEnableBusinessNrSearch: boolean

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
          this.$emit('add-success-nr', this.nrNumber)
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
  isRejectedName = (name: NameRequestIF): boolean => {
    return (name.status === NrState.REJECTED)
  }

  /** Returns true if the name is approved. */
  isApprovedName = (name: NameRequestIF): boolean => {
    return (name.status === NrState.APPROVED)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.form__btns {
  display: flex;

  .v-btn + .v-btn {
    margin-left: 0.5rem;
  }

  .help-text {
    justify-content: flex-start; // align help button to left
    color: $app-blue;
  }

  .v-btn[data-test="cancel-button"],
  .v-btn[data-test="add-button"] {
    min-width: 80px !important;
  }

  .v-btn[disabled]:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
    color: white !important;
    background-color: $app-blue !important;
    opacity: 0.4;
  }
}
</style>
