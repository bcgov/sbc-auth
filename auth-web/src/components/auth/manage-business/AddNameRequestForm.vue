<template>
  <div class="add-namerequest-form">
    <v-form ref="addNRForm" lazy-validation>
      <fieldset>
        <legend hidden>Name Request Number and Applicant Phone Number or Email Address</legend>
        <v-text-field
          filled
          label="Enter a Name Request Number"
          hint="Example: NR 1234567"
          req
          persistent-hint
          :rules="nrNumberRules"
          v-model="nrNumber"
          @blur="formatNrNumber()"
          data-test="nr-number"
        />
        <v-text-field
          filled
          label="Enter the Applicant Phone Number"
          hint="Example: 555-555-5555"
          persistent-hint
          :rules="applicantPhoneNumberRules"
          v-model="applicantPhoneNumber"
          type="tel"
          data-test="applicant-phone-number"
        />
        <div class="font-weight-bold ml-3 mb-2">or</div>
        <v-text-field
          filled
          label="Enter the Applicant Email Address"
          hint="Example: name@email.com"
          persistent-hint
          :rules="applicantEmailRules"
          v-model="applicantEmail"
          data-test="applicant-email"
        />
      </fieldset>

      <div class="form__btns mt-8">
        <v-btn
          large text
          class="pl-2 pr-2 forgot-btn"
          data-test="forgot-button"
          @click.stop="openHelp()"
        >
          <v-icon>mdi-help-circle-outline</v-icon>
          <span>I lost or forgot my Name Request (NR) Number</span>
        </v-btn>
        <v-btn
          data-test="add-button"
          large color="primary"
          :disabled="!isFormValid()"
          @click="add()"
          :loading="isLoading"
        >
          <span>Add</span>
        </v-btn>
        <v-btn
          large depressed
          color="default"
          class="ml-2"
          data-test="cancel-button"
          @click="$emit('on-cancel')"
        >
          <span>Cancel</span>
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
import { Component, Vue } from 'vue-property-decorator'
import { FilingTypes, LegalTypes } from '@/util/constants'
import { mapActions, mapState } from 'vuex'
import { BusinessRequest } from '@/models/business'
import CommonUtils from '@/util/common-util'
import { CreateNRAffiliationRequestBody } from '@/models/affiliation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { Organization } from '@/models/Organization'
import { StatusCodes } from 'http-status-codes'

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
  private readonly currentOrganization!: Organization
  private readonly addNameRequest!: (requestBody: CreateNRAffiliationRequestBody) => any

  private helpDialogBlurb = 'If you have lost your receipt and name results email and ' +
    'need assistance finding your Name Request (NR) Number, please contact use at:'

  private nrNumberRules = [
    v => !!v || 'Name Request Number is required',
    v => CommonUtils.validateNameRequestNumber(v) || 'Name Request Number is invalid'
  ]
  private applicantPhoneNumberRules = [
    v => this.isInputEntered(v, 'phone') || 'Phone number is required',
    v => CommonUtils.validatePhoneNumber(v) || 'Phone number is invalid'
  ]
  private applicantEmailRules = [
    v => this.isInputEntered(v, 'email') || 'Email is required',
    v => this.isValidateEmail(v) || 'Email is Invalid'
  ]
  private nrNumber = ''
  private applicantPhoneNumber = ''
  private applicantEmail = ''
  private isLoading = false

  $refs: {
    addNRForm: HTMLFormElement,
    helpDialog: HelpDialog
  }

  private isFormValid (): boolean {
    return !!this.nrNumber &&
      (!!this.applicantPhoneNumber || !!this.applicantEmail)
  }

  private isInputEntered (value: any, inputType: string): boolean {
    return (!!((inputType === 'email')
      ? this.applicantPhoneNumber
      : this.applicantEmail) || !!value)
  }

  private isValidateEmail (value: any): boolean {
    return ((!!this.applicantPhoneNumber && !!value) ||
      !!CommonUtils.validateEmailFormat(value))
  }

  private async add (): Promise<void> {
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
        this.resetForm()
      }
    }
  }

  private resetForm (): void {
    this.nrNumber = ''
    this.applicantEmail = ''
    this.applicantPhoneNumber = ''
    this.$refs.addNRForm.resetValidation()
    this.isLoading = false
  }

  private formatNrNumber (): void {
    this.nrNumber = CommonUtils.formatIncorporationNumber(this.nrNumber, true)
  }

  private openHelp (): void {
    this.$refs.helpDialog.open()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.forgot-btn {
  margin-right: auto;
}

.form__btns {
  display: flex;
  justify-content: flex-end;

  .v-btn + .v-btn {
    margin-left: 0.5rem;
  }
}
</style>
