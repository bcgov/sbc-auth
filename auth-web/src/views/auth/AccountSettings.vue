<template>
  <v-container class="view-container">

    <!-- Loading status -->
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>

    <div class="view-header">
      <v-btn large icon color="secondary"
        class="back-btn mr-3"
        @click="handleBackButton()"
        v-if="!isDirSearchUser"
        data-test="account-settings-back-button">
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
              <v-list-item :to="accountInfoUrl" data-test="account-info-nav-item">
                <v-list-item-icon>
                  <v-icon left>mdi-information-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Account Info</v-list-item-title>
              </v-list-item>
              <v-list-item :to="teamMembersUrl" data-test="team-members-nav-item">
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
import { Component, Prop, Vue } from 'vue-property-decorator'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { LoginSource } from '@/util/constants'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('user', ['currentUser'])
  }
})
export default class AccountSettings extends Vue {
  @Prop({ default: '' }) private orgId: string

  private readonly currentUser!: KCUserProfile
  private isLoading = true
  private isDirSearchUser: boolean = false

  private handleBackButton (): void {
    this.$router.push(`/account/${this.orgId}/business`)
  }

  private get accountInfoUrl (): string {
    return `/account/${this.orgId}/settings/account-info`
  }

  private get teamMembersUrl (): string {
    return `/account/${this.orgId}/settings/team-members`
  }

  private mounted () {
    this.isLoading = false
    this.isDirSearchUser = (this.currentUser?.loginSource === LoginSource.BCROS)
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
</style>
