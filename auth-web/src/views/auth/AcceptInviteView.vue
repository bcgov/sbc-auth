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
import { mapActions, mapGetters, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import { Invitation } from '@/models/Invitation'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('user', ['userProfile', 'userContact', 'redirectAfterLoginUrl']),
    ...mapState('org', ['currentOrganization', 'currentMembership', 'currentAccountSettings']),
    ...mapGetters('org', ['myOrgMembership'])
  },
  methods: {
    ...mapActions('org', ['acceptInvitation']),
    ...mapActions('user', ['getUserProfile'])
  },
  components: { InterimLanding }
})
export default class AcceptInviteView extends Mixins(NextPageMixin) {
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
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
   * User profile filled out?: Accept invitation, set orgid in sessionstorage, update header
   * User profile incomplete?:  Redirect to user profile, user profile will direct here after
   */
  private async accept () {
    try {
      if (!this.userContact || !this.userProfile.userTerms.isTermsOfUseAccepted) {
        // Go to user profile, with the token, so that we can continue acceptance flow afterwards
        this.$router.push(`/${Pages.USER_PROFILE}/${this.token}`)
        return
      } else {
        const invitation = await this.acceptInvitation(this.token)
        ConfigHelper.addToSession(SessionStorageKeys.CurrentAccount, JSON.stringify({ id: invitation.membership[0].org.id }))
        this.$store.commit('updateHeader') // this event eventually redirects to Pending approval page.No extra navigation needed
        return
      }
    } catch (exception) {
      this.inviteError = true
    }
  }
}
</script>
