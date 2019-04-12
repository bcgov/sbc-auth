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
                <v-btn class="recovery-btn"
                  color="primary"
                  flat
                  large
                  @click="passCodeDialog = true"
                >Forgotten Your Passcode?
                </v-btn>
                -->
                <v-btn class="sign-in-btn" @click="login"
                       color="primary"
                       large
                >Sign in
                    <v-icon dark right>arrow_forward</v-icon>
                </v-btn>
            </div>
        </v-form>
        <v-dialog
                width="50rem"
                v-model="passCodeDialog">
            <v-card>
                <v-card-title>
                    Forgotten
                </v-card-title>
                <v-card-text>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore
                    et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
                    aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
                    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
                    culpa qui officia deserunt mollit anim id est laborum.
                </v-card-text>
            </v-card>
        </v-dialog>
    </div>
</template>

<script lang="ts">
  export default {
    name: "PasscodeForm",


    data: () => ({
      passCodeDialog: false, // Forgotten Password Dialog
      valid: false,
      entityNumRules: [
        (v) => !!v || "Incorporation Number is required",
        (v) => v.length <= 10 || "Passcode rules here..."
      ],
      entityPasscodeRules: [
        (v) => !!v || "Passcode is required",
        (v) => v.length <= 10 || "Passcode rules here..."
      ]
    }),


    computed: {
      entityNumber: {
        get() {
          return this.$store.state.entityNumber;
        },
        set(value) {
          this.$store.commit("entityNumber", value);
        }
      },
      passcode: {
        get() {
          return this.$store.state.passcode;
        },
        set(value) {
          this.$store.commit("passcode", value);
        }
      }


    },
    methods: {
      login: () => {
        if (this.$refs.form.validate()) {
          console.log("Login  called -Valid");
          return true;
        } else {
          console.log("Login  called -Invalid");
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
        overflow hidden

    .v-btn
        margin 0

        .recovery-btn
            float left

        .sign-in-btn
            float right

    @media (max-width 600px)
        .sign-in-btn
            width 100%

    @media (min-width 960px)
        .v-input
            max-width 25rem


</style>
