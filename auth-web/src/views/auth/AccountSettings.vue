<template>
  <div>
    <!-- Breadcrumbs / Back Navigation -->
    <nav class="crumbs" v-if="isDirSearchUser">
      <v-container class="pt-5 pb-4">
        <v-btn large text color="primary" class="back-btn pr-2 pl-1" :href="dirSearchUrl">
          <v-icon small class="mr-1">mdi-arrow-left</v-icon>
          <span>Director Search Home</span>
        </v-btn>
      </v-container>
    </nav>

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
          <p class="mt-3 mb-0">Manage account information and users of this account</p>
        </div>
      </div>
      <v-card flat class="account-settings-card" data-test="account-settings-card">
        <v-container class="nav-container py-8 px-6">
          <v-navigation-drawer floating permanent width="auto" data-test="account-nav-drawer">
            <v-list class="py-0">
              <v-list-item-group color="primary">
                <v-list-item dense class="py-1 px-4" :to="accountInfoUrl" data-test="account-info-nav-item">
                  <v-list-item-icon>
                    <v-icon color="link" left>mdi-information-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Account Info</v-list-item-title>
                </v-list-item>
                <v-list-item dense class="py-1 px-4" :to="teamMembersUrl" data-test="team-members-nav-item">
                  <v-list-item-icon>
                    <v-icon color="link" left>mdi-account-group-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Team Members</v-list-item-title>
                </v-list-item>
                <v-list-item :to="transactionUrl" data-test="transactions-nav-item">
                  <v-list-item-icon>
                    <v-icon color="link" left>mdi-file-document-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-title>Transactions</v-list-item-title>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-navigation-drawer>
        </v-container>
        <transition name="fade" mode="out-in">
          <router-view class="account-settings__content px-10 py-9"></router-view>
        </transition>
      </v-card>
    </v-container>
  </div>
</template>

<script lang="ts">

import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
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
  private dirSearchUrl = ConfigHelper.getSearchApplicationUrl()

  private handleBackButton (): void {
    this.$router.push(`/account/${this.orgId}/business`)
  }

  private get accountInfoUrl (): string {
    return `/account/${this.orgId}/settings/account-info`
  }

  private get teamMembersUrl (): string {
    return `/account/${this.orgId}/settings/team-members`
  }

  private get transactionUrl (): string {
    return `/account/${this.orgId}/settings/transactions`
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
    width: 17rem;
    border-radius: 0 !important;
    border-right: 1px solid var(--v-grey-lighten2);
  }

  .v-list-item .v-list-item__title {
    font-size: 0.875rem !important;
    font-weight: 700;
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

  .back-btn {
    font-weight: 700;

    span {
      margin-top: -1px;
    }

    &:hover {
      span {
        text-decoration: underline;
      }
    }
  }

  .crumbs + .view-container {
    padding-top: 0 !important;
  }
</style>
