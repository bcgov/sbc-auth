<template>
  <v-container
    class="view-container pt-0"
  >
    <!-- Staff - Breadcrumbs / Back Navigation -->
    <nav
      v-if="isStaff || isExternalStaff"
      class="crumbs py-6"
      aria-label="breadcrumb"
    >
      <div>
        <router-link :to="backToTab">
          <v-icon
            small
            color="primary"
            class="mr-1"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back to Staff Dashboard</span>
        </router-link>
      </div>
    </nav>

    <!-- Back Button -->
    <nav
      v-if="!isStaff && !isExternalStaff"
      class="crumbs py-6"
      aria-label="breadcrumb"
    >
      <div>
        <a
          href="javascript:void()"
          data-test="account-settings-back-button"
          @click="handleBackButton()"
        >
          <v-icon
            small
            color="#1a5a96"
            class="mr-1"
          >mdi-arrow-left</v-icon>
          <span>Go to My Dashboard</span>
        </a>
      </div>
    </nav>

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

    <div class="view-header flex-column">
      <h1
        class="view-header__title"
        data-test="account-settings-title"
      >
        {{ currentOrganization.name }}
      </h1>
      <p
        class="mt-3 mb-0"
      >
        Manage account settings, team members, and view transactions for this account
      </p>
    </div>

    <!-- Suspend Account Banner-->
    <AccountSuspendAlert
      v-if="showAccountFreezeBanner"
      class="account-alert mb-0"
    />

    <!-- Inactive Account Banner-->
    <AccountInactiveAlert
      v-if="showInactiveFreezeBanner"
      class="account-alert mb-0"
    />

    <v-card
      flat
      class="account-settings-card"
      data-test="account-settings-card"
    >
      <v-container class="nav-container py-6 pr-0 pl-8">
        <v-navigation-drawer
          permanent
          width="auto"
          data-test="account-nav-drawer"
        >
          <!-- Manage Account -->
          <v-list
            role="navigation"
            aria-label="Manage Account"
            class="py-0"
          >
            <v-list-item-group
              color="primary"
              role="list"
            >
              <v-subheader class="px-0">
                MANAGE ACCOUNT
              </v-subheader>
              <v-list-item
                dense
                class="py-1 px-4"
                aria-label="Account Information"
                role="listitem"
                :to="accountInfoUrl"
                data-test="account-info-nav-item"
              >
                <v-list-item-icon>
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-information-outline
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Account Info</v-list-item-title>
              </v-list-item>
              <v-list-item
                dense
                class="py-1 px-4"
                aria-label="Account Team Members"
                role="listitem"
                :to="teamMembersUrl"
                data-test="team-members-nav-item"
              >
                <v-list-item-icon>
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-account-group-outline
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Team Members</v-list-item-title>
              </v-list-item>
              <!-- now this menu dispalying for regular/GOVN account will add bceid also if needed later -->
              <v-list-item
                v-if="isRegularAccount || isGovnAccount"
                v-can:VIEW_AUTH_OPTIONS.hide
                dense
                class="py-1 px-4"
                aria-label="Team Member Authentication Methods"
                role="listitem"
                :to="accountAuthUrl"
                data-test="user-auth-nav-item"
              >
                <v-list-item-icon>
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-shield-account-outline
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Authentication</v-list-item-title>
              </v-list-item>
              <v-list-item
                v-can:VIEW_REQUEST_PRODUCT_PACKAGE.hide
                dense
                class="py-1 px-4"
                aria-label="Products and Payment"
                role="listitem"
                :to="getUrl('product-settings')"
                data-test="user-auth-nav-item"
              >
                <v-list-item-icon>
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-apps
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Products and Payment</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </v-list>
          <!-- Account Activity -->
          <v-list
            v-if="accountActivityMenuPermission"
            role="navigation"
            aria-label="Account Activity"
          >
            <!-- add inside permission when adding menu items in this list -->
            <v-list-item-group
              color="primary"
              role="list"
            >
              <v-subheader class="mt-2 px-0">
                ACCOUNT ACTIVITY
              </v-subheader>
              <v-list-item
                v-can:MANAGE_STATEMENTS.hide
                dense
                class="py-1 px-4"
                aria-label="Account Statements"
                role="listitem"
                :to="statementsUrl"
                data-test="statements-nav-item"
              >
                <v-list-item-icon>
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-file-document-outline
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Statements</v-list-item-title>
              </v-list-item>
              <v-list-item
                v-can:TRANSACTION_HISTORY.hide
                dense
                class="py-1 px-4"
                aria-label="Account Transactions"
                role="listitem"
                :to="transactionUrl"
                data-test="transactions-nav-item"
              >
                <v-list-item-icon>
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-format-list-bulleted
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Transactions</v-list-item-title>
              </v-list-item>

              <v-list-item
                v-can:VIEW_ACTIVITYLOG.hide
                dense
                class="py-1 px-4"
                aria-label="Activity Log"
                role="listitem"
                :to="activityLogUrl"
                data-test="activity-log-nav-item"
              >
                <v-list-item-icon>
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-history
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Activity Log</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </v-list>

          <!-- ADVANCED SETTINGS -->
          <v-list
            v-if="advancedSettingsPermission"
            role="navigation"
            aria-label="ADVANCED SETTINGS"
          >
            <!-- add inside permission when adding menu items in this list -->
            <v-list-item-group
              color="primary"
              role="list"
            >
              <v-subheader class="mt-2 px-0">
                ADVANCED SETTINGS
              </v-subheader>
              <!-- v-can:MANAGE_STATEMENTS.hide -->
              <v-list-item
                v-can:VIEW_DEVELOPER_ACCESS.hide
                dense
                class="py-1 px-4"
                aria-label="Developer Access"
                role="listitem"
                :to="developerAccessUrl"
                data-test="dev-nav-item"
              >
                <v-list-item-icon>
                  <!-- TODO: update mdi to get this icon -->
                  <v-icon
                    color="link"
                    left
                  >
                    mdi-settings-transfer-outline
                  </v-icon>
                </v-list-item-icon>
                <v-list-item-title>Developer Access</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </v-list>
        </v-navigation-drawer>
      </v-container>
      <transition
        name="fade"
        mode="out-in"
      >
        <router-view class="account-settings__content pt-7 pb-10 px-10" />
      </transition>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { AccountStatus, Pages, Permission, Role } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import AccountInactiveAlert from '@/components/auth/common/AccountInactiveAlert.vue'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import AccountSuspendAlert from '@/components/auth/common/AccountSuspendAlert.vue'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

  @Component({
    components: {
      AccountSuspendAlert,
      AccountInactiveAlert
    },
    computed: {
      ...mapState(useUserStore, [
        'currentUser'
      ]),
      ...mapState(useOrgStore, [
        'currentOrganization',
        'currentMembership',
        'permissions'
      ])
    },
    methods: {
      ...mapActions(useOrgStore, [
        'syncOrganization',
        'syncMembership'
      ])
    }
  })
