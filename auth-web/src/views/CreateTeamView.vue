<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1 class="mb-5">Create Team</h1>
        <p class="intro-text">Create your Cooperatives Online Team.</p>
        <v-card class="profile-card">
          <v-container>
            <TeamForm />
          </v-container>
        </v-card>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { Organization } from '@/models/Organization'
import TeamForm from '@/components/auth/TeamForm.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    TeamForm
  }
})
export default class CreateTeamView extends Vue {
  async mounted () {}
}
</script>

<style lang="scss" scoped>
  article {
    flex: 1 1 auto;
    margin: 0 auto;
    max-width: 50rem;
  }

  .intro-text {
    margin-bottom: 3rem;
  }

  // Profile Card
  .profile-card .container {
    padding: 1.5rem;
  }

  @media (min-width: 960px) {
    .profile-card .container {
      padding: 2rem;
    }
  }
</style>
