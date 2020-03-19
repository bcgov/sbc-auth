<template>
  <v-container class="view-container">

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>
    <div class="user-profile-container" v-if="!isLoading">
      <v-row justify="center">
        <v-col lg="8" class="pt-0 pb-0">
          <div class="view-header user-profile-header">
            <h1>Director Search Account Access</h1>
            <p class="mb-0">You've been invited to administer the '@@replace@@' Director Search Account at the BC Registry. Create your user profile and log in to access this account</p>
          </div>
          <v-card class="profile-card" flat>
            <v-container class="pa-6">
              <v-card-title class="mb-4">
                Create your User Profile
              </v-card-title>
              <v-card-text>
                <create-user-profile-form
                  :token="token"
                ></create-user-profile-form>
              </v-card-text>
            </v-container>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import CreateUserProfileForm from '@/components/auth/CreateUserProfileForm.vue'
import Vue from 'vue'

@Component({
  components: {
    CreateUserProfileForm
  }
})
export default class CreateUserProfileView extends Vue {
  private isLoading = true

  @Prop() token: string

  private async mounted () {
    this.isLoading = false
  }
}
</script>

<style lang="scss" scoped>
   @import '$assets/scss/theme.scss';

  .v-card__title {
    font-weight: 700;
    letter-spacing: -0.02rem;
  }

  .user-profile-header {
    flex-direction: column;
  }
</style>
