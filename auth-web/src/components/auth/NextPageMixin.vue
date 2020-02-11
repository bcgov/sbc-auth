// You can declare a mixin as the same style as components.
<script lang="ts">
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapGetters, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import Component from 'vue-class-component'
import { Contact } from '@/models/contact'
import { Pages } from '@/util/constants'
import { User } from '@/models/user'
import Vue from 'vue'

@Component({
  computed: {
    ...mapState('user', ['userProfile', 'userContact']),
    ...mapState('org', ['currentOrganization', 'currentMembership', 'currentAccountSettings']),
    ...mapGetters('org', ['myOrgMembership'])
  }
})
export default class NextPageMixin extends Vue {
  protected readonly userProfile!: User
  protected readonly userContact!: Contact
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
}
</script>
