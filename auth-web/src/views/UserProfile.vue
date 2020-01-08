<template>
  <v-container>

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <div class="user-profile-container" v-if="!isLoading">
      <article>
        <v-row justify="center">
          <v-col lg="8" class="pt-0 pb-0">
            <div v-if="!editing">
              <h1 class="mb-4">Complete Profile</h1>
              <p class="intro-text">Enter your contact information to complete your profile.</p>
            </div>
            <div v-if="editing">
              <h1 class="mb-4">Edit Profile</h1>
              <p class="intro-text">Edit your profile contact information</p>
            </div>
            <v-card class="profile-card">
              <v-container>
                <v-card-title class="mb-4">
                  {{ userProfile.firstname }} {{ userProfile.lastname}}
                </v-card-title>
                <v-card-text>
                  <UserProfileForm/>
                </v-card-text>
              </v-container>
            </v-card>
          </v-col>
        </v-row>
      </article>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { Contact } from '@/models/contact'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
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
    ...mapState('user', ['userContact'])
  }
})
export default class UserProfile extends Mixins(NextPageMixin) {
  private userStore = getModule(UserModule, this.$store)
  private readonly getUserProfile!: (identifier: string) => User
  private editing = false
  private isLoading = true

  async mounted () {
    if (this.userContact) {
      this.editing = true
    }

    this.isLoading = false
  }
}
</script>

<style lang="scss" scoped>
   @import '$assets/scss/theme.scss';

  .view-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
  }

  .v-card__title {
    font-weight: 700;
    letter-spacing: -0.02rem;
  }

  .profile-card {
    margin-top: 3rem;
  }

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 2;
    background: $gray2;
  }
</style>
