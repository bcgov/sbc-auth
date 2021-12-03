<template>
  <v-form ref="form" lazy-validation data-test="form-profile">
    <p class="mb-9" v-if="isStepperView">Enter your contact information. Once your account is created, you may add additional users and assign roles.</p>
    <p class="mb-7" v-if="isAffidavitUpload">
      This will be reviewed by Registries staff and the account will be approved
      when authenticated.
    </p>
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
        <!-- The deactivate profile button should be hidden for account stepper view and for admin affidavit BCeId flow -->
        <v-btn
          large
          depressed
          color="default"
          class="deactivate-btn"
          v-show="editing && !isStepperView && !isAffidavitUpload"
          @click="$refs.deactivateUserConfirmationDialog.open()"
          data-test="btn-profile-deactivate"
        >Deactivate my profile</v-btn>
        <!-- The reset button should be hidden in Production environment and who doesn't have tester role and for admin affidavit BCeId flow  -->
        <v-btn
          large
          depressed
          color="default"
          class="reset-btn"
          v-show="editing && !isStepperView && isTester && !isAffidavitUpload"
          @click="$refs.resetDialog.open()"
          data-test="btn-profile-reset"
        >Reset</v-btn>
        <v-btn
          large
          depressed
          v-if="isStepperView || isAffidavitUpload"
          color="default"
          @click="goBack"
          data-test="btn-back"
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
          v-if="!isStepperView || isAffidavitUpload"
          @click="save"
          data-test="save-button"
        >
          {{ isAffidavitUpload ? 'Submit' :  'Save' }}
        </v-btn>
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-3"
          :disabled='!isFormValid()'
          @click="next"
          v-if="isStepperView"
          data-test="next-button"
        >
          <span v-if="enablePaymentMethodSelectorStep">
            Next
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>
          <span v-if="!enablePaymentMethodSelectorStep">Create Account</span>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="isStepperView"
          :isEmit="true"
          @click-confirm="cancel"
          v-if="!isAffidavitUpload"
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

import { AccessType, Account, LDFlags, LoginSource, Pages, Role } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { User, UserProfileData } from '@/models/user'
import { mapActions, mapMutations, mapState } from 'vuex'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { Contact } from '@/models/contact'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import UserService from '@/services/user.services'
import configHelper from '@/util/config-helper'
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
    ...mapState('org', ['currentOrganization']),
    ...mapState('user', [
      'userProfileData'
    ])
  },
  methods: {
    ...mapMutations('user', ['setUserProfileData', 'setUserProfile']),
    ...mapActions('user',
      [
        'createUserContact',
        'updateUserContact',
        'getUserProfile',
        'createAffidavit',
        'updateUserFirstAndLastName'
      ]),
    ...mapActions('org', ['syncMembership', 'syncOrganization'])
  }
})
export default class UserProfileForm extends Mixins(NextPageMixin, Steppable) {
    @Prop({ default: false }) isAffidavitUpload: boolean
    private readonly createUserContact!: (contact?: Contact) => Contact
    private readonly updateUserContact!: (contact?: Contact) => Contact
    private readonly getUserProfile!: (identifer: string) => User
    private readonly updateUserFirstAndLastName!: (user?: User) => Contact
    private readonly setUserProfileData!: (userProfile: UserProfileData | undefined) => void
    private readonly setUserProfile!: (userProfile: User | undefined) => void

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
    readonly userProfileData!: UserProfileData
    readonly syncMembership!: (orgId: number) => Promise<Member>
    readonly syncOrganization!: (orgId: number) => Promise<Organization>
    private readonly ACCOUNT_TYPE = Account
    private isTester: boolean = false
    private isReseting = false
    readonly currentUser!: KCUserProfile

    // this prop is used for conditionally using this form in both account stepper and edit profile pages
    @Prop({ default: false }) isStepperView: boolean
    @Prop({ default: AccessType.REGULAR }) stepperSource: string
    // need to cleat user profile in stepper BCEID re-upload time. if need to reset profile pass this
    @Prop({ default: false }) clearForm: boolean

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
      return this.isAffidavitUpload || this.token || (this.isStepperView && (this.stepperSource === AccessType.EXTRA_PROVINCIAL))
    }

    private get isBCEIDUser (): boolean {
      return this.currentUser?.loginSource === LoginSource.BCEID
    }

    private get enablePaymentMethodSelectorStep (): boolean {
      return LaunchDarklyService.getFlag(LDFlags.PaymentTypeAccountCreation) || false
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
      let user: any = {}
      // clear user profile data
      if (!this.clearForm) {
        // await this.setUserProfileData(undefined)
        // await this.setUserProfile(undefined)

        if (this.userProfileData) {
          user = this.userProfileData
        } else {
          user = { ...this.userProfile }
          user.email = this.userContact?.email
          user.phone = this.userContact?.phone
          user.phoneExtension = this.userContact?.phoneExtension
        }
      } else {
        user = this.userProfileData
      }
      this.firstName = user?.firstname || ''
      this.lastName = user?.lastname || ''
      this.emailAddress = user?.email || ''
      this.emailAddress = this.confirmedEmailAddress = user?.email || ''
      this.phoneNumber = user?.phone || ''
      this.extension = user?.phoneExtension || ''

      if (this.userContact) {
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
        if (this.isBCEIDUser) {
          await this.updateUserFirstAndLastName(user)
        }
        await this.saveOrUpdateContact(contact)
        await this.getUserProfile('@me')
        // If a token was provided, that means we are in the accept invitation flow for users and account coordinators
        // Incase if it is accept invitation flow for account admin emit event for parent to let know user profile process is done
        if (this.isAffidavitUpload) {
          this.$emit('emit-admin-profile-complete')
          return
        }
        // so redirect to /confirmtoken
        if (this.token) {
          this.$router.push('/confirmtoken/' + this.token)
          return
        }
        this.redirectToNext()
      }
    }

    private next () {
      const userProfile = {
        firstname: this.firstName.trim(),
        lastname: this.lastName.trim(),
        email: this.emailAddress.toLowerCase(),
        phone: this.phoneNumber,
        phoneExtension: this.extension
      }
      this.setUserProfileData(userProfile)

      // if payment method selector ld flag is enabled, the navigate to next step, otherwise emit & create account
      if (this.enablePaymentMethodSelectorStep) {
        this.stepForward()
      } else {
        this.createAccount()
      }
    }

    @Emit('final-step-action')
    private createAccount () {
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
        this.navigateBack()
      }
    }

    private navigateBack (): void {
      if (this.currentOrganization) {
        this.$router.push(`/account/${this.currentOrganization.id}`)
      } else {
        this.$router.push('/home')
      }
    }

    private goBack () {
      if (this.isAffidavitUpload) {
        // emit event to let parent know about the previous step request
        this.$emit('emit-admin-profile-previous-step')
      } else {
        this.stepBack(this.currentOrganization!.orgType === this.ACCOUNT_TYPE.PREMIUM)
      }
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
