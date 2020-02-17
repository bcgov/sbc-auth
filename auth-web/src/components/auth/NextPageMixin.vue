// You can declare a mixin as the same style as components.
<script lang="ts">
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapGetters, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import Component from 'vue-class-component'
import { Contact } from '@/models/contact'
import { Pages } from '@/util/constants'
import { User } from '@/models/user'
import Vue from 'vue'

@Component({
  computed: {
    ...mapState('user', ['userProfile', 'userContact', 'redirectAfterLoginUrl']),
    ...mapState('org', ['currentOrganization', 'currentMembership', 'currentAccountSettings']),
    ...mapGetters('org', ['myOrgMembership'])
  }
})
export default class NextPageMixin extends Vue {
  protected readonly userProfile!: User
  protected readonly userContact!: Contact
  protected readonly redirectAfterLoginUrl: string
  protected readonly currentOrganization!: Organization
  protected readonly currentMembership!: Member
  protected readonly currentAccountSettings!: AccountSettings

  protected getNextPageUrl (): string {
    let nextStep = '/'
    // Redirect to user profile if no contact info or terms not accepted
    // Redirect to create team if no orgs
    // Redirect to dashboard otherwise
    if (!this.userContact || !this.userProfile.userTerms.isTermsOfUseAccepted) {
      nextStep = Pages.USER_PROFILE
    } else if (!this.currentOrganization && !this.currentMembership) {
      nextStep = Pages.CREATE_ACCOUNT
    } else if (this.currentMembership.membershipStatus === MembershipStatus.Active) {
      nextStep = `${Pages.MAIN}/${this.currentOrganization.id}`
    } else if (this.currentMembership.membershipStatus === MembershipStatus.Pending) {
      nextStep = `${Pages.PENDING_APPROVAL}/${this.currentAccountSettings?.label}`
    } else {
      nextStep = `${Pages.MAIN}/${this.currentOrganization.id}`
    }
    return '/' + nextStep
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
}
</script>
