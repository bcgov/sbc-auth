// You can declare a mixin as the same style as components.
<script lang="ts">
import Component from 'vue-class-component'
import { Organization } from '@/models/Organization'
import { Pages } from '@/util/constants'
import { User } from '@/models/user'

import Vue from 'vue'

@Component({})
export default class NextPageMixin extends Vue {
  getNextPageUrl (userProfile:User, organizations:Organization[]):string {
    let nextStep:string = '/'
    // Redirect to user profile if no contact info
    // Redirect to create team if no orgs
    // Redirect to dashboard otherwise
    if (userProfile) {
      if (!userProfile.contacts || userProfile.contacts.length === 0) {
        nextStep = Pages.USER_PROFILE
      } else if (organizations.length === 0) {
        nextStep = Pages.CREATE_TEAM
      } else if (organizations.some(org => org.members[0].membershipStatus === 'PENDING_APPROVAL')) {
        nextStep = Pages.PENDING_APPROVAL + '/' + organizations[0].name
      } else {
        nextStep = Pages.MAIN
      }
    }
    return '/' + nextStep
  }
}
</script>
