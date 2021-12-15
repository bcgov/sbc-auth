<template>
  <div>
    <v-form ref="setupGovmAccountForm">
      <!-- Name of Account -->
      <v-row>
        <v-col cols="12" class="pb-0 mb-2">
          <h4 class="mb-2">Enter Ministry Information for this account</h4>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="">
          <v-text-field
            filled
            label="Ministry Name"
            v-model.trim="ministryName"
            :rules="ministryNameRules"
            persistent-hint
            :disabled="saving"
            data-test="input-ministry-name"
          >
          </v-text-field>
        </v-col>
        <v-col cols="12" class="">
          <v-text-field
            filled
            label="Branch/Division (if applicable)"
            v-model.trim="branchName"
            persistent-hint
            :disabled="saving"
            data-test="input-branch-name"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <!-- Email/Confirm Email -->
      <v-row>
        <v-col cols="12" class="pb-0">
          <h4 class="mb-2">Account Admin Contact</h4>
          <p class="mb-6">Enter the email address of the ministry's employee. An email will be sent this user
to verify and activate this account. This user will be the admin of this account.</p>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="pt-0 pb-0">
          <v-text-field
            filled
            label="Email Address"
            v-model.trim="email"
            :rules="emailRules"
            persistent-hint
            :disabled="saving"
            data-test="input-email-address"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="pt-0 pb-0">
          <v-text-field
            filled
            label="Confirm Email Address"
            v-model.trim="emailConfirm"
            :rules="emailRules"
            persistent-hint
            :error-messages="emailMatchError()"
            :disabled="saving"
            data-test="input-confirm-email-address"
          >
          </v-text-field>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" class="form__btns pb-0">
          <v-btn
            large
            color="primary"
            class="mr-2 submit-form-btn"
            :loading="saving"
            :disabled="!isFormValid() || saving"
            @click="save"
            data-test="save-button"
          >Send Invite</v-btn>
          <v-btn
            large
            depressed
            class="cancel-btn"
            color="default"
            :disable="saving"
            @click="cancel"
            data-test="cancel-button"
          >Cancel</v-btn>
        </v-col>
      </v-row>
    </v-form>
    <!-- Error Dialog -->
    <ModalDialog
      ref="errorDialog"
      :title="dialogTitle"
      :text="dialogText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="error" @click="close()" data-test="dialog-ok-button">OK</v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { AccessType, Account, Pages } from '@/util/constants'
import { Component, Vue } from 'vue-property-decorator'
import { CreateRequestBody, MembershipType, Organization } from '@/models/Organization'
import CommonUtils from '@/util/common-util'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component({
  components: {
    ModalDialog
  }
})
export default class SetupAccountForm extends Vue {
  @OrgModule.Action('createOrgByStaff') private createOrgByStaff!: (
    requestBody: CreateRequestBody
  ) => Promise<Organization>

  @OrgModule.Action('createInvitation') private createInvitation!: (Invitation) => Promise<void>

  public ministryName: string = ''
  public branchName: string = ''
  public errorMessage: string = ''
  public saving = false
  public loader = false
  public email = ''
  public emailConfirm = ''
  public dialogTitle = ''
  public dialogText = ''
  public emailRules = CommonUtils.emailRules()

  $refs: {
    setupGovmAccountForm: HTMLFormElement,
    errorDialog: ModalDialog
  }

  public readonly ministryNameRules = [
    v => !!v || 'A ministry name is required'
  ]

  private emailMatchError () {
    return (this.email === this.emailConfirm) ? null : 'Email Address does not match'
  }

  private isFormValid (): boolean {
    return !!this.ministryName &&
      !this.emailMatchError() &&
      this.$refs.setupGovmAccountForm.validate()
  }

  public async save () {
    this.loader = this.saving
    if (this.isFormValid()) {
      const createRequestBody: CreateRequestBody = {
        name: this.ministryName,
        accessType: AccessType.GOVM,
        branchName: this.branchName,
        typeCode: Account.PREMIUM
      }

      try {
        this.saving = true
        const organization = await this.createOrgByStaff(createRequestBody)
        await this.createInvitation({
          recipientEmail: this.email,
          sentDate: new Date(),
          membership: [{ membershipType: MembershipType.Admin, orgId: organization.id }]
        })
        this.saving = false
        this.loader = this.saving
        this.$router.push({ path: `/staff-setup-account-success/${AccessType.GOVM.toLowerCase()}/${this.ministryName}` })
      } catch (err) {
        this.saving = false
        switch (err.response.status) {
          case 409:
            this.errorMessage =
              'An account with this name already exists. Try a different account name.'
            break
          case 400:
            if (err.response.data.code === 'MAX_NUMBER_OF_ORGS_LIMIT') {
              this.errorMessage = 'Maximum number of accounts reached'
            } else {
              this.errorMessage = 'Invalid account name'
            }
            break
          default:
            this.errorMessage =
              'Something went wrong while attempting to create this account. Please try again later.'
        }
        this.showEntityNotFoundModal(this.errorMessage)
        this.loader = this.saving
      }
    }
  }

  public cancel () {
    this.$router.push({ path: Pages.STAFF_DASHBOARD })
  }

  showEntityNotFoundModal (msg?) {
    this.dialogTitle = 'An error has occured'
    this.dialogText = msg || 'Something went wrong while attempting to create this account. Please try again later.'
    this.$refs.errorDialog.open()
  }

  close () {
    this.$refs.errorDialog.close()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Tighten up some of the spacing between rows
[class^='col'] {
  padding-top: 0;
  padding-bottom: 0;
}

.form__btns {
  display: flex;
  justify-content: flex-end;
}
</style>
