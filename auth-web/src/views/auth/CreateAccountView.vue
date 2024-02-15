<template>
  <v-container>
    <div class="view-header flex-column">
      <h1 class="view-header__title mb-4">
        Create a New Account
      </h1>
      <p>Tell us about this new account, and enter an account name.</p>
    </div>
    <v-card class="profile-card">
      <v-container>
        <v-card-title class="mb-3">
          Account Information
        </v-card-title>
        <v-card-text>
          <CreateAccountInfoForm />
        </v-card-text>
      </v-container>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'CreateAccountView',
  components: {
    CreateAccountInfoForm
  }
})
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
  }

  .intro-text {
    margin-bottom: 3rem;
  }

  // Profile Card
  .profile-card .container {
    padding: 1rem;
  }
</style>
