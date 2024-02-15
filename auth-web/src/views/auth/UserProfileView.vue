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
import { defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { useOrgStore, useUserStore } from '@/stores'
import ConfigHelper from '@/util/config-helper'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import UserProfileForm from '@/components/auth/create-account/UserProfileForm.vue'

export default defineComponent({
  name: 'UserProfileView',
  components: {
    UserProfileForm
  },
  mixins: [NextPageMixin],
  props: {
    token: {
      type: String,
      required: true
    }
  },
  setup (props, { root }) {
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    const state = reactive({
      editing: false,
      loading: true
    })

    function navigateBack () {
      if (orgStore.currentOrganization) {
        window.location.assign(ConfigHelper.getBcrosDashboardURL())
      } else {
        root.$router.push('/home')
      }
    }

    onMounted(() => {
      if (userStore.userContact) {
        state.editing = true
      }

      state.loading = false
    })

    return {
      ...toRefs(state),
      navigateBack
    }
  }
})
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
