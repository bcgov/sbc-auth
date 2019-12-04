// You can declare a mixin as the same style as components.
<script lang="ts">
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapGetters, mapState } from 'vuex'
import Component from 'vue-class-component'
import { Pages } from '@/util/constants'
import { User } from '@/models/user'
import Vue from 'vue'

@Component({
  computed: {
    ...mapState('user', ['userProfile']),
    ...mapGetters('org', ['myOrg', 'myOrgMembership'])
  }
})
export default class NextPageMixin extends Vue {
  protected readonly userProfile!: User
  protected readonly myOrg!: Organization
  protected readonly myOrgMembership!: Member

  protected getNextPageUrl (): string {
    let nextStep:string = '/'
    // Redirect to user profile if no contact info
    // Redirect to create team if no orgs
    // Redirect to dashboard otherwise
    if (this.userProfile) {
      if (!this.userProfile.contacts || this.userProfile.contacts.length === 0) {
        nextStep = Pages.USER_PROFILE
      } else if (!this.myOrg) {
        nextStep = Pages.CREATE_TEAM
      } else if (this.myOrgMembership.membershipStatus === MembershipStatus.Pending) {
        nextStep = Pages.PENDING_APPROVAL + '/' + this.myOrg.name
      } else {
        nextStep = Pages.MAIN
      }
    }
    return '/' + nextStep
  }
}
</script>
