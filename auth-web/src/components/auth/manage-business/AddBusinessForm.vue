<template>
  <div class="add-business-form">
    <v-form ref="addBusinessForm" lazy-validation>
      <fieldset>
        <legend hidden>Incorporation Number and Passcodes</legend>
        <v-expand-transition>
          <div class="add-business-form__alert-container" v-show="validationError">
            <v-alert
              :value="true"
              color="error"
              icon="warning"
            >{{validationError}}</v-alert>
          </div>
        </v-expand-transition>
        <v-text-field
          filled
          label="Enter your Incorporation Number"
          hint="Example: CP1234567"
          req
          persistent-hint
          :rules="incorpNumRules"
          v-model="incorpNum"
          @blur="formatIncorpNum()"
          data-test="incorp-num"
        />
        <v-text-field
          filled
          label="Enter your Passcode"
          hint="Passcode must be exactly 9 digits"
          persistent-hint
          :rules="passcodeRules"
          :maxlength="9"
          v-model="passcode"
          autocomplete="off"
          data-test="passcode"
        />
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
            :maxlength="50"
            v-model="folioNumber"
            data-test="folionumber"
          />
        </div>
        <div class="form__btns mt-6">
          <v-btn
            large text
            class="pl-2 pr-2 lost-passcode-btn"
            data-test="forgot-passcode-button"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            <span>I lost or forgot my passcode</span>
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
            @click="cancel()"
          >
            <span>Cancel</span>
          </v-btn>
        </div>
      </fieldset>
    </v-form>

    <HelpDialog
      :helpDialogFor="'Passcode'"
      ref="helpDialog"
    />
  </div>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { FolioNumberload, LoginPayload } from '@/models/business'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { Organization } from '@/models/Organization'

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
  private validationError = ''
  private incorpNumRules = [
    v => !!v || 'Incorporation Number is required',
    v => CommonUtils.validateIncorporationNumber(v) || 'Incorporation Number is invalid'
  ]
  private passcodeRules = [
    v => !!v || 'Passcode is required',
    v => v?.length >= 9 || 'Passcode must be exactly 9 digits'
  ]
  private incorpNum = ''
  private passcode = ''
  private folioNumber = ''
  private isLoading = false

  $refs: {
    addBusinessForm: HTMLFormElement,
    helpDialog: HelpDialog
  }

  private isFormValid (): boolean {
    return !!this.incorpNum &&
      !!this.passcode &&
      this.$refs.addBusinessForm.validate()
  }

  private async add (): Promise<void> {
    if (this.isFormValid()) {
      this.isLoading = true
      try {
        // attempt to add business
        const addResponse = await this.addBusiness({
          businessIdentifier: this.incorpNum,
          passCode: this.passcode
        })
        if (addResponse?.status === 201) {
          const businessResponse = await this.updateBusinessName(this.incorpNum)
          if (businessResponse?.status === 200) {
            // update folio number if the business name updated successfully
            await this.updateFolioNumber({
              businessIdentifier: this.incorpNum,
              folioNumber: this.folioNumber
            })

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
  private cancel (): void {}

  resetForm () {
    this.incorpNum = ''
    this.passcode = ''
    this.$refs.addBusinessForm.resetValidation()
    this.isLoading = false
  }

  private formatIncorpNum (): void {
    this.incorpNum = CommonUtils.formatIncorporationNumber(this.incorpNum)
  }

  private openHelp (): void {
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
