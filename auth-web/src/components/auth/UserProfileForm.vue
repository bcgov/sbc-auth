<template>
  <v-form ref="form" lazy-validation>
    <p class="mb-9" v-if="isStepperView">Enter your contact information. Once your account is created, you may add additional users and assign roles.</p>
    <v-expand-transition>
      <div class="form_alert-container" v-show="formError">
        <v-alert type="error" class="mb-3"
                 :value="true"
        >
          {{formError}}
        </v-alert>
      </div>
    </v-expand-transition>
    <!-- First / Last Name -->
    <v-row v-if="isInEditNameMode">
      <v-col cols="6" class="py-0">
        <v-text-field
          filled
          label="First Name"
          req
          persistent-hint
          hint="Your first name as it appears on your affidavit"
          :rules="firstNameRules"
          v-model="firstName"
          data-test="firstName"
        >
        </v-text-field>
      </v-col>
      <v-col cols="6" class="py-0">
        <v-text-field
          filled
          label="Last Name"
          req
          persistent-hint
          hint="Your last name as it appears on your affidavit"
          :rules="lastNameRules"
          v-model="lastName"
          data-test="lastName"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12" class="py-0 mb-4">
        <h4
          v-bind:class="{'legal-name': !isStepperView}"
          class="mb-1"
        >{{firstName}} {{lastName}}</h4>
        <div class="mb-2" v-if="!isBCEIDUser">This is your legal name as it appears on your BC Services Card.</div>
      </v-col>
    </v-row>
    <!-- Email Address -->
    <v-row>
      <v-col cols="12" class="pt-0 pb-0">
        <v-text-field
                filled
                label="Email Address"
                req
                persistent-hint
                :rules="emailRules"
                v-model="emailAddress"
                data-test="email"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" class="pt-0 pb-0">
        <v-text-field
                filled
                label="Confirm Email Address"
                req
                persistent-hint
                :error-messages="emailMustMatch()"
                v-model="confirmedEmailAddress"
                data-test="confirm-email"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" md="6" class="pt-0 pb-0">
        <v-text-field
                filled
                label="Phone Number"
                persistent-hint
                type="tel"
                v-mask="['(###) ###-####']"
                v-model="phoneNumber"
                hint="Example: (555) 555-5555"
                :rules="phoneRules"
                data-test="phone"
        >
        </v-text-field>
      </v-col>
      <v-col cols="12" md="3" class="pt-0 pb-0">
        <v-text-field
                filled label="Extension"
                persistent-hint
                :rules="extensionRules"
                v-mask="'#####'"
                v-model="extension"
                data-test="phone-extension"
        >
        </v-text-field>
      </v-col>
    </v-row>

    <v-divider class="mt-7 mb-10"></v-divider>

    <v-row>
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <!-- The deactivate profile button should be hidden for account stepper view -->
        <v-btn
          large
          depressed
          color="default"
          class="deactivate-btn"
          v-show="editing && !isStepperView"
          @click="$refs.deactivateUserConfirmationDialog.open()"
        >Deactivate my profile</v-btn>
        <!-- The reset button should be hidden in Production environment and who doesn't have tester role -->
        <v-btn
          large
          depressed
          color="default"
          class="reset-btn"
          v-show="editing && !isStepperView && isTester"
          @click="$refs.resetDialog.open()"
        >Reset</v-btn>
        <v-btn
          large
          depressed
          v-if="isStepperView"
          color="default"
          @click="goBack"
        >
          <v-icon left class="mr-2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-2"
          :disabled='!isFormValid()'
          @click="save" data-test="save-button">
          {{(isStepperView) ? 'Create Account' : 'Save'}}
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="isStepperView"
          :isEmit="true"
          @click-confirm="cancel"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>

    <!-- Modal for deactivation confirmation -->
    <ModalDialog
      ref="deactivateUserConfirmationDialog"
      :title="$t('deactivateConfirmTitle')"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:text>
        <p class="pb-1">{{ $t('deactivateConfirmText')}} <strong>{{ $t('deactivateConfirmTextEmphasis') }}</strong></p>
      </template>
      <template v-slot:actions>
        <v-btn large color="error" @click="deactivate()" :loading="isDeactivating" data-test="deactivate-confirm-button">Deactivate</v-btn>
        <v-btn large color="default" :disabled="isDeactivating" @click="cancelConfirmDeactivate()" data-test="deactivate-cancel-button">Cancel</v-btn>
      </template>
    </ModalDialog>

    <!-- Modal for deactivation failure -->
    <ModalDialog
      ref="deactivateUserFailureDialog"
      :title="$t('deactivateFailureTitle')"
      :text="$t('deactivateFailureText')"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
    </ModalDialog>

    <!-- Modal for Reset  -->
    <ModalDialog
      ref="resetDialog"
      :title="$t('resetConfirmTitle')"
      :text="$t('resetConfirmText')"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:text>
        <p class="pb-1">{{ $t('resetConfirmText')}} <strong>{{ $t('resetConfirmTextEmphasis') }}</strong></p>
      </template>
      <template v-slot:actions>
        <v-btn large color="error" @click="reset()" :loading="isReseting" data-test="reset-confirm-button">Reset</v-btn>
        <v-btn large color="default" :disabled="isReseting" @click="cancelConfirmReset()" data-test="reset-cancel-button">Cancel</v-btn>
      </template>
    </ModalDialog>

    <!-- Modal for reset failure -->
    <ModalDialog
      ref="resetFailureDialog"
      :title="$t('resetFailureTitle')"
      :text="$t('resetFailureText')"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
    </ModalDialog>
  </v-form>
