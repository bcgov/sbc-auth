<template>
  <v-container>
    <div
      class="view-container"
      data-test="setup-govm-account"
    >
      <article>
        <div class="view-header">
          <v-btn
            large
            icon
            color="secondary"
            class="mr-2"
            data-test="account-settings-back-button"
            @click="handleBackButton()"
          >
            <v-icon class="font-weight-bold">
              mdi-arrow-left
            </v-icon>
          </v-btn>
          <div>
            <h1 class="view-header__title">
              Send Invite to Ministry Account
            </h1>
            <p class="mb-0">
              Enter the ministry name and account admin contact for this account.
              An email invite will be sent to the account admin's email containing instructions
              how to create their account.
            </p>
          </div>
        </div>
        <v-card
          class="profile-card py-4 px-6"
          flat
        >
          <v-container>
            <v-card-title>Account Details</v-card-title>
            <v-card-text>
              <SetupGovmAccountForm />
            </v-card-text>
          </v-container>
        </v-card>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import SetupGovmAccountForm from '@/components/auth/staff/SetupGovmAccountForm.vue'

@Component({
  components: {
    SetupGovmAccountForm
  }
})
export default class SetupGovmAccountView extends Vue {
  handleBackButton () {
    this.$router.go(-1)
  }
}
</script>

<style lang="scss" scoped>
  article {
    flex: 1 1 auto;
    margin: 0 auto;
    max-width: 50rem;
  }
  .v-card__title {
    font-weight: 700;
    letter-spacing: -0.01rem;
    font-size: 1.4rem;
  }
</style>
