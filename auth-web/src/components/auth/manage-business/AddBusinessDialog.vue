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
          <span>Manage a B.C Business</span>
        </v-card-title>

        <v-card-text class="py-2">
          <p>
           <strong>Business name:</strong> Dunder Mifflin Paper Company Inc.<br>
           <strong>Incorporation Number:</strong> BC0871349
          </p>
          <p>
            You must be authorised to manage this business. You can be authorised in one of the following ways:
          </p>

          <v-expansion-panels
      v-model="panel"
      class="bottom-border"
      accordion
    >
      <v-expansion-panels
  v-model="panel"
  class="bottom-border"
  accordion
>
  <v-expansion-panel
    id="x-panel-1"
    class="mb-4"
    :disabled="isOneOption"
    @click="identifyForm(1)"
  >
    <v-expansion-panel-header :class="{'name-options-header': isOneOption}">
      <span class="names-option-title" color="primary">Request authorization from the business</span>
      <template #actions>
        <v-icon color="primary">
          mdi-menu-down
        </v-icon>
      </template>
    </v-expansion-panel-header>

    <v-expansion-panel-content class="name-options-content pt-4">
      <p>
            Select the account you want to authorise you to perform Registries activities for  <strong>DUNDER MIFFLIN PAPER COMPANY INC. </strong>:
          </p>
      <div class="w-full">
          <v-select
            class="column-selections w-full"
            dense
            filled
            hide-details
            item-text="value"
            :items="headerSelections"
            :menu-props="{
              bottom: true,
              minWidth: '200px',
              maxHeight: 'none',
              offsetY: true,
              width: '100%'
            }"
            multiple
            return-object
            v-model="headersSelected"
          >
            <template v-slot:selection="{ index }">
              <span v-if="index === 0">Authorising Account</span>
            </template>
          </v-select>

            <p class="pt-8">
              You can add a message that will be included as part of your authorisation request.
            </p>

           <v-card-text class="pt-1 pb-1">
            <div class="relative">
              <v-textarea
                ref="textarea"
                hide-details
                dense
                filled
                placeholder="Enter an optional message"
                full-width
                v-model="message"
                :disabled="characterCount >= 4000 && message.length !== 4000"
                @input="updateCharacterCount"
              />
              <div class="character-counter absolute top-0 right-0 text-right pr-2 pt-2">
                <span :class="{'text-red-500': characterCount > 4000}">{{ characterCount }}/4000 characters</span>
              </div>
            </div>
          </v-card-text>

        </div>
    </v-expansion-panel-content>
  </v-expansion-panel>
</v-expansion-panels>

    </v-expansion-panels>

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
  large
  color="primary"
  id="add-button"
  :loading="isLoading"
  style="width: auto; display: inline-block; white-space: nowrap"
  @click="add()"
>
  <span>Mange this business</span>
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
  @Prop({ default: false }) readonly isGovStaffAccount: boolean
  @Prop({ default: '' }) readonly userFirstName: string
  @Prop({ default: '' }) readonly userLastName: string

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
  protected authorizationName = ''

  readonly authorizationLabel = 'Legal name of Authorized Person (e.g., Last Name, First Name)'

  readonly authorizationMaxLength = 100

  characterCount = 0;
  message = '';

  updateCharacterCount () {
    if (this.message.length > 4000) {
      this.message = this.message.substring(0, 4000)
    }
    this.characterCount = this.message.length
  }

  get isBusinessIdentifierValid (): boolean {
    return CommonUtils.validateIncorporationNumber(this.businessIdentifier)
  }

  get isCooperative (): boolean {
    return CommonUtils.isCooperativeNumber(this.businessIdentifier)
  }

  get isFirm (): boolean {
    return CommonUtils.isFirmNumber(this.businessIdentifier)
  }

  get showAuthorization (): boolean {
    return (this.isFirm && this.isGovStaffAccount)
  }

  get certifiedBy (): string {
    if (this.isGovStaffAccount) return this.authorizationName
    else return `${this.userLastName}, ${this.userFirstName}`
  }

  get authorizationRules (): any[] {
    return [
      v => !!v || 'Authorization is required'
    ]
  }

  get passcodeLabel (): string {
    if (this.isFirm) return 'Proprietor or Partner Name (e.g., Last Name, First Name Middlename)'
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
    // staff users must enter names
    // validate the form itself (according to the components' rules/state)
    return (
      !!this.businessIdentifier &&
      !!this.passcode &&
      (!this.isFirm || this.isCertified) &&
      !!this.certifiedBy &&
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
          certifiedByName: this.authorizationName,
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
    this.authorizationName = ''
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

// remove whitespace below error message
.authorization {
  ::v-deep .v-text-field__details {
    margin-bottom: 0 !important;
  }
}
</style>
