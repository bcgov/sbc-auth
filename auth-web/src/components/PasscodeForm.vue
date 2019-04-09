<template>
  <v-form class="passcode-form">
    <div class="mb-2">
      <v-text-field
        outline
        prepend-icon="work"
        label="Enter your Incorporation Number"
        hint="Example: 123456789"
        persistent-hint
        v-model="entityNum"
        :rules="entityNumRules"
      ></v-text-field>
    </div>
    <div>
      <v-text-field
        outline
        prepend-icon="lock"
        label="Enter your Passcode"
        hint="Example: 123456789"
        persistent-hint
        v-model="entityPasscode"
        :rules="entityPasscodeRules"
      ></v-text-field>
    </div>
    <div class="passcode-form__form-btns">
      <v-btn
        color="primary"
        large
        depressed
      >Continue to Filing
      <v-icon right dark>arrow_forward</v-icon>
      </v-btn>
    </div>
  </v-form>
</template>

<script>
export default {
  name: 'PasscodeForm',

  data: () => ({
    valid: false,
    entityNum: '',
    entityNumRules: [
      (v) => !!v || 'Incorporation Number is required',
      (v) => v.length <= 10 || 'Passcode rules here...'
    ],
    entityPasscode: '',
    entityPasscodeRules: [
      (v) => !!v || 'Passcode is required',
      (v) => v.length <= 10 || 'Passcode rules here...'
    ]
  })
};
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  .v-input
    max-width 25rem

  .passcode-form__form-btns
    text-align center

</style>