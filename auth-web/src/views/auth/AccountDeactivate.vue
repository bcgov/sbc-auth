<template>
  <v-container>
    <nav
      class="crumbs py-6"
      aria-label="breadcrumb">
      <div>
        <router-link to="d">
          <v-icon small color="primary" class="mr-1">mdi-arrow-left</v-icon>
          <span>Back to Account</span>
        </router-link>
      </div>
    </nav>
    <header class="view-header mb-9">
      <h2 class="view-header__title">Deactivate Account</h2>
      </header>
    <div class="mb-9">
      Please review the information below before deactivating your BC Registries and Online Services account.
    </div>
    <div>
      <deactivate-card></deactivate-card>
    </div>
    <v-card class="mt-10">
      <v-card-title class="font-weight-bold">
        Authorize and Deactivate Account
      </v-card-title>
      <v-card-text>
        <v-checkbox
          color="primary"
          class="terms-checkbox align-checkbox-label--top ma-0 pa-0"
          required
          data-test="check-termsAccepted"
        >
          <template v-slot:label>
            <span class="label-color ml-2">
              I understand that all team members, businesses and payment methods associated with this account
will be permanently removed from this account after once the 10 day deactivation period is complete.
            </span>

          </template>
        </v-checkbox>
      </v-card-text>
    </v-card>

  </v-container>
</template>

<script lang="ts">

import { AccountStatus, LDFlags, LoginSource, Pages, Permission, Role } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import AccountSuspendAlert from '@/components/auth/common/AccountSuspendAlert.vue'
import ConfigHelper from '@/util/config-helper'
import DeactivateCard from '@/components/auth/account-deactivate/DeactivateCard.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'

  @Component({
    components: {
      DeactivateCard,
      AccountSuspendAlert
    },
    computed: {
      ...mapState('user', [
        'currentUser'
      ]),
      ...mapState('org', [
        'currentOrganization',
        'currentMembership',
        'permissions'
      ])
    },
    methods: {
      ...mapActions('org', [
        'syncOrganization'
      ])
    }
  })
export default class AccountDeactivate extends Mixins(AccountMixin) {
  @Prop({ default: '' }) private orgId: string
  private readonly currentMembership!: Member
  private readonly currentUser!: KCUserProfile
  protected readonly syncOrganization!: (orgId: number) => Promise<Organization>
  private isLoading = true
  private isDirSearchUser: boolean = false
  private dirSearchUrl = ConfigHelper.getDirectorSearchURL()
  private readonly pagesEnum = Pages
  private readonly permissions!: string[]

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
  private get activityLogUrl (): string {
    return `/account/${this.orgId}/settings/activity-log`
  }

  private get backToTab () {
    return this.currentOrganization?.statusCode === AccountStatus.NSF_SUSPENDED ? Pages.STAFF_DASHBOARD_SUSPENDED : Pages.STAFF_DASHBOARD
  }

  private getUrl (page) {
    return `/account/${this.orgId}/settings/${page}`
  }

  private get enablePaymentMethodSelectorStep (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.PaymentTypeAccountCreation) || false
  }
  private get hideProductPackage (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.HideProductPackage) || false
  }
  // show menu header if statment of activity log present
  get accountActivityMenuPermission () {
    return [Permission.VIEW_ACTIVITYLOG, Permission.MANAGE_STATEMENTS].some(per => this.permissions.includes(per))
  }
  // show baner for staff user and account suspended
  private get showAccountFreezeBanner () {
    return this.isStaff && (this.currentOrganization?.statusCode === AccountStatus.NSF_SUSPENDED || this.currentOrganization?.statusCode === AccountStatus.SUSPENDED)
  }

  private async mounted () {
    this.isLoading = false
    this.isDirSearchUser = (this.currentUser?.loginSource === LoginSource.BCROS)
    if (this.$route.query?.tryOrgRefresh === 'true') {
      this.isLoading = true
      let count = 0
      let timerId = setInterval(async () => {
        // eslint-disable-next-line no-console
        console.log(`[OrgRefreshTimer] Org refresh ${++count}`)
        if (this.currentOrganization?.statusCode !== AccountStatus.ACTIVE) {
          await this.syncOrganization(this.currentOrganization?.id)
        } else {
          // eslint-disable-next-line no-console
          console.log('[OrgRefreshTimer] Org refresh stopped (ACTIVE)')
          clearInterval(timerId)
          this.isLoading = false
        }
      }, 3000)
      setTimeout(() => {
        // eslint-disable-next-line no-console
        console.log('[OrgRefreshTimer] Org refresh stopped')
        clearInterval(timerId)
        this.isLoading = false
      }, 10000)
    }
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
