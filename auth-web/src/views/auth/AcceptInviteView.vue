<template>
  <div v-if="inviteError">
    <InterimLanding
      :summary="$t('errorOccurredTitle')"
      :description="$t('invitationProcessingErrorMsg')"
      iconColor="error"
      icon="mdi-alert-circle-outline"
    />
  </div>
</template>

<script lang="ts">

import { AccessType, AccountStatus, ExternalStaffAccounts, LoginSource, Pages } from '@/util/constants'
import { Member, MembershipStatus } from '@/models/Organization'
import { defineComponent, getCurrentInstance, onMounted, reactive, toRefs } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import { useAppStore } from '@/stores'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'AcceptInviteLandingView',
  components: {
    InterimLanding
  },
  mixins: [NextPageMixin],
  props: {
    token: {
      type: String,
      required: true
    },
    loginSource: {
      type: String,
      default: LoginSource.BCSC
    }
  },
  setup (props, { root }) {
    const { proxy } = getCurrentInstance()
    const mixinProxy = proxy as any
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    const state = reactive({
      inviteError: false
    })

    function isProfileNeeded (): boolean {
      return props.loginSource.toUpperCase() !== LoginSource.IDIR.toUpperCase()
    }

    /**
   * is terms accepted : No -> Redirect to TOS page with token in url ; else continue
   * User profile[contact] not filled out: -> Redirect him to user profile url
   * Else invitation flow
   */
    async function accept () {
      try {
      // affidavit need for admin users only if not verified before
        const affidavitNeeded = !!root.$route.query.affidavit && !userStore.userProfile?.verified
        // if affidavit needed we will append that also in URL so we can refirect user to new flow after TOS accept
        const affidavitNeededURL = affidavitNeeded ? `?affidavit=true` : ''
        if (!userStore.userProfile.userTerms.isTermsOfUseAccepted) {
          await root.$router.push(`/${Pages.USER_PROFILE_TERMS}/${props.token}${affidavitNeededURL}`)
        } else if (props.token && affidavitNeeded) {
          await root.$router.push(`/${Pages.AFFIDAVIT_COMPLETE}/${props.token}`)
        } else if (!userStore.userContact && isProfileNeeded()) {
          await root.$router.push(`/${Pages.USER_PROFILE}/${props.token}`)
        } else {
          const invitation = await orgStore.acceptInvitation(props.token)
          const invitingOrg = invitation?.membership[0]?.org
          orgStore.setCurrentAccountSettings({
            id: invitingOrg.id,
            label: invitingOrg.name,
            type: 'ACCOUNT',
            urlpath: '',
            urlorigin: ''
          })
          // sync org since govm account is already approved
          if (invitingOrg?.accessType === AccessType.GOVM) {
            await userStore.syncUserProfile()
            // This gets overridden by the next setup in app.vue.
            orgStore.setCurrentOrganization(invitation?.membership[0]?.org)
            orgStore.createGovmOrgId = invitation?.membership[0]?.org?.id
            // set govm org Id.
            const membershipType: any = invitation?.membership[0]?.membershipType
            const membership: Member = {
              membershipTypeCode: membershipType,
              id: null,
              membershipStatus: MembershipStatus.Active,
              user: null
            }
            orgStore.setCurrentMembership(membership)
          } else {
            await orgStore.syncMembership(invitation?.membership[0]?.org?.id)
          }
          useAppStore().updateHeader()
          redirectToNextPage(invitingOrg)
        }
      } catch (exception) {
        console.error(exception)
        state.inviteError = true
      }
    }

    function redirectToNextPage(invitingOrg) {
      const isExternalStaff = ExternalStaffAccounts.includes(invitingOrg.typeCode)
      if (invitingOrg.statusCode === AccountStatus.ACTIVE && isExternalStaff) {
        window.location.assign(`${ConfigHelper.getSelfURL()}${Pages.STAFF_DASHBOARD}`)
      } else {
        const redirectUrl = mixinProxy.getNextPageUrl()
        mixinProxy.redirectTo(redirectUrl)
      }
    }

    onMounted(async () => {
      await userStore.getUserProfile('@me')
      await accept()
    })

    return {
      ...toRefs(state),
      accept,
      isProfileNeeded
    }
  }
})
</script>
