<template>
  <v-card>
    <v-card-title>Create a BC Registries Account</v-card-title>
    <v-card-text>
      <p class="mb-7">To access this service, you must securely log in with your BC Services Card, government’s trusted way to access online services. It typically takes five minutes or less to set up your mobile card, and the only information BC Registries can access from your card is your legal name.</p>
      <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/login-with-card" rel="noopener noreferrer"
        target="_blank">
        <v-icon small class="mr-2">mdi-open-in-new</v-icon>
        <span>Learn how to set up and use your BC Services Card</span>
      </a>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <slot name="actions">
        <v-btn large color="primary" @click="login()">Log in</v-btn>
      </slot>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
@Component({
  name: 'LoginBCSC'
})
export default class LoginBCSC extends Vue {
  private login () {
    this.$router.push('/signin/bcsc/createaccount')
  }
}
</script>

<style lang="scss" scoped>
</style>