</template>

<script lang="ts">

import { AccessType, Account, LoginSource, Pages, Role } from '@/util/constants'
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Contact } from '@/models/contact'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import Steppable from '@/components/auth/stepper/Steppable.vue'

import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import UserService from '@/services/user.services'
import configHelper from '@/util/config-helper'
import { getModule } from 'vuex-module-decorators'
import { mask } from 'vue-the-mask'

@Component({
  components: {
    ModalDialog,
    ConfirmCancelButton
  },
  directives: {
    mask
  },
  computed: {
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('user',
      [
        'createUserContact',
        'updateUserContact',
        'getUserProfile',
        'createAffidavit',
        'updateUserFirstAndLastName'
      ]),
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization'])
  }
})
export default class UserProfileForm extends Mixins(NextPageMixin, Steppable) {
    private readonly createUserContact!: (contact: Contact) => Contact
    private readonly updateUserContact!: (contact: Contact) => Contact
    private readonly getUserProfile!: (identifer: string) => User
    private readonly updateUserFirstAndLastName!: (user: User) => Contact

    private readonly createAffidavit!: () => User
    private firstName = ''
    private lastName = ''
    private emailAddress = ''
    private confirmedEmailAddress = ''
    private phoneNumber = ''
    private extension = ''
    private formError = ''
    private editing = false
    private deactivateProfileDialog = false
    private isDeactivating = false
    @Prop() token: string
    readonly currentOrganization!: Organization
    private readonly createOrg!: () => Promise<Organization>
    readonly syncMembership!: (orgId: number) => Promise<Member>
    readonly syncOrganization!: (orgId: number) => Promise<Organization>
    private readonly ACCOUNT_TYPE = Account
    private isTester: boolean = false
    private isReseting = false
    readonly currentUser!: KCUserProfile

    // this prop is used for conditionally using this form in both account stepper and edit profile pages
    @Prop({ default: false }) isStepperView: boolean
    @Prop({ default: AccessType.REGULAR }) stepperSource: string

    $refs: {
      deactivateUserConfirmationDialog: ModalDialog,
      deactivateUserFailureDialog: ModalDialog,
      resetDialog: ModalDialog,
      resetFailureDialog: ModalDialog,
      form: HTMLFormElement
    }

    private emailRules = [
      v => !!v || 'Email address is required',
      v => {
        const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        return pattern.test(v) || 'Valid email is required'
      }
    ]

    private phoneRules = [
      v => !v || (v.length === 0 || v.length === 14) || 'Phone number is invalid'
    ]

    private extensionRules = [
      v => !v || (v.length >= 0 || v.length <= 4) || 'Extension is invalid'
    ]

    private firstNameRules = [
      v => !!v || 'First Name is Required'
    ]

    private lastNameRules = [
      v => !!v || 'Last Name is Required'
    ]

    private get isInEditNameMode () {
      // isExtraProvStepperOr
      return this.token || (this.isStepperView && (this.stepperSource === AccessType.EXTRA_PROVINCIAL))
    }

    private get isBCEIDUser (): boolean {
      return this.currentUser?.loginSource === LoginSource.BCEID
    }

    private emailMustMatch (): string {
      return (this.emailAddress === this.confirmedEmailAddress) ? '' : 'Email addresses must match'
    }

    private isFormValid (): boolean {
      return this.$refs.form &&
        this.$refs.form.validate() &&
        this.confirmedEmailAddress === this.emailAddress
    }

