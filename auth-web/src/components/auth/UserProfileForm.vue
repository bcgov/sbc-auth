<template>
  <v-form ref="form" lazy-validation>
    <v-expand-transition>
      <div class="form_alert-container" v-show="formError">
        <v-alert type="error" class="mb-0"
                 :value="true"
        >
          {{formError}}
        </v-alert>
      </div>
    </v-expand-transition>
    <!-- First / Last Name -->
    <v-row>
      {{editing}}
    </v-row>
    <v-row>
      <v-col cols="12" md="6" class="pt-0 pb-0">
        <v-text-field
                filled
                label="First Name"
                req
                persistent-hint
                disabled
                v-model="firstName"
                data-test="first-name"
        >
        </v-text-field>
      </v-col>
      <v-col cols="12" md="6" class="pt-0 pb-0">
        <v-text-field
                filled
                label="Last Name"
                req
                persistent-hint
                disabled
                v-model="lastName"
                data-test="last-name"
        >
        </v-text-field>
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

    <v-row>
      <v-col cols="12" class="form__btns pt-5">
        <v-btn large depressed color="default" class="deactivate-btn" v-show="editing" @click="$refs.deactivateUserConfirmationDialog.open()">Deactivate my profile</v-btn>
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
        <div>
          <v-btn large color="primary" class="save-continue-button" :disabled='!isFormValid()' @click="save" data-test="save-button">
            Save
          </v-btn>
          <v-btn large depressed @click="cancel" data-test="cancel-button" class="cancel-button">Cancel</v-btn>
        </div>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">

import { Account, Pages } from '@/util/constants'
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import { Contact } from '@/models/contact'
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
    ModalDialog
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
        'getUserProfile'
      ]),
    ...mapActions('org', ['createOrg', 'syncMembership', 'syncOrganization'])
  }
})
export default class UserProfileForm extends Mixins(NextPageMixin, Steppable) {
    private readonly createUserContact!: (contact: Contact) => Contact
    private readonly updateUserContact!: (contact: Contact) => Contact
    private readonly getUserProfile!: (identifer: string) => User
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

    $refs: {
      deactivateUserConfirmationDialog: ModalDialog,
      deactivateUserFailureDialog: ModalDialog,
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
      if (this.userContact) {
        this.emailAddress = this.confirmedEmailAddress = this.userContact.email
        this.phoneNumber = this.userContact.phone
        this.extension = this.userContact.phoneExtension
        this.editing = true
      }
    }

    private async save () {
      if (this.isFormValid()) {
        const contact = {
          email: this.emailAddress.toLowerCase(),
          phone: this.phoneNumber,
          phoneExtension: this.extension
        }
        if (this.stepForward) { // On stepper ;so Save the org
          const organization = await this.createOrg()
          if (this.editing) {
            await this.updateUserContact(contact)
          } else {
            await this.createUserContact(contact)
          }
          await this.getUserProfile('@me')
          await this.syncOrganization(organization.id)
          await this.syncMembership(organization.id)
          this.$store.commit('updateHeader')
          this.$router.push('/setup-account-success')
        } else {
          await this.updateUserContact(contact)
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

    private redirectToNext () {
      this.$router.push(this.getNextPageUrl())
    }

    private cancel () {
      if (!this.stepBack) {
        window.history.back()
      } else {
        this.stepBack()
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
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .form__btns {
    display: flex;
    justify-content: flex-end;

    .v-btn + .v-btn {
      margin-left: 0.5rem;
    }

    .deactivate-btn {
      margin-right: auto;
    }
  }
</style>
