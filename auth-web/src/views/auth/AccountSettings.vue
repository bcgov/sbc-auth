<template>
  <v-container
    class="view-container"
    :class="{ 'crumbs-visible' : isDirSearchUser || isStaff }"
  >

    <!-- Director Search - Breadcrumbs / Back Navigation -->
    <nav class="crumbs py-6" v-if="isDirSearchUser" aria-labelledby="dirSearchNav">
      <div>
        <a :href="dirSearchUrl">
          <v-icon small color="primary" class="mr-1">mdi-arrow-left</v-icon>
          <span>Director Search Home</span>
        </a>
      </div>
    </nav>

    <!-- Staff - Breadcrumbs / Back Navigation -->
    <nav class="crumbs py-6" v-if="isStaff" aria-labelledby="staffNav">
      <div>
        <router-link to="/searchbusiness">
          <v-icon small color="primary" class="mr-1">mdi-arrow-left</v-icon>
          <span>Back to Staff Dashboard</span>
        </router-link>
      </div>
    </nav>

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
        v-if="!isDirSearchUser && !isStaff"
        data-test="account-settings-back-button">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      <div v-if="!isStaff">
        <h1 class="view-header__title" data-test="account-settings-title">Account Settings</h1>
        <p class="mt-3 mb-0">Manage account information and users of this account</p>
      </div>
      <div v-if="isStaff">
        <h1 class="view-header__title" data-test="account-settings-title">{{currentOrganization.name}}</h1>
        <p class="mt-3 mb-0">Manage account settings, team members, and view transactions for this account</p>
      </div>
    </div>

    <v-card flat class="account-settings-card" data-test="account-settings-card">
      <v-container class="nav-container py-7 pl-4">
        <v-navigation-drawer permanent width="auto" data-test="account-nav-drawer">

          <!-- Manage Account -->
          <v-list class="py-0">
            <v-list-item-group color="primary">
              <v-subheader>MANAGE ACCOUNT</v-subheader>
              <v-list-item dense class="py-1 px-6" :to="accountInfoUrl" data-test="account-info-nav-item">
                <v-list-item-icon>
                  <v-icon color="link" left>mdi-information-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Account Info</v-list-item-title>
              </v-list-item>
              <v-list-item dense class="py-1 px-6" :to="teamMembersUrl" data-test="team-members-nav-item">
                <v-list-item-icon>
                  <v-icon color="link" left>mdi-account-group-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Team Members</v-list-item-title>
              </v-list-item>
              <v-list-item dense class="py-1 px-6" :to="accountAuthUrl"  v-if="isRegularAccount" v-can:SET_AUTH_OPTIONS.hide data-test="user-auth-nav-item">
                <v-list-item-icon>
                  <v-icon color="link" left>mdi-shield-account-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Authentication</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </v-list>

          <!-- Account Activity -->
          <v-list v-if="isPremiumAccount" v-can:MANAGE_STATEMENTS.hide>
            <v-list-item-group color="primary">
              <v-subheader class="mt-4">ACCOUNT ACTIVITY</v-subheader>
              <v-list-item dense class="py-1 px-6"
                :to="statementsUrl"
                data-test="statements-nav-item"
              >
                <v-list-item-icon>
                  <v-icon color="link" left>mdi-file-document-outline</v-icon>
                </v-list-item-icon>
                <v-list-item-title>Statements</v-list-item-title>
              </v-list-item>
              <v-list-item dense class="py-1 px-6"
                :to="transactionUrl"
                data-test="transactions-nav-item"
              >
                <v-list-item-icon>
                  <v-icon color="link" left>mdi-format-list-bulleted</v-icon>
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
</template>

<script lang="ts">

import { Component, Mixins, Prop } from 'vue-property-decorator'
import { LoginSource, Pages, Role } from '@/util/constants'
import { Member, MembershipType } from '@/models/Organization'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'

import { mapState } from 'vuex'

  @Component({
    computed: {
      ...mapState('user', [
        'currentUser'
      ]),
      ...mapState('org', [
        'currentOrganization',
        'currentMembership'
      ])
    }
  })
export default class AccountSettings extends Mixins(AccountMixin) {
  @Prop({ default: '' }) private orgId: string
  private readonly currentMembership!: Member
  private readonly currentUser!: KCUserProfile
  private isLoading = true
  private isDirSearchUser: boolean = false
  private dirSearchUrl = ConfigHelper.getSearchApplicationUrl()

  private handleBackButton (): void {
    const backTo = this.isStaff ? Pages.STAFF_DASHBOARD : `/account/${this.orgId}/business`
    this.$router.push(backTo)
  }

  private get isStaff ():boolean {
    return this.currentUser.roles.includes(Role.Staff)
  }

  private get accountInfoUrl (): string {
    return `/account/${this.orgId}/settings/account-info`
  }

  private get teamMembersUrl (): string {
    return `/account/${this.orgId}/settings/team-members`
  }

  private get accountAuthUrl (): string {
    return `/account/${this.orgId}/settings/login-option`
  }

  private get transactionUrl (): string {
    return `/account/${this.orgId}/settings/transactions`
  }

  private get statementsUrl (): string {
    return `/account/${this.orgId}/settings/statements`
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
  }

  .v-subheader {
    color: var(--v-grey-darken4) !important;
    font-weight: bold;
  }

  .v-list-item .v-list-item__title {
    font-size: 0.875rem;
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

  .crumbs a {
    font-size: 0.875rem;
    text-decoration: none;

    i {
      margin-top: -2px;
    }
  }

  .crumbs a:hover {
    span {
      text-decoration: underline;
    }
  }

  .crumbs-visible {
    padding-top: 0 !important;
  }
</style>
