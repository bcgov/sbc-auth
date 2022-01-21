<template>
  <div v-if="inviteError">
    <interim-landing :summary="$t('errorOccurredTitle')" :description="$t('invitationProcessingErrorMsg')" iconColor="error" icon="mdi-alert-circle-outline">
    </interim-landing>
  </div>
</template>

<script lang="ts">

import { AccessType, IdpHint, LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import { Contact } from '@/models/contact'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { Invitation } from '@/models/Invitation'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import { User } from '@/models/user'

@Component({
  computed: {
    ...mapState('user', ['userProfile', 'userContact', 'redirectAfterLoginUrl']),
    ...mapState('org', ['currentOrganization', 'currentMembership', 'currentAccountSettings'])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganization', 'setCurrentMembership'
    ]),
    ...mapActions('org', ['acceptInvitation']),
    ...mapActions('user', ['getUserProfile'])
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
      const affidavitNeeded = !!this.$route.query.affidavit
      // if affidavit needed we will append that also in URL so we can refirect user to new flow after TOS accept
      const affidavitNeededURL = affidavitNeeded ? `?affidavit=true` : ''
      if (!this.userProfile.userTerms.isTermsOfUseAccepted) {
        await this.$router.push(`/${Pages.USER_PROFILE_TERMS}/${this.token}${affidavitNeededURL}`)
        return
      } else if (this.token && affidavitNeeded) {
        await this.$router.push(`/${Pages.AFFIDAVIT_COMPLETE}/${this.token}`)
        return
      } else if (!this.userContact && this.isProfileNeeded()) {
        await this.$router.push(`/${Pages.USER_PROFILE}/${this.token}`)
        return
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
