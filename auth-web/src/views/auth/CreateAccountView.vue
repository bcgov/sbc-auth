<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1 class="mb-5">Create a New Account</h1>
        <p class="intro-text">Tell us about this new account, and enter an account name.</p>
        <v-card class="profile-card">
          <v-container>
            <v-card-title class="mb-3">Account Information</v-card-title>
            <v-card-text>
              <CreateAccountInfoForm />
            </v-card-text>
          </v-container>
        </v-card>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import CreateAccountInfoForm from '@/components/auth/CreateAccount/CreateAccountInfoForm.vue'
import { Organization } from '@/models/Organization'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    CreateAccountInfoForm
  }
})
export default class CreateAccountView extends Vue { }
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
