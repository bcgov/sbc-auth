<template>
  <div id="add-business-dialog">
    <HelpDialog
      :helpDialogBlurb="helpDialogBlurb"
      ref="helpDialog"
    />

    <v-dialog
      attach="#entity-management"
      v-model="dialog"
      persistent
      scrollable
      max-width="675"
      data-test-tag="add-business"
      @keydown.esc="resetForm(true)"
    >
      <v-card>
        <v-card-title data-test="dialog-header">
          <span>Add an Existing Business</span>
        </v-card-title>

        <v-card-text class="py-2">
          <p>
            Add an existing business to your list by providing the following required pieces of information:
          </p>
          <v-tooltip top nudge-bottom="80" content-class="top-tooltip">
            <template v-slot:activator="{ on, attrs }">
              <ul class="add-business-unordered-list">
                <li>For <strong>cooperatives</strong>, enter the incorporation number and the passcode.</li>
                <li>For <strong>benefit companies</strong>, enter the incorporation number and the password.</li>
                <li>For <strong>sole proprietorships and general partnerships</strong>, enter the registration
                  number and either <span v-bind="attrs" v-on="on" activator class="underline-dotted">the name
                  of the proprietor or a partner</span>.</li>
              </ul>
            </template>
            <span>
              For individuals, it should be "Last Name, First Name MiddleName".<br>
              E.g. Watson, John Hamish
            </span>
          </v-tooltip>

          <v-form ref="addBusinessForm" lazy-validation class="mt-6">
            <!-- Business Identifier -->
            <v-text-field
              filled req persistent-hint validate-on-blur
              label="Incorporation Number or Registration Number"
              hint="Example: BC1234567, CP1234567 or FM1234567"
              :rules="businessIdentifierRules"
              v-model="businessIdentifier"
              @blur="formatBusinessIdentifier()"
              class="business-identifier mb-n2"
              aria-label="Incorporation Number and Password or Passcode"
            />

            <!-- Passcode -->
            <v-expand-transition>
              <v-text-field
                v-if="isBusinessIdentifierValid"
                filled
                :label="passcodeLabel"
                :hint="passcodeHint"
                persistent-hint
                :rules="passcodeRules"
                :maxlength="passcodeMaxLength"
                v-model="passcode"
                autocomplete="off"
                class="passcode mt-6 mb-n2"
                :aria-label="passcodeLabel"
              />
            </v-expand-transition>

            <!-- Certify (firms only) -->
            <v-expand-transition>
              <Certify
                v-if="isBusinessIdentifierValid && isFirm"
                :clause="certifyClause"
                entity="registered entity"
                @update:isCertified="isCertified = $event"
                class="certify mt-6"
              />
            </v-expand-transition>

            <!-- Folio Number -->
            <v-expand-transition>
              <section v-if="isBusinessIdentifierValid" class="mt-6">
                <header class="font-weight-bold">Folio / Reference Number</header>
                <p class="mt-4 mb-0">
                  If you file forms for a number of companies, you may want to enter a
                  folio or reference number to help you keep track of your transactions.
                </p>
                <v-text-field
                  filled hide-details
                  label="Folio or Reference Number (Optional)"
                  :maxlength="50"
                  v-model="folioNumber"
                  class="folio-number mt-6"
                  aria-label="Folio or Reference Number (Optional)"
                />
              </section>
            </v-expand-transition>
          </v-form>
        </v-card-text>

        <v-card-actions class="form__btns">
          <v-btn
            v-if="isBusinessIdentifierValid && !isFirm"
            large text
            class="pl-2 pr-2 mr-auto"
            id="forgot-button"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>{{forgotButtonText}}</span>
          </v-btn>
          <v-btn
            large outlined color="primary"
            id="cancel-button"
            @click="resetForm(true)"
          >
            <span>Cancel</span>
          </v-btn>
          <v-btn
            large color="primary"
            id="add-button"
            :loading="isLoading"
            @click="add()"
          >
            <span>Add</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { FolioNumberload, LoginPayload } from '@/models/business'
import Certify from './Certify.vue'
import CommonUtils from '@/util/common-util'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { StatusCodes } from 'http-status-codes'
import { mapActions } from 'vuex'

@Component({
  components: {
    Certify,
    HelpDialog
  },
  methods: {
    ...mapActions('business', [
      'addBusiness',
      'updateBusinessName',
      'updateFolioNumber'
    ])
  }
})
export default class AddBusinessDialog extends Vue {
  $refs: {
    addBusinessForm: HTMLFormElement,
    helpDialog: HelpDialog
  }

  @Prop({ default: false }) readonly dialog: boolean

  private readonly addBusiness!: (loginPayload: LoginPayload) => any
  private readonly updateBusinessName!: (businessNumber: string) => any
  private readonly updateFolioNumber!: (folioNumberload: FolioNumberload) => void

  // local variables
  protected businessIdentifier = '' // aka incorporation number of registration number
  protected passcode = '' // aka password or  proprietor/partner
  protected folioNumber = ''
  protected isLoading = false
  protected isCertified = false // firms only
  protected businessIdentifierRules = []

  readonly certifyClause = 'Note: It is an offence to make or assist in making a false or misleading ' +
    'statement in a record filed under the Partnership Act. A person who commits this offence is ' +
    'subject to a maximum fine of $5,000.'

  get isBusinessIdentifierValid (): boolean {
    return CommonUtils.validateIncorporationNumber(this.businessIdentifier)
  }

  get isCooperative (): boolean {
    return CommonUtils.isCooperativeNumber(this.businessIdentifier)
  }

  get isFirm (): boolean {
    return CommonUtils.isFirmNumber(this.businessIdentifier)
  }

