<template>
  <div id="manage-business-dialog">
    <v-dialog
      attach="#entity-management"
      v-model="dialog.show"
      persistent
      scrollable
      width="730px"
      data-test-tag="add-business"
      @keydown.esc="resetForm(true)"
    >
      <v-card class="px-3">
        <v-card-title data-test="dialog-header">
          <span>Manage a B.C. Business</span>
        </v-card-title>

        <v-card-text class="py-0">
          <v-form ref="addBusinessForm" lazy-validation class="mt-0">
            <template>
              <div class="font-weight-bold mr-2 float-left">Business Name:</div>
              <div>{{businessName}}</div>

              <div class="font-weight-bold mr-2 float-left">Incorporation Number:</div>
              <div>{{businessIdentifier}}</div>

              <div class="my-5">
                You must be authorized to manage this business. You can be authorized in one of the following ways:
              </div>
            </template>

            <v-card class="mx-auto" flat>
              <v-list class="mr-2">

                <v-list-group class="top-of-list" eager v-model="passcodeOption">
                  <template v-slot:activator>
                    <v-list-item-title>Use the business {{passwordText}}</v-list-item-title>
                  </template>
                  <div class="item-content">
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
                      type="password"
                      class="passcode mt-0 mb-2"
                      :aria-label="passcodeLabel"
                    />
                    <Certify
                      v-if="isBusinessIdentifierValid && isFirm"
                      :certifiedBy="certifiedBy"
                      entity="registered entity"
                      @update:isCertified="isCertified = $event"
                      class="certify"
                      :class="(isBusinessIdentifierValid && showAuthorization) ? 'mt-4 mb-5' : 'mt-6 mb-5'"
                    />
                  </div>
                </v-list-group>

                <v-list-group v-model="emailOption">
                  <template v-slot:activator>
                    <v-list-item-title>
                      Confirm authorization using your registered office email address
                      <div class="subtitle"> (If you forgot or don't have a business {{passwordText}})</div>
                    </v-list-item-title>
                  </template>
                  <div style="color:#313132;">
                    <div>
                      An email will be sent to the registered office contact email of the business:
                    </div>
                    <div><b>{}**@********</b></div>
                    <div style="margin:6px 5px 16px 0 !important">
                      To confirm your access, please click on the link in the email. This will add the business to your Business Registry List. The link is valid for 15 minutes.
                    </div>
                  </div>
                </v-list-group>

                <v-list-group v-model="requestAuthBusinessOption">
                  <template v-slot:activator>
                    <v-list-item-title>Request authorization from the business</v-list-item-title>
                  </template>
                  <div style="color:#313132;">
                    place holder
                  </div>
                </v-list-group>

                <v-list-group v-model="requestAuthRegistryOption">
                  <template v-slot:activator>
                    <v-list-item-title>Request authorization from the Business Registry</v-list-item-title>
                  </template>
                  <div style="color:#313132;">
                    place holder
                  </div>
                </v-list-group>

              </v-list>
            </v-card>

          </v-form>
        </v-card-text>

        <v-card-actions class="mt-5 form__btns">
          <v-btn
            v-if="isBusinessIdentifierValid && !isFirm"
            large text
            class="px-0 mr-auto primary--text"
            id="forgot-button"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>Help</span>
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
            class="px-7"
            :loading="isLoading"
            @click="add()"
          >
            <span>Manage This Business</span>
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <HelpDialog
      :helpDialogBlurb="helpDialogBlurb"
      ref="helpDialog"
    />

  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import BusinessLookup from './BusinessLookup.vue'
import Certify from './Certify.vue'
import CommonUtils from '@/util/common-util'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { LoginPayload } from '@/models/business'
import { StatusCodes } from 'http-status-codes'
import { mapActions } from 'vuex'

@Component({
  components: {
    BusinessLookup,
    Certify,
    HelpDialog
  },
  methods: {
    ...mapActions('business', [
      'addBusiness',
      'updateBusinessName'
    ])
  }
})
export default class ManageBusinessDialog extends Vue {
  $refs: {
    addBusinessForm: HTMLFormElement,
    helpDialog: HelpDialog,
  }

  @Prop() dialog: {show: boolean;}
  @Prop({ default: false }) readonly isGovStaffAccount: boolean
  @Prop({ default: '' }) readonly userFirstName: string
  @Prop({ default: '' }) readonly userLastName: string
  @Prop({ default: '' }) readonly businessName: string
  @Prop({ default: '' }) readonly businessIdentifier: string

  private readonly addBusiness!: (loginPayload: LoginPayload) => any
  private readonly updateBusinessName!: (businessNumber: string) => any

  // local variables
  businessIdentifierRules = []
  passcode = '' // aka password or proprietor/partner
  isLoading = false
  isCertified = false // firms only
  authorizationName = ''

  passcodeOption = false
  emailOption = false
  requestAuthBusinessOption = false
  requestAuthRegistryOption = false

  readonly authorizationLabel = 'Legal name of Authorized Person (e.g., Last Name, First Name)'

  readonly authorizationMaxLength = 100

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
    if (this.isCooperative) return 'Enter the passcode you have setup in Coporate Online, must be exactly 9 digits'
    return 'Enter the password you have setup in Coporate Online, must be 8 to 15 characters'
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
      v => !!v || 'Password is required, enter the password you have setup in Coporate Online',
      v => CommonUtils.validateCorporatePassword(v) || 'Password must be 8 to 15 characters'
    ]
  }

  get passwordText (): string {
    return (this.isCooperative ? 'passcode' : 'password')
  }

  get helpDialogBlurb (): string {
    if (this.isCooperative) {
      return 'If you have not received your Access Letter from BC Registries, or have lost your Passcode, ' +
        'please contact us at:'
    } else {
      return `If you have trouble with getting the email, have lost your company password/passcode, 
        or have problems getting the authorization, please contact us at: `
    }
  }
  get isFormValid (): boolean {
    // business id is required
    // passcode is required
    // firms must accept certify clause
    // staff users must enter names, only if business id is valid and is a firm
    // validate the form itself (according to the components' rules/state)
    return (
      !!this.businessIdentifier &&
      !!this.passcode &&
      (!this.isFirm || this.isCertified) &&
      (!(this.isBusinessIdentifierValid && this.isFirm) || !!this.certifiedBy) &&
      this.$refs.addBusinessForm.validate()
    )
  }

  async add (): Promise<void> {
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
        // let parent know that add was successful
        this.$emit('add-success')
      } catch (exception) {
        if (exception.response?.status === StatusCodes.UNAUTHORIZED) {
          this.$emit('add-failed-invalid-code', this.passcodeLabel)
        } else if (exception.response?.status === StatusCodes.NOT_FOUND) {
          this.$emit('add-failed-no-entity')
        } else if (exception.response?.status === StatusCodes.NOT_ACCEPTABLE) {
          this.$emit('add-failed-passcode-claimed')
        } else if (exception.response?.status === StatusCodes.BAD_REQUEST) {
          console.log(exception.response?.data?.code === 'DATA_ALREADY_EXISTS')
          this.$emit('business-already-added', { name: this.businessName, identifier: this.businessIdentifier })
        } else {
          this.$emit('add-unknown-error')
        }
      } finally {
        this.resetForm()
      }
    }
  }

  resetForm (emitCancel = false): void {
    this.passcode = ''
    this.authorizationName = ''
    this.passcodeOption = false
    this.emailOption = false
    this.requestAuthBusinessOption = false
    this.requestAuthRegistryOption = false
    this.$refs.addBusinessForm.resetValidation()
    this.isLoading = false
    if (emitCancel) {
      this.$emit('on-cancel')
    }
    this.dialog.show = false
  }

  formatBusinessIdentifier (): void {
    this.businessIdentifierRules = [
      v => !!v || 'Incorporation Number or Registration Number is required',
      v => CommonUtils.validateIncorporationNumber(v) ||
        'Incorporation Number or Registration Number is not valid'
    ]
  }

  openHelp (): void {
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

::v-deep {

  .v-list-group{
    border-bottom: 1px solid rgb(228, 228, 228);
    &.top-of-list{
      border-top: 1px solid rgb(228, 228, 228);
    }
    .item-content{
      color: #000 !important;
    }
  }

  .v-list-item{
    background: #FFFFFF;
    height: 4rem !important;
    margin: 0 !important;
  }

  .v-list-item--link>
  .v-list-item__title{
    font-weight: 300 !important;
    margin-left:-1rem !important;
    color: var(--v-primary-base) !important;
    .subtitle {
      line-height: 1.5rem;
      font-size: 9pt;
      color: var(--v-primary-base) !important;
      font-weight: normal;
    }
  }

  .v-list-item--active>
  .v-list-item__title{
    font-weight: 600 !important;
    margin-left:-1rem !important;
    color: #000 !important;
    .subtitle {
      line-height: 1.5rem;
      font-size: 9pt;
      color: #000 !important;
      font-weight: normal;
    }
  }

  .v-list-item__content{
    color: #000 !important;
  }
}
</style>
