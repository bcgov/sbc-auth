<template>
  <div class="add-business-form">
    <v-form ref="addBusinessForm" lazy-validation>
      <fieldset>
        <legend hidden>Incorporation Number and Password or Passcode</legend>
        <v-text-field
          filled
          label="Enter your Incorporation Number"
          hint="Example: BC1234567 or CP1234567"
          req
          persistent-hint
          :rules="businessIdentifierRules"
          v-model="businessIdentifier"
          @blur="formatBusinessIdentifier()"
          data-test="business-identifier"
        />
        <v-text-field
          filled
          :label="passcodeLabel"
          :hint="passcodeHint"
          persistent-hint
          :rules="passcodeRules"
          :maxlength="passcodeMaxLength"
          v-model="passcode"
          autocomplete="off"
          data-test="passcode"
        />
      </fieldset>

      <fieldset class="mt-8">
        <legend class="mb-4">Folio / Reference Number (optional)</legend>
        <p class="mb-8">
          If you file forms for a number of companies, you may want to enter a
          folio or reference number to help you keep track of your transactions.
        </p>
        <div class="folioNumber-form__row">
          <v-text-field
            filled
            label="Folio or Reference Number"
            :maxlength="50"
            v-model="folioNumber"
            data-test="folio-number"
          />
        </div>
        <div class="form__btns mt-6">
          <v-btn
            large text
            class="pl-2 pr-2 forgot-btn"
            data-test="forgot-button"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>{{forgotButtonText}}</span>
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
      </fieldset>
    </v-form>

    <HelpDialog
      :helpDialogBlurb="helpDialogBlurb"
      ref="helpDialog"
    />
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import { FolioNumberload, LoginPayload } from '@/models/business'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
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
      'addBusiness',
      'updateBusinessName',
      'updateFolioNumber'
    ])
  }
})
export default class AddBusinessForm extends Vue {
  private readonly currentOrganization!: Organization
  private readonly addBusiness!: (loginPayload: LoginPayload) => any
  private readonly updateBusinessName!: (businessNumber: string) => any
  private readonly updateFolioNumber!: (folioNumberload: FolioNumberload) => void

  private businessIdentifierRules = [
    v => !!v || 'Incorporation Number is required',
    v => CommonUtils.validateIncorporationNumber(v) || 'Incorporation Number is invalid'
  ]
  private businessIdentifier = ''
  private passcode = ''
  private folioNumber = ''
  private isLoading = false

  $refs: {
    addBusinessForm: HTMLFormElement,
    helpDialog: HelpDialog
  }

  private get isCooperative (): boolean {
    return CommonUtils.isCooperativeNumber(this.businessIdentifier)
  }

  private get passcodeLabel (): string {
    return 'Enter your ' + (this.isCooperative ? 'Passcode' : 'Password')
  }

  private get passcodeHint (): string {
    return this.isCooperative
      ? 'Passcode must be exactly 9 digits'
      : 'Password must be 8 to 15 characters'
  }

  private get passcodeMaxLength (): number {
    return this.isCooperative ? 9 : 15
  }

  private get passcodeRules (): any[] {
    return this.isCooperative
      ? [
        v => !!v || 'Passcode is required',
        v => CommonUtils.validateCooperativePasscode(v) || 'Passcode must be exactly 9 digits'
      ]
      : [
        v => !!v || 'Password is required',
        v => CommonUtils.validateCorporatePassword(v) || 'Password must be 8 to 15 characters'
      ]
  }

  private get forgotButtonText (): string {
    return 'I lost or forgot my ' + (this.isCooperative ? 'passcode' : 'password')
  }

  private get helpDialogBlurb (): string {
    if (this.isCooperative) {
      return 'If you have not received your Access Letter from BC Registries, or have lost your Passcode, ' +
        'please contact us at:'
    } else {
      const url = 'www.corporateonline.gov.bc.ca'
      return `If you have forgotten or lost your password, please visit <a href="https://${url}">${url}</a> ` +
        'and choose the option "Forgot Company Password", or contact us at:'
    }
  }

  private isFormValid (): boolean {
    return !!this.businessIdentifier &&
      !!this.passcode &&
      this.$refs.addBusinessForm.validate()
  }

  private async add (): Promise<void> {
    if (this.isFormValid()) {
      this.isLoading = true
      try {
        // attempt to add business
        const addResponse = await this.addBusiness({
          businessIdentifier: this.businessIdentifier,
          passCode: this.passcode
        })
        if (addResponse?.status === 201) {
          const businessResponse = await this.updateBusinessName(this.businessIdentifier)
          if (businessResponse?.status === 200) {
            // update folio number if the business name updated successfully
            await this.updateFolioNumber({
              businessIdentifier: this.businessIdentifier,
              folioNumber: this.folioNumber
            })

            // emit event to let parent know business added
            this.$emit('add-success')
          } else {
            this.$emit('add-unknown-error')
          }
        }
      } catch (exception) {
        if (exception.response?.status === StatusCodes.UNAUTHORIZED) {
          this.$emit('add-failed-invalid-code')
        } else if (exception.response?.status === StatusCodes.NOT_FOUND) {
          this.$emit('add-failed-no-entity')
        } else if (exception.response?.status === StatusCodes.NOT_ACCEPTABLE) {
          this.$emit('add-failed-passcode-claimed')
        } else {
          this.$emit('add-unknown-error')
        }
      } finally {
        this.resetForm()
      }
    }
  }

  resetForm () {
    this.businessIdentifier = ''
    this.passcode = ''
    this.folioNumber = ''
    this.$refs.addBusinessForm.resetValidation()
    this.isLoading = false
  }

  private formatBusinessIdentifier (): void {
    this.businessIdentifier = CommonUtils.formatIncorporationNumber(this.businessIdentifier)
  }

  private openHelp (): void {
    this.$refs.helpDialog.open()
  }

  /** Emits event to parent initially and when business identifier changes. */
  @Watch('businessIdentifier', { immediate: true })
  private onBusinessIdentifierChange (): void {
    this.$emit('on-business-identifier', this.businessIdentifier)
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