  get passcodeLabel (): string {
    if (this.isFirm) return 'Proprietor or Partner Name'
    if (this.isCooperative) return 'Passcode'
    return 'Password'
  }

  get passcodeHint (): string {
    if (this.isFirm) return 'Name as it appears on the Business Summary or the Statement of Registration'
    if (this.isCooperative) return 'Passcode must be exactly 9 digits'
    return 'Password must be 8 to 15 characters'
  }

  get passcodeMaxLength (): number {
    if (this.isFirm) return 150
    if (this.isCooperative) return 9
    return 15
  }

  get passcodeRules (): any[] {
    if (this.isFirm) {
      return [
        v => !!v || 'Proprietor or Partner Name is required',
        v => v.length <= 150 || 'Maximum 150 characters'
      ]
    }
    if (this.isCooperative) {
      return [
        v => !!v || 'Passcode is required',
        v => CommonUtils.validateCooperativePasscode(v) || 'Passcode must be exactly 9 digits'
      ]
    }
    return [
      v => !!v || 'Password is required',
      v => CommonUtils.validateCorporatePassword(v) || 'Password must be 8 to 15 characters'
    ]
  }

  get forgotButtonText (): string {
    return 'I lost or forgot my ' + (this.isCooperative ? 'passcode' : 'password')
  }

  get helpDialogBlurb (): string {
    if (this.isCooperative) {
      return 'If you have not received your Access Letter from BC Registries, or have lost your Passcode, ' +
        'please contact us at:'
    } else {
      const url = 'www.corporateonline.gov.bc.ca'
      return `If you have forgotten or lost your password, please visit <a href="https://${url}">${url}</a> ` +
        'and choose the option "Forgot Company Password", or contact us at:'
    }
  }

  get isFormValid (): boolean {
    // business id is required
    // passcode is required
    // firms must accept certify clause
    // validate the form itself (according to the components' rules/state)
    return (
      !!this.businessIdentifier &&
      !!this.passcode &&
      (!this.isFirm || this.isCertified) &&
      this.$refs.addBusinessForm.validate()
    )
  }

  protected async add (): Promise<void> {
    this.$refs.addBusinessForm.validate()
    if (this.isFormValid) {
      this.isLoading = true
      try {
        // try to add business
        const addResponse = await this.addBusiness({
          businessIdentifier: this.businessIdentifier,
          passCode: this.passcode
        })
        // check if add didn't succeed
        if (addResponse?.status !== StatusCodes.CREATED) {
          this.$emit('add-unknown-error')
        }
        // try to update business name
        const businessResponse = await this.updateBusinessName(this.businessIdentifier)
        // check if update didn't succeed
        if (businessResponse?.status !== StatusCodes.OK) {
          this.$emit('add-unknown-error')
        }
        // update folio number
        await this.updateFolioNumber({
          businessIdentifier: this.businessIdentifier,
          folioNumber: this.folioNumber
        })
        // let parent know that add was successful
        this.$emit('add-success')
      } catch (exception) {
        if (exception.response?.status === StatusCodes.UNAUTHORIZED) {
          this.$emit('add-failed-invalid-code', this.passcodeLabel)
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

  private resetForm (emitCancel = false): void {
    this.businessIdentifier = ''
    this.passcode = ''
    this.folioNumber = ''
    this.$refs.addBusinessForm.resetValidation()
    this.isLoading = false
    if (emitCancel) {
      this.$emit('on-cancel')
    }
  }

  protected formatBusinessIdentifier (): void {
    this.businessIdentifierRules = [
      v => !!v || 'Incorporation Number or Registration Number is required',
      v => CommonUtils.validateIncorporationNumber(v) ||
        'Incorporation Number or Registration Number is not valid'
    ]
    this.businessIdentifier = CommonUtils.formatIncorporationNumber(this.businessIdentifier)
  }

  protected openHelp (): void {
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

.v-tooltip__content {
  background-color: RGBA(73, 80, 87, 0.95) !important;
  color: white !important;
  border-radius: 4px;
  font-size: 12px !important;
  line-height: 18px !important;
  padding: 15px !important;
  letter-spacing: 0;
  max-width: 270px !important;
}

.v-tooltip__content:after {
  content: "" !important;
  position: absolute !important;
  top: 50% !important;
  right: 100% !important;
  margin-top: -10px !important;
  border-top: 10px solid transparent !important;
  border-bottom: 10px solid transparent !important;
  border-right: 8px solid RGBA(73, 80, 87, .95) !important;
}

.top-tooltip:after {
  top: 100% !important;
  left: 45% !important;
  margin-top: 0 !important;
  border-right: 10px solid transparent !important;
  border-left: 10px solid transparent !important;
  border-top: 8px solid RGBA(73, 80, 87, 0.95) !important;
}

.add-business-unordered-list {
  list-style: none;
  padding-left: 1rem;

  li {
    margin-left: 1.5rem;

    &::before {
      content: "\2022";
      display: inline-block;
      width: 1.5em;
      color: $gray9;
      margin-left: -1.5em;
    }
  }
}

.underline-dotted {
  border-bottom: dotted;
  border-bottom-width: 2px;
}

.form__btns {
  display: flex;
  justify-content: flex-end;

  .v-btn + .v-btn {
    margin-left: 0.5rem;
  }

  #cancel-button,
  #add-button {
    min-width: unset !important;
    width: 100px;
  }

  // override disabled button color
  .v-btn[disabled]:not(.v-btn--flat):not(.v-btn--text):not(.v-btn--outlined) {
    color: white !important;
    background-color: $app-blue !important;
    opacity: 0.4;
  }
}
</style>
