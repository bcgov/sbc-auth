<template>
  <div v-if="inviteError">
    <interim-landing
      :summary="$t('errorOccurredTitle')"
      :description="$t('invitationProcessingErrorMsg')"
      iconColor="error"
      icon="mdi-alert-circle-outline"
    />
  </div>
</template>

<script lang="ts">

import { AccessType, LoginSource, Pages } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { Invitation } from '@/models/Invitation'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import { User } from '@/models/user'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

@Component({
  computed: {
    ...mapState(useUserStore, ['userProfile', 'userContact', 'redirectAfterLoginUrl']),
    ...mapState(useOrgStore, ['currentOrganization', 'currentMembership', 'currentAccountSettings'])
  },
  methods: {
    ...mapActions(useOrgStore, ['acceptInvitation', 'setCurrentOrganization', 'setCurrentMembership']),
    ...mapActions(useUserStore, ['getUserProfile'])
  },
  components: { InterimLanding }
})
export default class AcceptInviteView extends Mixins(NextPageMixin) {
  private readonly acceptInvitation!: (token: string) => Promise<Invitation>
  private readonly getUserProfile!: (identifier: string) => Promise<User>
  private readonly setCurrentOrganization!: (organization: Organization) => void
  private readonly setCurrentMembership!: (membership: Member) => void
  @Prop() token: string
  private inviteError: boolean = false
  @Prop({ default: LoginSource.BCSC }) loginSource: string

  private async mounted () {
    await this.getUserProfile('@me')
    await this.accept()
  }

  private isProfileNeeded (): boolean {
    return this.loginSource.toUpperCase() !== LoginSource.IDIR.toUpperCase()
  }

  /**
   * is terms accepted : No -> Redirect to TOS page with token in url ; else continue
   * User profile[contact] not filled out: -> Redirect him to user profile url
   * Else invitation flow
   */
  private async accept () {
    try {
      // affidavit need for admin users only if not verified before
      const affidavitNeeded = !!this.$route.query.affidavit && !this.userProfile?.verified
      // if affidavit needed we will append that also in URL so we can refirect user to new flow after TOS accept
      const affidavitNeededURL = affidavitNeeded ? `?affidavit=true` : ''
      if (!this.userProfile.userTerms.isTermsOfUseAccepted) {
        await this.$router.push(`/${Pages.USER_PROFILE_TERMS}/${this.token}${affidavitNeededURL}`)
      } else if (this.token && affidavitNeeded) {
        await this.$router.push(`/${Pages.AFFIDAVIT_COMPLETE}/${this.token}`)
      } else if (!this.userContact && this.isProfileNeeded()) {
        await this.$router.push(`/${Pages.USER_PROFILE}/${this.token}`)
      } else {
        const invitation = await this.acceptInvitation(this.token)
        const invitingOrg = invitation?.membership[0]?.org
        this.setCurrentAccountSettings({
          id: invitingOrg.id,
          label: invitingOrg.name,
          type: 'ACCOUNT',
          urlpath: '',
          urlorigin: ''
        })
        // sync org since govm account is already approved
        if (invitingOrg?.accessType === AccessType.GOVM) {
          await this.syncUserProfile()
          this.setCurrentOrganization(invitation?.membership[0]?.org)
          const membershipType: any = invitation?.membership[0]?.membershipType
          const membership: Member = {
            membershipTypeCode: membershipType,
            id: null,
            membershipStatus: MembershipStatus.Active,
            user: null
          }
          this.setCurrentMembership(membership)
        } else {
          await this.syncMembership(invitation?.membership[0]?.org?.id)
        }
        // Remove Vuex with Vue 3
        this.$store.commit('updateHeader')
        this.$router.push(this.getNextPageUrl())
      }
    } catch (exception) {
      this.inviteError = true
    }
  }
}
</script>
