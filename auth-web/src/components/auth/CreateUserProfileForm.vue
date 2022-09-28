<template>
  <div>
    <v-form ref="form" lazy-validation>
      <!-- Username -->
      <v-row>
        <v-col cols="12" class="py-0 mb-4">
          <v-text-field
              filled
              label="Username"
              req
              persistent-hint
              :hint="inputHints.username"
              :rules="usernameRules"
              v-model.trim="username"
              data-test="username"
              :disabled="isLoading"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <!-- Password -->
      <v-row>
        <v-col cols="12" class="py-0 mb-4">
          <v-text-field
              filled
              label="Password"
              req
              persistent-hint
              :hint="inputHints.password"
              :rules="passwordRules"
              v-model="password"
              data-test="password"
              type="password"
              :disabled="isLoading"
              :append-icon="(password && !passwordRuleValid) ? 'mdi-alert-circle-outline' : '' "
          >
          </v-text-field>
          <div
            class="pl-1 my-1 password-error"
            v-bind:class="{ 'error--text': password && !passwordRuleValid }"
          >
            <ul>
              <li>include at least one uppercase character (A-Z)</li>
              <li>include at least one lowercase character (a-z)</li>
              <li>include at least one number (0-9)</li>
              <li>include at least one special character (examples: !, @, #, $)</li>
            </ul>
          </div>
        </v-col>
      </v-row>
      <!-- Confirm Password -->
      <v-row>
        <v-col cols="12" class="pt-0 pb-0">
          <v-text-field
              filled
              label="Confirm Password"
              req
              persistent-hint
              :hint="inputHints.confirmPassword"
              :error-messages="passwordMustMatch()"
              v-model="confirmPassword"
              data-test="confirm-password"
              type="password"
              :disabled="isLoading"
          >
          </v-text-field>
        </v-col>
      </v-row>

      <v-row>
        <v-col cols="12" class="form__btns pt-5">
            <v-btn
              large
              color="primary"
              class="save-continue-button"
              :loading="isLoading"
              :disabled='!isFormValid() || isLoading'
              @click="nextStep"
              data-test="next-button"
            > Next
            </v-btn>
            <v-btn
              large
              depressed
              @click="cancel"
              data-test="cancel-button"
              class="cancel-button"
            > Cancel
            </v-btn>
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
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import { Organization } from '@/models/Organization'
import { UserProfileRequestBody } from '@/models/user'
import UserService from '@/services/user.services'

@Component({
  components: {
    ModalDialog
  }
})
export default class CreateUserProfileForm extends Mixins(NextPageMixin) {
    private username = ''
    private password = ''
    private confirmPassword = ''
    private isLoading = false
    private dialogTitle = ''
    private dialogText = ''
    private passwordRuleValid = false

    private inputHints = {
      username: 'Minimum 8 characters',
      password: `Minimum of 8 characters and includes the following:`,
      confirmPassword: 'Minimum of 8 characters'
    }

    @Prop() token: string

    $refs: {
      form: HTMLFormElement,
      errorDialog: ModalDialog
    }

    private usernameRules = [
      v => !!v?.trim() || 'Username is required',
      v => (v.trim().length >= 8) || this.inputHints.username
    ]

    private passwordRules = [
      value => !!value || 'Password is required',
      value => this.validatePassword(value) || this.inputHints.password
    ]

    private passwordMustMatch (): string {
      return (this.password === this.confirmPassword) ? '' : 'Passwords must match'
    }

    private isFormValid (): boolean {
      return this.$refs.form &&
        this.$refs.form.validate() &&
        !this.passwordMustMatch()
    }

    private async mounted () {
    }

    private async nextStep () {
      if (this.isFormValid()) {
        this.isLoading = true
        const requestBody: UserProfileRequestBody = {
          username: this.username.trim().toLowerCase(),
          password: this.password
        }
        try {
          const response = await UserService.createUserProfile(this.token, requestBody)
          if (response?.data?.users?.length) {
            this.redirectToSignin()
          }
        } catch (error) {
          this.isLoading = false
          // TODO: Handle cases according to the type of the error
          if (error?.response?.data?.code) {
            switch (error.response.data.code) {
              case 'FAILED_ADDING_USER_IN_KEYCLOAK':
                this.showErrorModal('Failed to add the user, please try again')
                break
              case 409:
                this.showErrorModal('The username has already been taken.Please try another user name.')
                break
              default: this.showErrorModal()
            }
          } else {
            this.$emit('show-error-message')
          }
        }
      }
    }

    private redirectToSignin () {
      let redirectUrl = ConfigHelper.getSelfURL() + '/confirmtoken/' + this.token
      this.$router.push('/signin/bcros/' + encodeURIComponent(redirectUrl))
    }

    private cancel () {
      this.$router.push('/signin/bcros/')
    }

    private validatePassword (value) {
      this.passwordRuleValid = CommonUtils.validatePasswordRules(value)
      return this.passwordRuleValid
    }

    close () {
      this.$refs.errorDialog.close()
    }

    showErrorModal (msg?) {
      this.dialogTitle = 'An error has occured'
      this.dialogText = msg || 'Something went wrong while attempting to create this profile. Please try again later.'
      this.$refs.errorDialog.open()
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

  .password-error {
    color: rgba(0,0,0,.6);
    font-size: 12px;
    min-height: 14px;
    min-width: 1px;
    position: relative;
  }
</style>
