<template>
  <div class="passcode-form">
    <v-form ref="addBusinessForm" lazy-validation>
      <fieldset>
        <legend class="mb-4" hidden>Incorporation Number and Passcodes</legend>
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
          <v-btn large text class="pl-2 pr-2 lost-passcode-btn" data-test="forgot-passcode-button" @click.stop="openHelp()">
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>I lost or forgot my passcode</span>
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
      </fieldset>
    </v-form>
    <HelpDialog
      :helpDialogFor="'Passcode'"
      ref="helpDialog"
    ></HelpDialog>
  </div>
</template>

<script lang="ts">
import { Business, FolioNumberload, LoginPayload } from '@/models/business'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import BusinessModule from '@/store/modules/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import HelpDialog from '@/components/auth/HelpDialog.vue'
import { Organization } from '@/models/Organization'
import { getModule } from 'vuex-module-decorators'

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
  private readonly updateBusinessName!: (businessIdentifier: string) => any
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
  private isLoading = false
  private isLoading = false

  $refs: {
    addBusinessForm: HTMLFormElement,
    helpDialog: HelpDialog
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
      this.isLoading = true
      try {
        // attempt to add business
        const addResponse = await this.addBusiness({ businessIdentifier: this.businessIdentifier, passCode: this.passcode })

        if (addResponse?.status === 201) {
          const businessResponse = await this.updateBusinessName(this.businessIdentifier)
          if (businessResponse?.status === 200) {
            // update folio number if the business name updated successfully
            await this.updateFolioNumber({ businessIdentifier: this.businessIdentifier, folioNumber: this.folioNumber })
            // emit event to let parent know business added
            this.$emit('add-success')
          } else {
            this.$emit('add-unknown-error')
          }
        }
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
    this.isLoading = false
  }

  incorpNumFormat () {
    this.businessIdentifier = CommonUtils.formatIncorporationNumber(this.businessIdentifier)
  }

  openHelp () {
    this.$refs.helpDialog.open()
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
