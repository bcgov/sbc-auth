<template>
  <v-container>
    <div class="view-container">
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
              Create a Director Search Account
            </h1>
            <p class="mb-0">
              Enter the name and contact information for this account, and indicate which products
              this account will have access to.
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
              <SetupAccountForm />
            </v-card-text>
          </v-container>
        </v-card>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import SetupAccountForm from '@/components/auth/staff/SetupAccountForm.vue'

@Component({
  components: {
    SetupAccountForm
  }
})
export default class SetupAccountView extends Vue {
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
