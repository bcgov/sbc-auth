<template>
  <v-container>
    <!-- Loading status -->
    <v-progress-circular
      :indeterminate=true
      v-if="isLoading"
    />
    <div v-if="!isLoading" class="view-container">
      <article>
        <div v-if="!editing">
          <h1>Complete User Profile</h1>
          <p class="intro-text">It looks like we are missing some information to complete your user profile.</p>
        </div>
        <div v-if="editing">
          <h1>Edit User Profile</h1>
          <p class="intro-text">Update and manage your contact information</p>
        </div>
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
import { mapActions, mapState } from 'vuex'
import { Component } from 'vue-property-decorator'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import UserProfileForm from '@/components/auth/UserProfileForm.vue'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    UserProfileForm,
    SupportInfoCard
  },
  methods: {
    ...mapActions('user', ['getUserProfile'])
  },
  computed: {
    ...mapState('user', ['userProfile'])
  }
})
export default class UserProfile extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private readonly userProfile!: User
  private readonly getUserProfile!: (identifier: string) => User
  private editing = false
  private isLoading = true

  async mounted () {
    if (!this.userProfile) {
      await this.getUserProfile('@me')
    }

    if (this.userProfile.contacts && this.userProfile.contacts[0]) {
      this.editing = true
    }

    this.isLoading = false
  }
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
