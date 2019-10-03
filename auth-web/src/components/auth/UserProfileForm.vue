<template>
  <v-form ref="form" lazy-validation>
    <v-expand-transition>
      <div class="form_alert-container" v-show="formError">
        <v-alert
          :value="true"
          color="error"
          icon="warning"
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
      <v-col cols="12" class="form__btns pb-0">
        <v-btn large color="primary" class=".save-continue-button" :disabled='!isFormValid()' @click="save">
          Next
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import UserModule from '../../store/modules/user'
import configHelper from '../../util/config-helper'
import { mask } from 'vue-the-mask'
import { User } from '../../models/user'

@Component({
  directives: {
    mask
  }
})
export default class UserProfileForm extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private firstName = ''
  private lastName = ''
  private emailAddress = ''
  private confirmedEmailAddress = ''
  private phoneNumber = ''
  private extension = ''
  private formError = ''

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
      this.confirmedEmailAddress === this.emailAddress
  }

  mounted () {
    this.userStore.getUserProfile('@me').then((userProfile:User) => {
      this.firstName = userProfile.firstname
      this.lastName = userProfile.lastname
      if (userProfile.contacts && userProfile.contacts[0]) {
        this.emailAddress = this.confirmedEmailAddress = userProfile.contacts[0].email
        this.phoneNumber = userProfile.contacts[0].phone
        this.extension = userProfile.contacts[0].phoneExtension
      }
    })
  }

  save () {
    if (this.isFormValid()) {
      this.userStore.createUserContact({
        email: this.emailAddress.toLowerCase(),
        phone: this.phoneNumber,
        phoneExtension: this.extension
      }).then((contact) => {
        this.$router.push('/main')
      })
    }
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';

  [class^="col"] {
    padding-top: 0;
    padding-bottom: 0;
  }

  .form__btns {
    display: flex;
    justify-content: flex-end;
  }

</style>
