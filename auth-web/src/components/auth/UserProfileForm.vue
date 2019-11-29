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
      <v-col cols="12" md="6" class="pt-0 pb-0">
        <v-text-field
                filled
                label="First Name"
                req
                persistent-hint
                disabled
                v-model="firstName"
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
        >
        </v-text-field>
      </v-col>
      <v-col cols="12" md="3" class="pt-0 pb-0">
        <v-text-field
                filled label="Extension"
                persistent-hint
                :rules="extensionRules"
                v-mask="'###'"
                v-model="extension"
        >
        </v-text-field>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" class="pt-0 pb-0">
        <terms-of-use-dialog :lastAcceptedVersion="lastAcceptedVersion"
                             @termsupdated="updateTerms"></terms-of-use-dialog>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" class="form__btns pt-5">
        <v-dialog max-width="640" v-model="deactivateProfileDialog" style="display: none;">
          <template v-slot:activator="{ on }">
            <v-btn large text color="primary" v-on="on" class="deactivate-btn">Deactivate my profile</v-btn>
          </template>
          <v-card>
            <v-card-title>
              Deactivate your profile
            </v-card-title>
            <v-card-text>
              <p class="pb-1">Deactivating your Cooperatives Online profile will remove your contact information, and your access to associated teams and/or affiliated businesses. <strong>This action cannot be undone.</strong></p>
              <v-row>
                <v-col cols="12" class="form__btns">
                  <v-btn large color="error" to="./profiledeactivated" :loading="isDeactivating">Deactivate</v-btn>
                  <!-- Show loading indicator while deactivation process is active -->
                  <!-- Show ModalDialog Error if process failed -->
                  <!-- Redirect to 'ProfileDeactivated' view once successful -->

                  <v-btn large depressed color="default" @click="deactivateProfileDialog = false">Cancel</v-btn>
                  <!-- User should be able to recover when clicking this button (if the deactivation process is delayed and it is visible still) -->

                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-dialog>
        <div>
          <v-btn large color="primary" class=".save-continue-button" :disabled='!isFormValid()' @click="save">
            Save
          </v-btn>
          <v-btn large depressed @click="cancel">Cancel</v-btn>
        </div>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Component, Mixins, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { Contact } from '@/models/contact'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import NextPageMixin from './NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import TermsOfUseDialog from '@/components/auth/TermsOfUseDialog.vue'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'
import { mask } from 'vue-the-mask'

@Component({
  components: {
    TermsOfUseDialog
  },
  directives: {
    mask
  },
  computed: {
    ...mapState('user', ['userProfile']),
    ...mapState('org', ['organizations'])
  },
  methods: {
    ...mapActions('user',
      [
        'createUserContact',
        'updateUserContact',
        'updateUserTerms',
        'getUserProfile'
      ]
    ),
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class UserProfileForm extends Mixins(NextPageMixin) {
    private userStore = getModule(UserModule, this.$store)
    private orgStore = getModule(OrgModule, this.$store)
    private readonly userProfile!: User
    private readonly organizations!: Organization[]
    private readonly createUserContact!: (contact: Contact) => Contact
    private readonly updateUserContact!: (contact: Contact) => Contact
    private readonly updateUserTerms!: () => User
    private readonly getUserProfile!: (identifer: string) => User
    private readonly syncOrganizations!: () => Organization[]
    private firstName = ''
    private lastName = ''
    private emailAddress = ''
    private confirmedEmailAddress = ''
    private phoneNumber = ''
    private extension = ''
    private formError = ''
    private editing = false
    private lastAcceptedVersion = ''
    private isTermsAccepted: boolean
    private deactivateProfileDialog = false
    private isDeactivating = false

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
      v => !v || (v.length >= 0 || v.length <= 3) || 'Extension is invalid'
    ]

    private emailMustMatch (): string {
      return (this.emailAddress === this.confirmedEmailAddress) ? '' : 'Email addresses must match'
    }

    private isFormValid (): boolean {
      return (!this.$refs || !this.$refs.form) ? false : (this.$refs.form as Vue & { validate: () => boolean }).validate() &&
        this.confirmedEmailAddress === this.emailAddress && this.isTermsAccepted
    }

    async mounted () {
      if (!this.userProfile) {
        await this.getUserProfile('@me')
      }

      if (!this.organizations || this.organizations.length < 1) {
        await this.syncOrganizations()
      }

      this.firstName = this.userProfile.firstname
      this.lastName = this.userProfile.lastname
      if (this.userProfile.contacts && this.userProfile.contacts[0]) {
        this.emailAddress = this.confirmedEmailAddress = this.userProfile.contacts[0].email
        this.phoneNumber = this.userProfile.contacts[0].phone
        this.extension = this.userProfile.contacts[0].phoneExtension
        this.editing = true
        if (this.userProfile.is_terms_of_use_accepted) {
          this.lastAcceptedVersion = this.userProfile.terms_of_use_version
        }
      }
    }

    updateTerms (event) {
      this.isTermsAccepted = event.istermsaccepted
      this.userStore.updateCurrentUserTerms({
        terms_of_use_accepted_version: event.termsversion,
        is_terms_of_use_accepted: event.istermsaccepted
      })
    }

    async save () {
      if (this.isFormValid()) {
        const contact = {
          email: this.emailAddress.toLowerCase(),
          phone: this.phoneNumber,
          phoneExtension: this.extension
        }
        if (!this.editing) {
          await Promise.all([
            await this.createUserContact(contact),
            await this.updateUserTerms()
          ])
        } else {
          await this.updateUserContact(contact)
        }
        await this.getUserProfile('@me')
        this.redirectToNext()
      }
    }

    private redirectToNext () {
      this.$router.push(this.getNextPageUrl(this.userProfile, this.organizations))
    }

    cancel () {
      window.history.back()
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
  }

  .deactivate-btn {
    margin-right: auto;
  }
</style>
