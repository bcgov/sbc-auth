<template>
  <div class="passcode-form">
    <v-form ref="addBusinessForm" lazy-validation>
      <fieldset>
        <legend class="mb-4" hidden>Incorporation Number and Passcode</legend>
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
            label="Enter your Incorporation Number"
            hint="Example: CP1234567"
            req
            persistent-hint
            :rules="entityNumRules"
            v-model="businessIdentifier"
            @blur="incorpNumFormat"
            data-test="business-identifier"
          ></v-text-field>
          <v-text-field
            filled
            label="Enter your Passcode"
            hint="Passcode must be exactly 9 digits"
            persistent-hint
            :rules="entityPasscodeRules"
            :maxlength="9"
            v-model="passcode"
            autocomplete="off"
            data-test="business-passcode"
          ></v-text-field>

      </fieldset>
      <fieldset class="mt-8">
        <legend class="mb-4">Folio / Reference Number (optional)</legend>
        <p class="mb-8">
          If you file forms for a number of companies, you may want to enter a folio or reference number to help you keep track of your transactions.
        </p>
        <div class="folioNumber-form__row">
          <v-text-field
            filled
            label="Folio or Reference Number"
            persistent-hint
            :maxlength="50"
            v-model="folioNumber"
          ></v-text-field>
        </div>
        <div class="form__btns mt-6">
          <v-btn large text class="pl-2 pr-2 lost-passcode-btn" data-test="forgot-passcode-button" @click.stop="helpDialog = true">
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>I lost or forgot my passcode</span>
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
      </fieldset>
    </v-form>
    <v-dialog v-model="helpDialog" max-width="640">
      <v-card>
        <v-card-title>Need Assistance?</v-card-title>
        <v-card-text>
          <p class="mb-7">If you have not received your Access Letter from BC Registries, or have lost your Passcode, please contact us at:</p>
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

@Component({
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('business', ['addBusiness', 'updateFolioNumber'])
  }
})
export default class AddBusinessForm extends Vue {
  private readonly currentOrganization!: Organization
  private readonly addBusiness!: (loginPayload: LoginPayload) => void
  private readonly updateFolioNumber!: (folioNumberload: FolioNumberload) => void
  private validationError = ''
  private entityNumRules = [
    v => !!v || 'Incorporation Number is required',
    v => CommonUtils.validateIncorporationNumber(v) || 'Incorporation Number is invalid'
  ]
  private entityPasscodeRules = [
    v => !!v || 'Passcode is required',
    v => v.length >= 9 || 'Passcode must be exactly 9 digits'
  ]
  private VUE_APP_COPS_REDIRECT_URL = ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private businessIdentifier: string = ''
  private passcode: string = ''
  private folioNumber: string = ''
  private helpDialog = false

  $refs: {
    addBusinessForm: HTMLFormElement
  }

  private isFormValid (): boolean {
    return !!this.businessIdentifier &&
      !!this.passcode &&
      this.$refs.addBusinessForm.validate()
  }

  private redirectToNext (): void {
    this.$router.push(`/account/${this.currentOrganization.id}`)
  }

  async add () {
    if (this.isFormValid()) {
      try {
        // close modal but continue to work in background
        this.$emit('close-add-business-modal')

        // attempt to add business
        await this.addBusiness({ businessIdentifier: this.businessIdentifier.trim().toUpperCase(), passCode: this.passcode })

        await this.updateFolioNumber({ businessIdentifier: this.businessIdentifier.trim().toUpperCase(), folioNumber: this.folioNumber })

        // emit event to let parent know business added
        this.$emit('add-success')
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
  cancel () {}

  resetForm () {
    this.businessIdentifier = ''
    this.passcode = ''
    this.$refs.addBusinessForm.resetValidation()
  }

  incorpNumFormat () {
    this.businessIdentifier = CommonUtils.formatIncorporationNumber(this.businessIdentifier)
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
