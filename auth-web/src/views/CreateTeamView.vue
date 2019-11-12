<template>
  <v-container>
    <div class="view-container">
      <article>
        <div>
          <h1>Create Team</h1>
          <p>Create your Cooperatives Online Team</p>
        </div>
        <v-card class="profile-card">
          <TeamForm />
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
  // Layout
  article {
    flex: 1 1 auto;
  }

  @media (min-width: 960px) {
    article {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }

    .view-container {
      flex-flow: row nowrap;
    }
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
