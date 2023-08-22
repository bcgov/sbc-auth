<template>
  <v-container class="view-container">
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
          <div
            v-if="!editing"
            class="view-header user-profile-header"
          >
            <h1>Complete Profile</h1>
            <p class="mb-0">
              Enter your contact information to complete your profile.
            </p>
          </div>
          <div
            v-if="editing"
            class="view-header"
          >
            <v-btn
              large
              icon
              color="secondary"
              class="back-btn mr-3"
              @click="navigateBack()"
            >
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <div>
              <h1 class="view-header__title">
                Edit Profile
              </h1>
              <p class="mt-3 mb-0">
                Edit your profile contact information
              </p>
            </div>
          </div>
          <v-card
            flat
            class="profile-card"
          >
            <v-container>
              <v-card-text>
                <UserProfileForm :token="token" />
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
import ConfigHelper from '@/util/config-helper'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import { User } from '@/models/user'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'
import { mapState } from 'pinia'
import { useUserStore } from '@/store/user'

@Component({
  components: {
    UserProfileForm,
    SupportInfoCard
  },
  computed: {
    ...mapState(useUserStore, ['userContact'])
  }
})
export default class UserProfileView extends Mixins(NextPageMixin) {
  private readonly getUserProfile!: (identifier: string) => User
  @Prop() token: string
  private editing = false
  private isLoading = true

  private navigateBack (): void {
    if (this.currentOrganization) {
      window.location.assign(ConfigHelper.getBcrosDashboardURL())
    } else {
      this.$router.push('/home')
    }
  }

  private async mounted () {
    if (this.userContact) {
      this.editing = true
    }

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
