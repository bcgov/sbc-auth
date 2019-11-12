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
          <h1 class="mb-5">Complete User Profile</h1>
          <p class="intro-text">It looks like we are missing some information to complete your user profile.</p>
        </div>
        <div v-if="editing">
          <h1 class="mb-5">Edit User Profile</h1>
          <p class="intro-text">Update and manage your contact information.</p>
        </div>
        <v-card class="profile-card">
          <v-container>
            <v-card-title>
              <h2>Your Profile</h2>
            </v-card-title>
            <v-card-text>
              <UserProfileForm/>
            </v-card-text>
          </v-container>
        </v-card>
      </article>
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
    if (this.userProfile.contacts && this.userProfile.contacts[0]) {
      this.editing = true
    }

    this.isLoading = false
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
  }

  .intro-text {
    margin-bottom: 3rem;
  }

  // Profile Card
  .profile-card .container {
    padding: 1rem;
  }
</style>
