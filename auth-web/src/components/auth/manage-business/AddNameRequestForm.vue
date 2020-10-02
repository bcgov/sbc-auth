<template>
  <div class="passcode-form">
    <v-form ref="addNRForm" lazy-validation>
      <fieldset>
        <v-expand-transition>
          <div class="passcode-form__alert-container" v-show="validationError">
            <v-alert
              :value="true"
              color="error"
              icon="warning"
            >{{validationError}}
            </v-alert>
          </div>
        </v-expand-transition>
          <v-text-field
            filled
            label="Enter a Name Request Number"
            hint="Example: NR 1234567"
            req
            persistent-hint
            :rules="entityNumRules"
            v-model="nameRequestNumber"
            @blur="incorpNumFormat"
            data-test="business-identifier"
          ></v-text-field>
          <v-text-field
            filled
            label="Enter the Applicant Phone Number"
            hint="Example: 555-555-5555"
            persistent-hint
            :rules="entityPhoneNumberRules"
            v-model="applicantPhoneNumber"
            type="tel"
            data-test="entity-phonenumber"
          ></v-text-field>
          <div class="font-weight-bold ml-3 mb-2">or</div>
          <v-text-field
            filled
            label="Enter the Applicant Email Address"
            hint="Example: name@email.com"
            persistent-hint
            :rules="entityEmailRules"
            v-model="applicantEmail"
            data-test="entity-email"
          ></v-text-field>
      </fieldset>
      <div class="form__btns mt-8">
        <v-btn large text class="pl-2 pr-2 lost-passcode-btn" data-test="forgot-passcode-button" @click.stop="openHelp()">
          <v-icon>mdi-help-circle-outline</v-icon>
          <span>I lost or forgot my Name Request (NR) Number</span>
        </v-btn>
        <v-btn
          data-test="add-business-button"
          large color="primary"
          :disabled="!isFormValid()"
          @click="add"
          :loading="isLoading"
        >
          <span>Add</span>
        </v-btn>
        <v-btn large depressed color="default" class="ml-2" data-test="cancel-button" @click="cancel">
          <span>Cancel</span>
        </v-btn>
      </div>
    </v-form>
    <HelpDialog
      :helpDialogFor="'Name Request (NR) Number'"
      ref="helpDialog"
    ></HelpDialog>
  </div>
</template>

<script lang="ts">
import { Business, BusinessRequest, FolioNumberload, LoginPayload } from '@/models/business'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { FilingTypes, LegalTypes } from '@/util/constants'
import { mapActions, mapMutations, mapState } from 'vuex'
import BusinessModule from '@/store/modules/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { CreateNRAffiliationRequestBody } from '@/models/affiliation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { Organization } from '@/models/Organization'
import { getModule } from 'vuex-module-decorators'
import { mask } from 'vue-the-mask'

@Component({
  directives: {
    mask
  },
  components: {
    HelpDialog
  },
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('business', [
      'addNameRequest',
      'createNamedBusiness',
      'updateFolioNumber'
    ])
  }
})
export default class AddNameRequestForm extends Vue {
  private readonly currentOrganization!: Organization
  private readonly addNameRequest!: (payload: CreateNRAffiliationRequestBody) => any
  private readonly createNamedBusiness!: (filingBody: BusinessRequest) => any
  private readonly updateFolioNumber!: (folioNumberload: FolioNumberload) => void
  private validationError = ''
  private entityNumRules = [
    v => !!v || 'Name Request Number is required',
    v => CommonUtils.validateNameRequestNumber(v) || 'Name Request Number is invalid'
  ]
  private entityPhoneNumberRules = [
    v => this.isInputEntered(v, 'phone') || 'Phone number is required',
    v => !(v.length > 12) || 'Phone number is invalid'
  ]
  private entityEmailRules = [
    v => this.isInputEntered(v, 'email') || 'Email is required',
    v => this.isValidateEmail(v) || 'Email is Invalid'
  ]
  private VUE_APP_COPS_REDIRECT_URL = ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private nameRequestNumber: string = ''
  private applicantPhoneNumber: string = ''
  private applicantEmail: string = ''
  private passcode: string = ''
  private folioNumber: string = ''
  private isLoading = false

  $refs: {
    addNRForm: HTMLFormElement,
    helpDialog: HelpDialog
  }

  private isFormValid (): boolean {
    return !!this.nameRequestNumber &&
      (!!this.applicantPhoneNumber || !!this.applicantEmail)
  }

  private isInputEntered (value: any, inputType: string) {
    return (!!((inputType === 'email') ? this.applicantPhoneNumber : this.applicantEmail) || !!value)
  }

  private isValidateEmail (value: any) {
    return ((!!this.applicantPhoneNumber && !!value) || !!CommonUtils.validateEmailFormat(value))
  }

  async add () {
    if (this.isFormValid()) {
      this.isLoading = true
      try {
        // attempt to add business
        const nrResponse = await this.addNameRequest({
          businessIdentifier: this.nameRequestNumber,
          phone: this.applicantPhoneNumber.replace(/-/g, ''),
          email: this.applicantEmail
        })

        if (nrResponse?.status === 201) {
          // update the legal api if the status is success
          const filingBody: BusinessRequest = {
            filing: {
              header: {
                name: FilingTypes.INCORPORATION_APPLICATION,
                accountId: this.currentOrganization.id
              },
              business: {
                legalType: LegalTypes.BCOMP
              },
              incorporationApplication: {
                nameRequest: {
                  legalType: LegalTypes.BCOMP,
                  nrNumber: this.nameRequestNumber
                }
              }
            }
          }
          const filingResponse = await this.createNamedBusiness(filingBody)
          if (filingResponse?.errorMsg) {
            this.$emit('add-unknown-error')
          } else {
            // emit event to let parent know business added
            this.$emit('add-success')
          }
        }
      } catch (exception) {
        if (exception.response && exception.response.status === 400) {
          this.$emit('add-failed-show-msg', exception.response?.data?.message || '')
        } else if (exception.response && exception.response.status === 404) {
          this.$emit('add-failed-no-entity')
        } else {
          this.$emit('add-unknown-error')
        }
      } finally {
        this.resetForm()
      }
    }
  }

  @Emit()
  cancel () {
  }

  resetForm () {
    this.nameRequestNumber = ''
    this.applicantEmail = ''
    this.applicantPhoneNumber = ''
    this.$refs.addNRForm.resetValidation()
    this.isLoading = false
  }

  incorpNumFormat () {
    this.nameRequestNumber = CommonUtils.formatIncorporationNumber(this.nameRequestNumber, true)
  }

  openHelp () {
    this.$refs.helpDialog.open()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
  .lost-passcode-btn {
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
