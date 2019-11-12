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
      <v-col cols="12" md="6">
        <v-text-field
                filled
                label="First Name"
                req
                persistent-hint
                readonly
                v-model="firstName"
        >
        </v-text-field>
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field
                filled
                label="Last Name"
                req
                persistent-hint
                readonly
                v-model="lastName"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <!-- Email Address -->
    <v-row>
      <v-col cols="12">
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
      <v-col cols="12">
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
      <v-col cols="12" md="6">
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
      <v-col cols="12" md="3">
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
      <v-col cols="12">
        <terms-of-use-dialog :lastAcceptedVersion="lastAcceptedVersion" @termsupdated="updateTerms"></terms-of-use-dialog>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" class="form__btns pb-0">
        <v-btn large color="primary" class=".save-continue-button" :disabled='!isFormValid()' @click="save">
          Save
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { Contact } from '@/models/contact'
import { Organization } from '@/models/Organization'
import TermsOfUseDialog from '@/components/auth/TermsOfUseDialog.vue'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'
import { mask } from 'vue-the-mask'

  @Component({
    components: { TermsOfUseDialog },
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
export default class UserProfileForm extends Vue {
    private userStore = getModule(UserModule, this.$store)
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

      if (!this.organizations) {
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
      this.userStore.updateCurrentUserTerms({ terms_of_use_accepted_version: event.termsversion, is_terms_of_use_accepted: event.istermsaccepted })
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
        this.$router.push('/main')
      }
    }

    private redirectToNext () {
      // If this user is not a member of a team, redirect to Create Team view
      if (!this.organizations || this.organizations.length === 0) {
        this.$router.push({ path: '/createteam' })
      } else { // If a member of a team, redirect to dashboard for that team
        this.$router.push({ path: '/main' })
      }
    }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  // Tighten up some of the spacing between rows
  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }
</style>
