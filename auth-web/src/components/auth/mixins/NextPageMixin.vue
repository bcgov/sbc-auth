// You can declare a mixin as the same style as components.
<script lang="ts">
import { LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
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
  protected readonly currentUser: KCUserProfile
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
      case LoginSource.BCROS:
        return `/${Pages.SEARCH_BUSINESS}`
      case LoginSource.BCSC:
        let nextStep = '/'
        // Redirect to user profile if no contact info or terms not accepted
        // Redirect to create team if no orgs
        // Redirect to dashboard otherwise
        if (!this.userContact || !this.userProfile?.userTerms?.isTermsOfUseAccepted) {
          nextStep = Pages.USER_PROFILE
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
      this.$router.push(target)
    }
  }

  protected async syncUser () {
    this.setCurrentAccountSettings(this.getAccountFromSession())
    await this.syncUserProfile()
    if (this.currentAccountSettings) {
      await this.syncMembership(this.currentAccountSettings.id)
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
