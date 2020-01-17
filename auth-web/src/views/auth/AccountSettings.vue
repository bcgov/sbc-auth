<template>
  <v-container class="view-container">

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <div class="view-header">
      <v-btn large icon color="primary" class="back-btn mr-3" to="/main">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <div>
        <h1 class="view-header__title">Account Settings</h1>
        <p class="mb-0">Manage account information and users of this account</p>
      </div>
    </div>
    <v-card flat class="account-settings-card">
      <v-container class="nav-container">
        <v-navigation-drawer floating permanent>
          <v-list dense>
            <v-list-item-group color="primary">
              <v-list-item @click="accountInfo">
                <v-list-item-icon>
                  <v-icon left>mdi-information-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Account Info</v-list-item-title>
              </v-list-item>
              <v-list-item @click="teamMembers">
                <v-list-item-icon>
                  <v-icon left>mdi-account-group-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Team Members</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-navigation-drawer>
        <!-- Tab Contents
        <v-tabs vertical hide-slider mobile-break-point="900" v-model="tab" background-color="transparent">
          <v-tab><v-icon left>mdi-information-outline</v-icon>Account Info</v-tab>
          <v-tab><v-icon left>mdi-account-multiple-outline</v-icon>Team Members</v-tab>
        </v-tabs>
        -->
      </v-container>
      <v-container>
        <transition name="fade" mode="out-in">
          <router-view></router-view>
        </transition>
      </v-container>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
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
  readonly currentUser!: UserInfo
  errorMessage : string = ''
  isStaff: boolean = false

  private teamName: string = ''
  private teamType: string = 'BASIC'

  accountInfo () {
    this.$router.push('/account-settings/account-info')
  }

  teamMembers () {
    this.$router.push('/account-settings/team-members')
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

  ::v-deep {
    h2 {
      padding-bottom: 1.5rem;
      font-size: 1.5rem;
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
