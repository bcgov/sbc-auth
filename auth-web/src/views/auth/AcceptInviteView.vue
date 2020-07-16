<template>
  <div v-if="inviteError">
    <interim-landing :summary="$t('errorOccurredTitle')" :description="$t('invitationProcessingErrorMsg')" iconColor="error" icon="mdi-alert-circle-outline">
    </interim-landing>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { Pages, SessionStorageKeys } from '@/util/constants'
import { mapActions, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import { Invitation } from '@/models/Invitation'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('user', ['userProfile', 'userContact', 'redirectAfterLoginUrl']),
    ...mapState('org', ['currentOrganization', 'currentMembership', 'currentAccountSettings'])
  },
  methods: {
    ...mapActions('org', ['acceptInvitation']),
    ...mapActions('user', ['getUserProfile'])
  },
  components: { InterimLanding }
})
export default class AcceptInviteView extends Mixins(NextPageMixin) {
  private readonly acceptInvitation!: (token: string) => Promise<Invitation>
  private readonly getUserProfile!: (identifier: string) => Promise<User>
  protected readonly userContact!: Contact
  protected readonly userProfile!: User

  @Prop() token: string
  private inviteError: boolean = false

  private async mounted () {
    await this.getUserProfile('@me')
    await this.accept()
  }

  /**
   * is terms accepted : No -> Redirect to TOS page with token in url ; else continue
   * User profile[contact] not filled out: -> Redirect him to user profile url
   * Else invitation flow
   */
  private async accept () {
    try {
      if (!this.userProfile.userTerms.isTermsOfUseAccepted) {
        this.$router.push(`/${Pages.USER_PROFILE_TERMS}/${this.token}`)
        return
      } else if (!this.userContact) {
        this.$router.push(`/${Pages.USER_PROFILE}/${this.token}`)
        return
      } else {
        const invitation = await this.acceptInvitation(this.token)
        // ConfigHelper.addToSession(SessionStorageKeys.CurrentAccount, JSON.stringify({ id: invitation.membership[0].org.id, label: invitation.membership[0].org.name }))
        const invitingOrg = invitation.membership[0].org
        this.setCurrentAccountSettings({
          id: invitingOrg.id,
          label: invitingOrg.name,
          type: 'ACCOUNT',
          urlpath: '',
          urlorigin: ''
        })
        await this.syncMembership(invitation?.membership[0]?.org?.id)
        this.$store.commit('updateHeader')
        this.$router.push(this.getNextPageUrl())
        return
      }
    } catch (exception) {
      this.inviteError = true
    }
  }
}
</script>
