<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1 class="mb-5">Already On a Team</h1>
        <p class="intro-text">You cannot accept this invitation, because you already have membership on a team</p>
        <v-card class="profile-card">
          <v-container>
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
import CreateAccountInfoForm from '@/components/auth/create-account/CreateAccountInfoForm.vue'
import { Component, Vue } from 'vue-property-decorator'

@Component({
  components: {
    CreateAccountInfoForm
  }
})
export default class DuplicateTeamWarningView extends Vue { }
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
