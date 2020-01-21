<template>
  <v-container class="view-container">

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <div class="view-header">
      <v-btn large icon color="secondary" class="back-btn mr-3" to="/main" data-test="account-settings-back-button">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <div>
        <h1 class="view-header__title" data-test="account-settings-title">Account Settings</h1>
        <p class="mb-0">Manage account information and users of this account</p>
      </div>
    </div>
    <v-card flat class="account-settings-card" data-test="account-settings-card">
      <v-container class="nav-container">
        <v-navigation-drawer floating permanent data-test="account-nav-drawer">
          <v-list dense>
            <v-list-item-group color="primary">
              <v-list-item to="/account-settings/account-info" data-test="account-info-nav-item">
                <v-list-item-icon>
                  <v-icon left>mdi-information-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Account Info</v-list-item-title>
              </v-list-item>
              <v-list-item to="/account-settings/team-members" data-test="team-members-nav-item">
                <v-list-item-icon>
                  <v-icon left>mdi-account-group-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Team Members</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-navigation-drawer>
      </v-container>
      <v-container class="account-settings__content">
        <transition name="fade" mode="out-in">
          <router-view></router-view>
        </transition>
      </v-container>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import AccountInfo from '@/components/auth/AccountInfo.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { Role } from '@/util/constants'
import { UserInfo } from '@/models/userInfo'
import UserManagement from '@/components/auth/UserManagement.vue'

@Component({
  components: {
    AccountInfo,
    UserManagement
  }
})
export default class AccountSettings extends Vue {
  private isLoading = true

  private mounted () {
    this.isLoading = false
  }

  private goToAccountInfo () {
    this.$router.push('/account-settings/account-info')
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

  .account-settings-card {
    display: flex;
  }

  .nav-container {
    flex: 0 0 auto;
    width: 16rem;
    border-right: 1px solid $gray3;
  }

  .v-list--dense .v-list-item .v-list-item__title {
    font-weight: 700;
  }

  .account-settings__content {
    ::v-deep {
      .view-header {
        margin-bottom: 1.75rem;
      }

      h2 {
        font-size: 1.5rem;
      }
    }
  }

  .fade-enter-active,
  .fade-leave-active {
    transition-duration: 0.3s;
    transition-property: opacity;
    transition-timing-function: ease;
  }

  .fade-enter,
  .fade-leave-active {
    opacity: 0
  }

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    z-index: 2;
    background: $gray2;
  }
</style>