export default class AccountSettings extends Mixins(AccountMixin) {
  @Prop({ default: -1 }) private orgId: number
  private readonly currentMembership!: Member
  private readonly currentUser!: KCUserProfile
  protected readonly syncOrganization!: (orgId: number) => Promise<Organization>
  protected readonly syncMembership!: (orgId: number) => Promise<Member>
  private isLoading = true
  private readonly pagesEnum = Pages
  private readonly permissions!: string[]

  private handleBackButton (): void {
    this.isStaff || this.isExternalStaff
      ? this.$router.push(Pages.STAFF_DASHBOARD)
      : window.location.assign(ConfigHelper.getBcrosDashboardURL(this.orgId))
  }

  private get isStaff ():boolean {
    return this.currentUser.roles.includes(Role.Staff)
  }

  private get isExternalStaff ():boolean {
    return this.currentUser.roles.includes(Role.ExternalStaffReadonly)
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
  private get activityLogUrl (): string {
    return `/account/${this.orgId}/settings/activity-log`
  }

  private get developerAccessUrl (): string {
    return `/account/${this.orgId}/settings/developer-access`
  }

  private get backToTab () {
    return this.currentOrganization?.statusCode === AccountStatus.NSF_SUSPENDED ? Pages.STAFF_DASHBOARD_SUSPENDED : Pages.STAFF_DASHBOARD
  }

  private getUrl (page) {
    return `/account/${this.orgId}/settings/${page}`
  }

  // show menu header if statment of activity log present
  get accountActivityMenuPermission () {
    return [Permission.VIEW_ACTIVITYLOG, Permission.MANAGE_STATEMENTS].some(per => this.permissions.includes(per))
  }
  // show menu header if developer acvess and premium account
  get advancedSettingsPermission () {
    return this.isPremiumAccount && [Permission.VIEW_DEVELOPER_ACCESS].some(per => this.permissions.includes(per))
  }

  // show baner for staff user and account suspended
  private get showAccountFreezeBanner () {
    return (this.isStaff || this.isExternalStaff) && (
      this.currentOrganization?.statusCode === AccountStatus.NSF_SUSPENDED ||
      this.currentOrganization?.statusCode === AccountStatus.SUSPENDED
    )
  }

  // show baner for staff user and account inactive
  private get showInactiveFreezeBanner () {
    return (this.isStaff || this.isExternalStaff) && (
      this.currentOrganization?.statusCode === AccountStatus.INACTIVE
    )
  }

  private async mounted () {
    await this.syncOrganization(this.orgId)
    await this.syncMembership(this.orgId)
    this.isLoading = false
  }
}
</script>

<style lang="scss" scoped>
  .account-settings-card {
    display: flex;
  }

  .nav-container {
    flex: 0 0 auto;
    width: 17.75rem;
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

  .account-alert.v-alert {
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
  }

  .account-alert + .v-card {
    border-top-right-radius: 0;
    border-top-left-radius: 0;
  }
</style>