    private async mounted () {
      if (!this.userProfile) {
        await this.getUserProfile('@me')
      }
      this.firstName = this.userProfile?.firstname
      this.lastName = this.userProfile?.lastname
      this.emailAddress = this.userProfile?.email
      if (this.userContact) {
        this.emailAddress = this.confirmedEmailAddress = this.userContact.email
        this.phoneNumber = this.userContact.phone
        this.extension = this.userContact.phoneExtension
        this.editing = true
      }

      if (configHelper.getAuthResetAPIUrl()) {
        this.isTester = this.currentUser?.roles?.includes(Role.Tester)
      }
    }

    private async save () {
      if (this.isFormValid()) {
        const user:User = {
          firstname: this.firstName.trim(),
          lastname: this.lastName.trim()
        }
        const contact = {
          email: this.emailAddress.toLowerCase(),
          phone: this.phoneNumber,
          phoneExtension: this.extension
        }
        if (this.stepForward) { // On stepper ;so Save the org
          this.createAccount(contact, user)
        } else {
          if (this.isBCEIDUser) {
            await this.updateUserFirstAndLastName(user)
          }
          await this.saveOrUpdateContact(contact)
          await this.getUserProfile('@me')
          // If a token was provided, that means we are in the accept invitation flow
          // so redirect to /confirmtoken
          if (this.token) {
            this.$router.push('/confirmtoken/' + this.token)
            return
          }
          this.redirectToNext()
        }
      }
    }

    private async createAccount (contact:Contact, user:User) {
      try {
        // for bceid , create affidavit first
        // TODO implement checks for bceid
        if (this.isBCEIDUser) {
          await this.createAffidavit()
          await this.updateUserFirstAndLastName(user)
        }
        const organization = await this.createOrg()
        await this.saveOrUpdateContact(contact)
        await this.getUserProfile('@me')
        await this.syncOrganization(organization.id)
        await this.syncMembership(organization.id)
        this.$store.commit('updateHeader')
        if (this.isBCEIDUser) {
          this.$router.push('/setup-non-bcsc-account-success')
        } else {
          this.$router.push('/setup-account-success')
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error(err)
        switch (err?.response?.status) {
          case 409:
            this.formError =
                    'An account with this name already exists. Try a different account name.'
            break
          case 400:
            switch (err.response.data?.code) {
              case 'MAX_NUMBER_OF_ORGS_LIMIT':
                this.formError = 'Maximum number of accounts reached'
                break
              case 'ACTIVE_AFFIDAVIT_EXISTS':
                this.formError = err.response.data.message || 'Affidavit already exists'
                break
              default:
                this.formError = 'Invalid account name'
            }
            break
          default:
            this.formError =
                    'An error occurred while attempting to create your account.'
        }
      }
    }

    private async saveOrUpdateContact (contact:Contact) {
      if (this.editing) {
        await this.updateUserContact(contact)
      } else {
        await this.createUserContact(contact)
      }
    }

    private redirectToNext () {
      this.$router.push(this.getNextPageUrl())
    }

    private cancel () {
      if (this.isStepperView) {
        this.$router.push('/')
      } else {
        window.history.back()
      }
    }

    private goBack () {
      this.stepBack(this.currentOrganization!.orgType === this.ACCOUNT_TYPE.PREMIUM)
    }

    private async deactivate (): Promise<void> {
      try {
        this.isDeactivating = true
        await UserService.deactivateUser()
        const redirectUri = encodeURIComponent(`${configHelper.getSelfURL()}/profiledeactivated`)
        this.$router.push(`/${Pages.SIGNOUT}/${redirectUri}`)
      } catch (exception) {
        this.$refs.deactivateUserFailureDialog.open()
      } finally {
        this.isDeactivating = false
      }
    }

    private cancelConfirmDeactivate () {
      this.$refs.deactivateUserConfirmationDialog.close()
    }

    private async reset (): Promise<void> {
      try {
        this.isReseting = true
        await UserService.resetUser()
        const redirectUri = encodeURIComponent(`${configHelper.getSelfURL()}/profiledeactivated`)
        this.$router.push(`/${Pages.SIGNOUT}/${redirectUri}`)
      } catch (exception) {
        this.$refs.resetFailureDialog.open()
      } finally {
        this.isReseting = false
      }
    }

    private cancelConfirmReset () {
      this.$refs.resetDialog.close()
    }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.legal-name {
  font-size: 1.25rem !important;
  font-weight: 700;
  letter-spacing: -0.02rem;
}
</style>
