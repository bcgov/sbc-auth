<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1>Create Account</h1>
        <v-card class="profile-card">
          <v-container>
            <h2 class="mb-7">Enter User Profile</h2>
            <UserProfileForm/>
          </v-container>
        </v-card>
      </article>
      <aside>
        <SupportInfoCard/>
      </aside>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    UserProfileForm,
    SupportInfoCard
  }
})
export default class UserProfile extends Vue {

}
</script>

<style lang="scss" scoped>
  // Layout
  article {
    flex: 1 1 auto;
  }

  aside {
    flex: 0 0 auto;
    margin-top: 2rem;
  }

  @media (min-width: 960px) {
    article {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }

    aside {
      margin-top: 0;
      margin-left: 2rem;
      width: 20rem;
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
