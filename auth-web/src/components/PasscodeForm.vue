<template>
  <div>
    <v-form class="passcode-form" ref="form">
      <div class="passcode-form__row">
        <v-text-field
          box
          label="Enter your Incorporation Number"
          hint="Example: 123456789" req
          persistent-hint
          :rules="entityNumRules"
          v-model="entityNumber"
        ></v-text-field>
      </div>
      <div class="passcode-form__row">
        <v-text-field
          box
          label="Enter your Passcode"
          hint="Example: 123456789"
          persistent-hint
          :rules="entityPasscodeRules"
          v-model="passcode"
        ></v-text-field>
      </div>
      <div class="passcode-form__form-btns">
        <!--
        <a href="#">Forgot your Passcode?</a>
        -->
        <v-btn @click="login" class="signinbtn"
          color="primary"
          depressed
          large
        >Sign in
          <v-icon dark right>arrow_forward</v-icon>
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script lang="ts">
  export default {
    name: 'PasscodeForm',


    data: () => ({
      valid: false,
      entityNumRules: [
        (v) => !!v || 'Incorporation Number is required',
        (v) => v.length <= 10 || 'Passcode rules here...'
      ],
      entityPasscodeRules: [
        (v) => !!v || 'Passcode is required',
        (v) => v.length <= 10 || 'Passcode rules here...'
      ]
    }),


    computed: {
      entityNumber: {
        get() {
          return this.$store.state.entityNumber;
        },
        set(value) {
          this.$store.commit('entityNumber', value);
        }
      },
      passcode: {
        get() {
          return this.$store.state.passcode;
        },
        set(value) {
          this.$store.commit('passcode', value);
        }
      }


    },
    methods: {
      login: () => {
        if (this.$refs.form.validate()) {
          console.log('Login  called -Valid');
          return true;
        } else {
          console.log('Login  called -Invalid');
          return false;
        }
      }


    }

  };
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  .passcode-form__row
    margin-top 1rem

  .passcode-form__form-btns
    margin-top 2rem
    text-align right

    .forgotten-link
      flex 1 1 auto

  .v-btn
    margin 0

  .v-input
    max-width 25rem

</style>
