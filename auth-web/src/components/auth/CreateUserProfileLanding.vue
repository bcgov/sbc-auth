<template>
  <v-container class="view-container">
    <template v-if="!inviteError">
      <!-- Loading status -->
      <v-fade-transition>
        <div
          v-if="isLoading"
          class="loading-container"
        >
          <v-progress-circular
            size="50"
            width="5"
            color="primary"
            :indeterminate="isLoading"
          />
        </div>
      </v-fade-transition>
      <div
        v-if="!isLoading"
        class="user-profile-container"
      >
        <v-row justify="center">
          <v-col
            lg="8"
            class="pt-0 pb-0"
          >
            <div class="view-header user-profile-header">
              <h1>Director Search Account Access</h1>
              <p class="mb-0">
                You've been invited to administer the {{ orgName }} Director Search Account at the BC Registry.
                Create your user profile and log in to access this account
              </p>
            </div>
            <v-card
              class="profile-card"
              flat
            >
              <v-container class="pa-6">
                <v-card-title class="mb-4">
                  Create your User Profile
                </v-card-title>
                <v-card-text>
                  <create-user-profile-form
                    :token="token"
                    @show-error-message="showErrorOccured"
                  />
                </v-card-text>
              </v-container>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </template>
    <div v-else>
      <interim-landing
        :summary="$t('errorOccurredTitle')"
        :description="$t('invitationProcessingErrorMsg')"
        icon="mdi-alert-circle-outline"
        iconColor="error"
      />
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import CreateUserProfileForm from '@/components/auth/CreateUserProfileForm.vue'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import Vue from 'vue'

@Component({
  components: {
    CreateUserProfileForm,
    InterimLanding
  }
})
export default class CreateUserProfileView extends Vue {
  private isLoading = true
  private inviteError = false

  @Prop() token: string
  @Prop({ default: '' }) orgName: string

  private async mounted () {
    this.isLoading = false
  }

  private showErrorOccured () {
    this.inviteError = true
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
