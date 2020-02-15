<template>
  <div v-if="inviteError">
    <interim-landing :summary="$t('errorOccurredTitle')" :description="$t('invitationProcessingErrorMsg')" iconColor="error" icon="mdi-alert-circle-outline">
    </interim-landing>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { Member, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
import { Contact } from '@/models/contact'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import { Invitation } from '@/models/Invitation'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { Pages } from '@/util/constants'
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
   * do they have a user profile already : accept invitation ; set orgid to sessionstorage ; reset header
   * no user profile :  do nothing; redirect to user profile
   *
   */
  private async accept () {
    try {
      if (!this.userContact || !this.userProfile.userTerms.isTermsOfUseAccepted) {
        // or simply go to user profile
        this.$router.push(`/${Pages.USER_PROFILE}/${this.token}`)
        return
      } else {
        const invitation = await this.acceptInvitation(this.token)
        sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify({ id: invitation.membership[0].org.id }))
        this.$store.commit('updateHeader')
        // this.$router.push(this.getNextPageUrl())
      }

      const invitation = await this.acceptInvitation(this.token)
      this.$store.commit('updateHeader')
      this.$router.push(this.getNextPageUrl())
    } catch (exception) {
      this.inviteError = true
    }
  }
}
</script>
