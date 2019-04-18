<template>
  <div>
    <v-form class="passcode-form" ref="form" lazy-validation>
      <v-alert
        v-if="loginError"
        :value="true"
        color="error"
        icon="warning"
      >{{loginError}}</v-alert>
      <div class="passcode-form__row">
        <v-text-field
          box
          label="Enter your Incorporation Number"
          hint="Example: CP1234567"
          req
          persistent-hint
          :rules="entityNumRules"
          v-model="entityNumber"
        ></v-text-field>
      </div>
      <div class="passcode-form__row">
        <v-text-field
          :append-icon="show1 ? 'visibility' : 'visibility_off'"
          :type="show1 ? 'text' : 'password'"
          @click:append="show1 = !show1"
          box
          label="Enter your Passcode"
          hint="Passcode must be exactly 9 digits"
          persistent-hint
          :rules="entityPasscodeRules"
          :maxlength="9"
          v-model="passcode"
        ></v-text-field>
      </div>
        <div class="passcode-form__form-btns">
        <v-btn class="sign-in-btn" @click="login" color="primary" large>
          <v-progress-circular :indeterminate="true" size="20" width="2" v-if="showSpinner"></v-progress-circular>
          <span>{{showSpinner ? 'Signing in' : 'Sign in'}}</span>
          <v-icon dark right v-if="!showSpinner">arrow_forward</v-icon>
        </v-btn>
      </div>
    </v-form>
    <v-dialog width="50rem" v-model="passCodeDialog">
      <v-card>
        <v-card-title>Forgotten</v-card-title>
        <v-card-text>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import LoginServices from '@/services/login.services'

export default {
  name: 'PasscodeForm',

  data: () => ({
    show1: false,
    showSpinner: false,
    passCodeDialog: false, // Forgotten Password Dialog
    loginError: '',
    valid: false,
    entityNumRules: [
      v => !!v || 'Incorporation Number is required'
    ],
    entityPasscodeRules: [
      v => !!v || 'Passcode is required',
      v => v.length >= 9 || 'Passcode must be exactly 9 digits'
    ]
  }),

  computed: {
    entityNumber: {
      get () {
        return this.$store.state.entityNumber
      },
      set (value) {
        this.$store.commit('entityNumber', value)
      }
    },
    passcode: {
      get () {
        return this.$store.state.passcode;;
      },
      set (value) {
        this.$store.commit('passcode', value)
      }
    }
  },
  methods: {
    login () {
      if (this.$refs.form.validate()) {
        console.log('VUE_APP_ROOT_API:' + process.env.VUE_APP_ROOT_API)

        LoginServices.login(this.$store.state.entityNumber, this.$store.state.passcode)
          .then(response => {
            if (response.data.error) {
              this.loginError =
                'Login Failed. Invalid Incorporation Number or Passcode'
            } else if (response.data.access_token) {
              this.showSpinner = true
              setTimeout(() => {
                window.location.href = 'https://coops-dev.pathfinder.gov.bc.ca/'
              }, 500)
              localStorage.name = response.data.access_token
            }
          })
          .catch(response => {
            this.loginError = 'something went wrong'
          })
      }
    }
  }
}
</script>

<style lang="stylus" scoped>
@import '../assets/styl/theme.styl';

.passcode-form__row {
  margin-top: 1rem;
}

.passcode-form__form-btns {
  margin-top: 2rem;
  overflow: hidden;
}

.v-alert + .passcode-form__row
  margin-top 2.25rem

.v-btn {
  margin: 0;

  .recovery-btn {
    float: left;
  }

  .sign-in-btn {
    float: right;
  }
}

.v-progress-circular
  margin-right 1rem
  margin-left -0.5rem

@media (max-width: 600px) {
  .sign-in-btn {
    width: 100%;
  }
}

@media (min-width: 960px) {
  .v-input {
    max-width: 25rem;
  }
}
</style>
