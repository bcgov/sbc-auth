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
            v-mask="['###-###-####']"
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
        <v-btn large text class="pl-2 pr-2 lost-passcode-btn" data-test="forgot-passcode-button" @click.stop="helpDialog = true">
          <v-icon>mdi-help-circle-outline</v-icon>
          <span>I lost or forgot my Name Request (NR) Number</span>
        </v-btn>
        <v-btn
          data-test="add-business-button"
          large color="primary"
          :disabled="!isFormValid()"
          @click="add"
        >
          <span>Add</span>
        </v-btn>
        <v-btn large depressed color="default" class="ml-2" data-test="cancel-button" @click="cancel">
          <span>Cancel</span>
        </v-btn>
      </div>
    </v-form>
    <v-dialog v-model="helpDialog" max-width="640">
      <v-card>
        <v-card-title>Need Assistance?</v-card-title>
        <v-card-text>
          <p class="mb-7">If you have not received your Access Letter from BC Registries, or have lost your Name Request (NR) Number, please contact us at:</p>
          <ul class="contact-info__list mb-7">
            <li>
              <span>Toll Free:</span>&nbsp;&nbsp;{{ $t('techSupportTollFree') }}
            </li>
            <li>
              <span>Phone:</span>&nbsp;&nbsp;{{ $t('techSupportPhone') }}
            </li>
            <li>
              <span>Email:</span>&nbsp;&nbsp;<a v-bind:href="'mailto:' + $t('techSupportEmail') + '?subject=' + $t('techSupportEmailSubject')">{{ $t('techSupportEmail') }}</a>
            </li>
          </ul>
          <div>
            <p class="mb-0"><strong>Hours of Operation:</strong><br>Monday to Friday, 8:30am - 4:30pm <span title="Pacific Standard Time">PST</span></p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn large color="primary" @click="helpDialog = false">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Business, FolioNumberload, LoginPayload } from '@/models/business'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import BusinessModule from '@/store/modules/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { Organization } from '@/models/Organization'
import { getModule } from 'vuex-module-decorators'
import { mask } from 'vue-the-mask'

@Component({
  directives: {
    mask
  },
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('business', ['addBusiness', 'updateFolioNumber'])
  }
})
export default class AddNameRequestForm extends Vue {
  private readonly currentOrganization!: Organization
  private readonly addBusiness!: (payload: LoginPayload) => void
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
  private helpDialog = false

  $refs: {
    addNRForm: HTMLFormElement
  }

  private isFormValid (): boolean {
    return !!this.nameRequestNumber &&
      (!!this.applicantPhoneNumber || !!this.applicantEmail)
  }

  private isInputEntered (value: any, ipType: string) {
    return (!!((ipType === 'email') ? this.applicantPhoneNumber : this.applicantEmail) || !!value)
  }

  private isValidateEmail (value: any) {
    return ((!!this.applicantPhoneNumber && !!value) || !!CommonUtils.validateEmailFormat(value))
  }

  private redirectToNext (): void {
    this.$router.push(`/account/${this.currentOrganization.id}`)
  }

  async add () {
    if (this.isFormValid()) {
      try {
        // attempt to add business
        await this.addBusiness({
          businessIdentifier: this.nameRequestNumber.trim().toUpperCase(),
          phone: this.applicantPhoneNumber,
          email: this.applicantEmail
        })

        // await this.updateFolioNumber({ businessIdentifier: this.nameRequestNumber.trim().toUpperCase(), folioNumber: this.folioNumber })

        // emit event to let parent know business added
        this.$emit('add-success')
        this.$emit('close-add-nr-modal')
      } catch (exception) {
        if (exception.response && exception.response.status === 401) {
          this.$emit('add-failed-invalid-code')
        } else if (exception.response && exception.response.status === 404) {
          this.$emit('add-failed-no-entity')
        } else if (exception.response && exception.response.status === 406) {
          this.$emit('add-failed-passcode-claimed')
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
  }

  incorpNumFormat () {
    this.nameRequestNumber = this.nameRequestNumber.trim().toUpperCase()
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';
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
