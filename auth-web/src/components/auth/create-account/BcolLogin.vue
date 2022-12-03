<template>
  <v-form ref="form" lazy-validation  data-test="form-bcol-login">
    <fieldset>
      <legend class="mb-3">
        BC Online Prime Contact Details
        <v-tooltip bottom color="grey darken-4">
          <template v-slot:activator="{ on }">
            <v-icon color="grey darken-4" v-on="on" tabindex="0">mdi-help-circle-outline</v-icon>
          </template>
          <div class="bcol-tooltip__msg py-2">BC Online Prime Contacts are users who have authority to manage account settings for a BC Online Account.</div>
        </v-tooltip>
      </legend>
      <v-slide-y-transition>
        <div class="pb-2" v-show="errorMessage">
          <v-alert type="error" icon="mdi-alert-circle-outline" data-test="alert-bcol-error">
            {{errorMessage}}
          </v-alert>
        </div>
      </v-slide-y-transition>
      <v-row>
        <v-col :cols="hideLinkBtn ? 6 : 4 " class="py-0 pr-0">
          <v-text-field
            dense
            filled
            label="User ID"
            v-model.trim="username"
            :rules="usernameRules"
            req
            data-test="input-user-id"
          >
          </v-text-field>
        </v-col>
        <v-col :cols="hideLinkBtn?6:4" class="py-0 pr-0">
          <v-text-field
            dense
            filled
            label="Password"
            type="password"
            v-model.trim="password"
            req
            :rules="passwordRules"
            data-test="input-user-password"
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0" v-if="!hideLinkBtn">
          <v-btn
            large
            depressed
            color="primary"
            class="link-account-btn"
            @click="linkAccounts()"
            data-test="dialog-save-button"
            :loading="isLoading"
            :disabled='!isFormValid() || isLoading'
          >
            Link Account
          </v-btn>
        </v-col>
      </v-row>
    </fieldset>
  </v-form>
</template>

<script lang="ts">
import { BcolAccountDetails, BcolProfile } from '@/models/bcol'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component({
  name: 'BcolLogin'
})
export default class BcolLogin extends Vue {
  private username: string = ''
  private password: string = ''
  private errorMessage: string = ''
  private isLoading: boolean = false
  @Prop({ default: false }) hideLinkBtn: boolean
  @OrgModule.Action('validateBcolAccount')
  private readonly validateBcolAccount!: (bcolProfile: BcolProfile) => Promise<BcolAccountDetails>

  private async mounted () {
    this.password = ''
  }

  @Watch('password')
  onPasswordChange () {
    this.emitBcolInfo()
  }

  @Watch('username')
  onUsernameChange () {
    this.emitBcolInfo()
  }

  private isFormValid (): boolean {
    return !!this.username && !!this.password
  }
  private usernameRules = [
    v => !!v || 'Username is required'
  ]

  private passwordRules = [
    value => !!value || 'Password is required',
    value => (value?.trim().length <= 8) || 'Use only first 8 characters for password'
  ]

  $refs: {
    form: HTMLFormElement
  }

  private async linkAccounts () {
    this.isLoading = true
    this.errorMessage = ''
    // Validate form, and then create an team with this user a member
    if (this.isFormValid()) {
      const bcolProfile: BcolProfile = {
        userId: this.username,
        password: this.password
      }
      try {
        const bcolAccountDetails = await this.validateBcolAccount(bcolProfile)
        this.isLoading = false
        if (bcolAccountDetails) { // TODO whats the success status
          this.$emit('account-link-successful', { bcolProfile, bcolAccountDetails })
          this.resetForm()
        }
      } catch (err) {
        this.isLoading = false
        switch (err.response.status) {
          case 409:
            this.errorMessage = err.response.data.message
            break
          case 400:
            this.errorMessage = err.response.data.message
            break
          default:
            this.errorMessage = 'An error occurred while attempting to create your account.'
        }
      }
    }
  }
  resetForm () {
    this.password = this.errorMessage = ''
    this.$refs.form.resetValidation()
  }

  @Emit()
  private async emitBcolInfo () {
    const bcolInfo: BcolProfile = {
      userId: this.username,
      password: this.password
    }
    return bcolInfo
  }
}
</script>

<style lang="scss" scoped>
  .bcol-tooltip__msg {
    max-width: 20rem;
    line-height: 1.5;
    font-size: 0.9375rem;
  }

  .v-icon {
    margin-top: -2px;
    font-size: 1.25rem !important;
  }

  .v-btn.link-account-btn {
    font-size: 0.875rem !important;
    font-weight: 700;
  }

  .v-tooltip__content:before {
    content: ' ';
    position: absolute;
    top: -20px;
    left: 50%;
    margin-left: -10px;
    width: 20px;
    height: 20px;
    border-width: 10px 10px 10px 10px;
    border-style: solid;
    border-color: transparent transparent var(--v-grey-darken4) transparent;
  }
</style>
