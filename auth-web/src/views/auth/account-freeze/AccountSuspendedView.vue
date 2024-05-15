<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        sm="6"
        class="text-center"
      >
        <v-icon
          size="40"
          data-test="icon-lock-suspend-account"
          color="error"
          class="mb-6"
        >
          mdi-alert-circle-outline
        </v-icon>
        <h1 data-test="header-account-suspend">
          Your Account is Suspended
        </h1>
        <div
          v-if="isAdmin"
          data-test="div-is-admin"
        >
          <p class="mt-8 mb-10">
            Your account is suspended. For more information, please contact the BC Online Partnership Office at:<br>
          </p>
          <p class="mt-1 mb-1">
            Email: <span class="text-underline">bconline@gov.bc.ca</span>
          </p>
          <p>Telephone: 1-800-663-6102</p>
        </div>
        <div
          v-else
          data-test="div-is-user"
        >
          <p class="mt-4">
            Your account is suspended from: <span class="font-weight-bold">May 10, 2024.</span>
          </p>
          <p class="mt-4">
            Please contact the account administrator to reactive your account.
          </p>
          <p class="mt-4 mb-10">
            Account Administrator Email: <a href="mailto:rodrigo.barraza@gov.bc.ca">rodrigo.barraza@gov.bc.ca</a>
          </p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class AccountSuspendedView extends Vue {
  @Prop({ default: false }) isAdmin: boolean
}
</script>
<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.text-underline {
    text-decoration: underline;
}
</style>
