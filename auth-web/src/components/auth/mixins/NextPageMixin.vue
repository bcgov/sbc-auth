// You can declare a mixin as the same style as components.
<script lang="ts">
import { AccountStatus, LoginSource, Pages, Permission, Role, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import { useOrgStore, useUserStore } from '@/stores'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import Component from 'vue-class-component'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { User } from '@/models/user'
import Vue from 'vue'

@Component({
  computed: {
    ...mapState(useUserStore, ['currentUser', 'userProfile', 'userContact', 'redirectAfterLoginUrl']),
    ...mapState(useOrgStore, ['currentOrganization', 'currentMembership', 'currentAccountSettings', 'permissions',
      'needMissingBusinessDetailsRedirect'])
  },
  methods: {
    ...mapActions(useUserStore, ['loadUserInfo', 'syncUserProfile', 'getUserProfile']),
    ...mapActions(useOrgStore, ['syncOrganization', 'syncMembership', 'resetCurrentOrganization',
      'setCurrentAccountSettings', 'syncStaffPermissions'])
  }
})
export default class NextPageMixin extends Vue {
  protected readonly currentUser!: KCUserProfile
  protected readonly userProfile!: User
  protected readonly userContact!: Contact
  protected readonly redirectAfterLoginUrl: string
  protected readonly currentOrganization!: Organization
  protected readonly currentMembership!: Member
  protected readonly currentAccountSettings!: AccountSettings
  protected readonly permissions!: string[]
  protected readonly setCurrentAccountSettings!: (accountSettings: AccountSettings) => void
  protected readonly syncUserProfile!: () => void
  protected readonly syncOrganization!: (currentAccount: number) => Promise<Organization>
  protected readonly syncMembership!: (currentAccount: number) => Promise<Member>
  protected readonly syncStaffPermissions!: () => Promise<string[]>
  protected readonly resetCurrentOrganization!: () => Promise<void>
  private readonly needMissingBusinessDetailsRedirect!: boolean
  // its used to determine if any pending redirect like NFS or account pending page
  protected anyPendingRedirect:boolean = false

  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }

  protected getNextPageUrl (): string {
    const dashboardUrl = `${ConfigHelper.getRegistryHomeURL()}dashboard`
    let orgName = ''
    switch (this.currentUser?.loginSource) {
      case LoginSource.IDIR:
        // if the user is staff redirect to staff dashboard
        orgName = encodeURIComponent(btoa(this.currentAccountSettings?.label))
        if (this.currentUser.roles.includes(Role.Staff)) {
          return `/${Pages.SEARCH_BUSINESS}`
        } else if (!this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          return `/${Pages.USER_PROFILE_TERMS}`
        } else if (this.currentOrganization && this.currentOrganization.statusCode === AccountStatus.PENDING_INVITE_ACCEPT) {
          return `/${Pages.CREATE_GOVM_ACCOUNT}`
          // waiting for staff approval
        } else if (this.currentMembership && this.currentMembership.membershipStatus === MembershipStatus.Pending) {
          return `/${Pages.PENDING_APPROVAL}/${orgName}`
          //  if account status pending invite accept need to send create account page w
        } else if (this.currentOrganization && this.currentOrganization.statusCode === AccountStatus.PENDING_STAFF_REVIEW) {
          // redirect to pending page
          return `/${Pages.SETUP_GOVM_ACCOUNT_SUCCESS}`
        } else {
          return dashboardUrl
        }
      case LoginSource.BCROS: {
        let bcrosNextStep = '/'
        if (!this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          bcrosNextStep = `/${Pages.USER_PROFILE_TERMS}`
        } else if (this.currentOrganization && this.currentMembership.membershipStatus === MembershipStatus.Active) {
          if ([MembershipType.Coordinator, MembershipType.Admin].includes(this.currentMembership.membershipTypeCode)) {
            bcrosNextStep = `/${Pages.MAIN}/${this.currentOrganization.id}/settings/team-members`
          } else {
            bcrosNextStep = ConfigHelper.getDirectorSearchURL()
          }
        }

        return bcrosNextStep
      }
      // case LoginSource.IDIR:
      case LoginSource.BCSC: {
        let nextStep = '/'
        // Redirect to TOS if no terms accepted
        // for invited users , handle user profile
        // Redirect to create team if no orgs
        // Redirect to dashboard otherwise
        orgName = encodeURIComponent(btoa(this.currentAccountSettings?.label))
        if (!this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          nextStep = `/${Pages.USER_PROFILE_TERMS}`
        } else if (!this.currentOrganization && !this.currentMembership) {
          nextStep = `/${Pages.CREATE_ACCOUNT}`
        } else if (this.currentOrganization && this.currentMembership.membershipStatus === MembershipStatus.Active) {
          nextStep = dashboardUrl // redirect to dashboard
        } else if (this.currentMembership.membershipStatus === MembershipStatus.Pending) {
          nextStep = `/${Pages.PENDING_APPROVAL}/${orgName}`
        } else {
          nextStep = dashboardUrl // redirect to dashboard
        }

        return nextStep
      }
      case LoginSource.BCEID: {
        // if they are in invitation flow [check session storage], take them to
        // Redirect to TOS if no terms accepted
        // for invited users , handle user profile
        // Redirect to create team if no orgs
        // Redirect to dashboard otherwise
        let bceidNextStep = '/'
        orgName = encodeURIComponent(btoa(this.currentAccountSettings?.label))
        let invToken = ConfigHelper.getFromSession(SessionStorageKeys.InvitationToken)
        const affidavitNeeded = ConfigHelper.getFromSession(SessionStorageKeys.AffidavitNeeded)

        if (invToken) {
          // if affidavit needed we will append that also in URL
          const affidavitNeededURL = affidavitNeeded === 'true' ? `?affidavit=true` : ''
          bceidNextStep = `/${Pages.CONFIRM_TOKEN}/${invToken}${affidavitNeededURL}`
          ConfigHelper.removeFromSession(SessionStorageKeys.InvitationToken)
          ConfigHelper.removeFromSession(SessionStorageKeys.AffidavitNeeded)
        } else if (!this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          bceidNextStep = `/${Pages.USER_PROFILE_TERMS}`
        } else if (!this.currentOrganization && !this.currentMembership) {
          let isExtraProv = ConfigHelper.getFromSession(SessionStorageKeys.ExtraProvincialUser)
          if (isExtraProv) {
            bceidNextStep = `/${Pages.CREATE_NON_BCSC_ACCOUNT}`
          } else {
            bceidNextStep = `/${Pages.CHOOSE_AUTH_METHOD}`
          }
        } else if (this.currentOrganization && this.currentOrganization.statusCode === AccountStatus.PENDING_STAFF_REVIEW) {
          bceidNextStep = `/${Pages.PENDING_APPROVAL}/${orgName}/true`
        } else if (this.currentOrganization && this.currentMembership.membershipStatus === MembershipStatus.Active) {
          bceidNextStep = dashboardUrl// redirect to dashboard
        } else if ([MembershipStatus.PendingStaffReview, MembershipStatus.Pending].includes(this.currentMembership?.membershipStatus)) {
          // if user is pending show pending page.
          bceidNextStep = `/${Pages.PENDING_APPROVAL}/${orgName}`
        } else {
          bceidNextStep = dashboardUrl // redirect to dashboard
        }

        return `${bceidNextStep}`
      }
      default:
        return dashboardUrl
    }
  }

  protected redirectAfterLogin () {
    // If a redirect url is given, redirect to that page else continue to dashboard or userprofile
    if (this.redirectAfterLoginUrl) {
      if (CommonUtils.isUrl(this.redirectAfterLoginUrl)) {
        window.location.href = decodeURIComponent(this.redirectAfterLoginUrl)
      } else {
        this.$router.push(`/${this.redirectAfterLoginUrl}`)
      }
    } else {
      this.$router.push(this.getNextPageUrl())
    }
  }

  protected redirectTo (target: string): void {
    if (CommonUtils.isUrl(target)) {
      // Solves where we get passed http:/www.google.ca for example.
      if (!target.includes('://')) {
        target = target.replace(':/', '://')
      }
      window.location.assign(target)
    } else {
      if (this.$route.path !== target) {
        this.$router.push(target)
      }
    }
  }

  protected async syncUser () {
    // eslint-disable-next-line no-console
    await this.syncUserProfile()
    this.setCurrentAccountSettings(this.getAccountFromSession())
    if (this.currentAccountSettings) {
      await this.syncMembership(this.currentAccountSettings.id)
      // not sure if this code is needed..but shud be invoked only if member is active
      if (this.currentMembership.membershipStatus === MembershipStatus.Active) {
        await this.syncOrganization(this.currentAccountSettings.id)
      }
      if (this.currentMembership.membershipStatus !== MembershipStatus.Active) {
        // Set current org to blank state if not active in the current org
        await this.resetCurrentOrganization()
      }
    }

    // This occurs on account switching, if we are on the dashboard, we want to resync staff permissions
    if (this.$route.fullPath.includes(Pages.STAFF_DASHBOARD)) {
      await this.syncStaffPermissions()
    }
  }

  protected accountFreezeRedirect () {
    if (this.currentOrganization?.statusCode === AccountStatus.NSF_SUSPENDED) {
      this.anyPendingRedirect = true
      // eslint-disable-next-line no-console
      console.log('Redirecting user to Account Freeze message since the account is temporarly suspended.')
      if (this.permissions.some(code => code === Permission.MAKE_PAYMENT)) {
        this.$router.push(`/${Pages.ACCOUNT_FREEZE_UNLOCK}`)
      } else {
        this.$router.push(`/${Pages.ACCOUNT_FREEZE}`)
      }
    } else {
      /** If user is in the account freeze page while switching the account,
       * then need to redirect them to account info page if that account is active.
       * otherwise user will stuck on the account freeze page **/
      if (this.$route.name?.search('account-freeze') > -1) {
        this.anyPendingRedirect = true
        this.$router.push(`${Pages.MAIN}/${this.currentOrganization.id}/${Pages.ACCOUNT_SETTINGS}`)
      }
    }
  }

  protected accountPendingRedirect () {
    if (this.needMissingBusinessDetailsRedirect) {
      this.anyPendingRedirect = true
      this.$router.push(`/${Pages.UPDATE_ACCOUNT}`)
    } else if (this.currentMembership.membershipStatus === MembershipStatus.Active && this.$route.path.indexOf(Pages.PENDING_APPROVAL) > 0) {
      // 1. If user was in a pending approval page and switched to an active account, take them to the back to page
      this.anyPendingRedirect = false
    } else if (this.currentMembership.membershipStatus === MembershipStatus.Pending) {
      this.anyPendingRedirect = true
      const label = encodeURIComponent(btoa(this.currentAccountSettings?.label))
      // 2. If user has a pending account status, take them to pending approval page (no matter where they are)
      this.$router.push(`/${Pages.PENDING_APPROVAL}/${label}`)
    }
  }
}
</script>
