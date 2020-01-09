<template>
  <div v-if="inviteError">
    <interim-landing :summary="$t('errorOccurredTitle')" :description="$t('invitationProcessingErrorMsg')" iconColor="error" icon="mdi-alert-circle-outline">
    </interim-landing>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import { Invitation } from '@/models/Invitation'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapActions('org', ['acceptInvitation', 'syncOrganizations']),
    ...mapActions('user', ['getUserProfile'])
  },
  components: { InterimLanding }
})
export default class AcceptInviteView extends Mixins(NextPageMixin) {
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private readonly acceptInvitation!: (token: string) => Invitation
  private readonly syncOrganizations!: () => Organization[]
  private readonly getUserProfile!: (identifier: string) => User

  @Prop() token: string
  private inviteError: boolean = false

  private async mounted () {
    await this.getUserProfile('@me')
    await this.syncOrganizations()
    // Check to make sure this user is not already a member of a team
    if (this.organizations.length > 0) {
      this.$router.push('/duplicateteam')
    } else {
      this.accept()
    }
  }

  private async accept () {
    try {
      await this.acceptInvitation(this.token)
      // the accept invitation creates a new org
      await this.syncOrganizations()
      this.$router.push(this.getNextPageUrl())
    } catch (exception) {
      this.inviteError = true
    }
  }
}
</script>
