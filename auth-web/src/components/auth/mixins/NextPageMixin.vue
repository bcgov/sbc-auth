// You can declare a mixin as the same style as components.
<script lang="ts">
import { LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus, MembershipType, OrgStatus, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import Component from 'vue-class-component'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import OrgModule from '@/store/modules/org'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('user', ['currentUser', 'userProfile', 'userContact', 'redirectAfterLoginUrl']),
    ...mapState('org', ['currentOrganization', 'currentMembership', 'currentAccountSettings'])
  },
  methods: {
    ...mapActions('user', ['loadUserInfo', 'syncUserProfile', 'getUserProfile']),
    ...mapActions('org', ['syncOrganization', 'syncMembership', 'resetCurrentOrganization']),
    ...mapMutations('org', ['setCurrentAccountSettings'])
  }
})
export default class NextPageMixin extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private orgStore = getModule(OrgModule, this.$store)
  protected readonly currentUser!: KCUserProfile
  protected readonly userProfile!: User
  protected readonly userContact!: Contact
  protected readonly redirectAfterLoginUrl: string
  protected readonly currentOrganization!: Organization
  protected readonly currentMembership!: Member
  protected readonly currentAccountSettings!: AccountSettings
  protected readonly setCurrentAccountSettings!: (accountSettings: AccountSettings) => void
  protected readonly syncUserProfile!: () => void
  protected readonly syncOrganization!: (currentAccount: number) => Promise<Organization>
  protected readonly syncMembership!: (currentAccount: number) => Promise<Member>
  protected readonly resetCurrentOrganization!: () => Promise<void>

  protected getAccountFromSession (): AccountSettings {
    return JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || '{}'))
  }

  protected getNextPageUrl (): string {
    switch (this.currentUser?.loginSource) {
      case LoginSource.IDIR:
        return `/${Pages.SEARCH_BUSINESS}`
      case LoginSource.BCROS:
        let bcrosNextStep = '/'
        if (!this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          bcrosNextStep = `/${Pages.USER_PROFILE_TERMS}`
        } else if (this.currentOrganization && this.currentMembership.membershipStatus === MembershipStatus.Active) {
          if ((this.currentMembership.membershipTypeCode === MembershipType.Admin) || (this.currentMembership.membershipTypeCode === MembershipType.Coordinator)) {
            bcrosNextStep = `/${Pages.MAIN}/${this.currentOrganization.id}/settings/team-members`
          } else {
            bcrosNextStep = ConfigHelper.getValue('DIRECTOR_SEARCH_URL')
          }
        }
        return bcrosNextStep
      case LoginSource.BCSC:
        let nextStep = '/'
        // Redirect to TOS if no terms accepted
        // for invited users , handle user profile
        // Redirect to create team if no orgs
        // Redirect to dashboard otherwise
        if (!this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          nextStep = Pages.USER_PROFILE_TERMS
        } else if (!this.currentOrganization && !this.currentMembership) {
          nextStep = Pages.CREATE_ACCOUNT
        } else if (this.currentOrganization && this.currentMembership.membershipStatus === MembershipStatus.Active) {
          nextStep = `${Pages.MAIN}/${this.currentOrganization.id}`
        } else if (this.currentMembership.membershipStatus === MembershipStatus.Pending) {
          nextStep = `${Pages.PENDING_APPROVAL}/${this.currentAccountSettings?.label}`
        } else {
          nextStep = `${Pages.MAIN}/${this.currentOrganization.id}`
        }
        return `/${nextStep}`
      case LoginSource.BCEID:
        // if they are in invitation flow [check session storage], take them to
        // Redirect to TOS if no terms accepted
        // for invited users , handle user profile
        // Redirect to create team if no orgs
        // Redirect to dashboard otherwise
        let bceidNextStep = '/'
        let invToken = ConfigHelper.getFromSession(SessionStorageKeys.InvitationToken)
        if (invToken) {
          bceidNextStep = `${Pages.CONFIRM_TOKEN}/${invToken}`
          ConfigHelper.removeFromSession(SessionStorageKeys.InvitationToken)
        } else if (!this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          bceidNextStep = Pages.USER_PROFILE_TERMS
        } else if (!this.currentOrganization && !this.currentMembership) {
          let isExtraProv = ConfigHelper.getFromSession(SessionStorageKeys.ExtraProvincialUser)
          if (isExtraProv) {
            bceidNextStep = Pages.CREATE_NON_BCSC_ACCOUNT
          } else {
            bceidNextStep = Pages.CHOOSE_AUTH_METHOD
          }
        } else if (this.currentOrganization && this.currentOrganization.statusCode === OrgStatus.PendingAffidavitReview) {
          bceidNextStep = `${Pages.PENDING_APPROVAL}/${this.currentAccountSettings?.label}/true`
        } else if (this.currentOrganization && this.currentMembership.membershipStatus === MembershipStatus.Active) {
          bceidNextStep = `${Pages.MAIN}/${this.currentOrganization.id}`
        } else if (this.currentMembership.membershipStatus === MembershipStatus.Pending) {
          bceidNextStep = `${Pages.PENDING_APPROVAL}/${this.currentAccountSettings?.label}`
        } else {
          bceidNextStep = `${Pages.MAIN}/${this.currentOrganization.id}`
        }
        return `/${bceidNextStep}`
      default:
        return `/${Pages.HOME}`
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
      // await this.syncOrganization(this.currentAccountSettings.id)
      if (this.currentMembership.membershipStatus === MembershipStatus.Active) {
        await this.syncOrganization(this.currentAccountSettings.id)
      } else {
        // Set current org to blank state if not active in the current org
        await this.resetCurrentOrganization()
      }
    }
  }
}
</script>
