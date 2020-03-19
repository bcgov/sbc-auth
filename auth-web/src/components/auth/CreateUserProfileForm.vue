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
    <!-- Username -->
    <v-row>
      <v-col cols="12" class="pt-0 pb-0">
        <v-text-field
            filled
            label="Username"
            req
            persistent-hint
            :rules="usernameRules"
            v-model="username"
            data-test="username"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <!-- Password -->
    <v-row>
      <v-col cols="12" class="pt-0 pb-0">
        <v-text-field
            filled
            label="Password"
            req
            persistent-hint
            :rules="passwordRules"
            v-model="password"
            data-test="password"
        >
        </v-text-field>
      </v-col>
    </v-row>
    <!-- Confirm Password -->
    <v-row>
      <v-col cols="12" class="pt-0 pb-0">
        <v-text-field
            filled
            label="Confirm Email Address"
            req
            persistent-hint
            :error-messages="passwordMustMatch()"
            v-model="confirmPassword"
            data-test="confirm-password"
        >
        </v-text-field>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" class="form__btns pt-5">
          <v-btn large color="primary" class="save-continue-button" :disabled='!isFormValid()' @click="nextStep" data-test="next-button">
            Next
          </v-btn>
          <v-btn large depressed @click="cancel" data-test="cancel-button" class="cancel-button">Cancel</v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
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
    private formError = ''
    private editing = false

    @Prop() token: string

    $refs: {
      form: HTMLFormElement
    }

    private usernameRules = [
      v => !!v || 'Username is required'
    ]

    private passwordRules = [
      v => !!v || 'Password is required'
    ]

    private passwordMustMatch (): string {
      return (this.password === this.confirmPassword) ? '' : 'Passwords must'
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
        const requestBody: UserProfileRequestBody = {
          username: this.username,
          password: this.password
        }
        const response = UserService.createUserProfile(this.token, requestBody)
        // eslint-disable-next-line no-console
        console.log(response)
        // this.redirectToNext()
      }
    }

    private redirectToNext () {
      this.$router.push(this.getNextPageUrl())
    }

    private cancel () {
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
</style>
