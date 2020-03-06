<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1 class="mb-3">Create a Director Search Account</h1>
        <p class="intro-text pb-3">Enter the name and contact information for this account, and indicate which products
this account will have access to.</p>
        <v-card class="profile-card py-4 px-6">
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
export default class SetupAccountView extends Vue { }
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
