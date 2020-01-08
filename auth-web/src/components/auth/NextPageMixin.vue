// You can declare a mixin as the same style as components.
<script lang="ts">
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapGetters, mapState } from 'vuex'
import Component from 'vue-class-component'
import { Contact } from '@/models/contact'
import { Pages } from '@/util/constants'
import { User } from '@/models/user'
import Vue from 'vue'

@Component({
  computed: {
    ...mapState('user', ['userProfile', 'userContact']),
    ...mapState('org', ['organizations', 'currentOrganization']),
    ...mapGetters('org', ['myOrgMembership'])
  }
})
export default class NextPageMixin extends Vue {
  protected readonly userProfile!: User
  protected readonly userContact!: Contact
  protected readonly myOrgMembership!: Member
  protected readonly organizations!: Organization[]
  protected readonly currentOrganization!: Organization

  protected getNextPageUrl (): string {
    let nextStep = '/'
    // Redirect to user profile if no contact info or terms not accepted
    // Redirect to create team if no orgs
    // Redirect to dashboard otherwise
    if (!this.userContact || !this.userProfile.userTerms.isTermsOfUseAccepted) {
      nextStep = Pages.USER_PROFILE
    } else if (!this.currentOrganization) {
      nextStep = Pages.CREATE_TEAM
    } else if (this.myOrgMembership.membershipStatus === MembershipStatus.Active) {
      nextStep = Pages.MAIN
    } else if (this.myOrgMembership.membershipStatus === MembershipStatus.Pending) {
      nextStep = Pages.PENDING_APPROVAL + '/' + this.currentOrganization.name
    } else {
      nextStep = Pages.MAIN
    }
    return '/' + nextStep
  }
}
</script>
