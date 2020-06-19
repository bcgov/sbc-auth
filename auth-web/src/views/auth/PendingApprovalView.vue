<template>
  <div>
    <template v-if="isDenied">
      <interim-landing :summary="$t('notAuthorized')" :description="$t('deniedInvitationMsg', { team: $route.params.team_name })" icon="mdi-alert-circle-outline" iconColor="error">
      </interim-landing>
    </template>
    <template v-else>
      <div v-if="$route.params.team_name">
        <interim-landing :summary="$t(title, { team: $route.params.team_name })" :description="$t(description)" icon="mdi-information-outline">
        </interim-landing>
      </div>
      <div v-if="!$route.params.team_name">
        <interim-landing :summary="$t('noPendingInvitationTitle')" :description="$t('noPendingInvitationMsg')" icon="mdi-information-outline">
        </interim-landing>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { LoginSource, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus } from '@/models/Organization'
import { Component } from 'vue-property-decorator'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  components: { InterimLanding },
  computed: {
    ...mapState('org', [
      'currentMembership'
    ])
  }
})

export default class PendingApprovalView extends Vue {
  protected readonly currentMembership!: Member
  private isDenied: boolean = false

  mounted () {
    this.isDenied = (this.currentMembership?.membershipStatus === MembershipStatus.Rejected || this.currentMembership?.membershipStatus === MembershipStatus.Inactive)
  }

  get isExtraPro () {
    return sessionStorage.getItem(SessionStorageKeys.UserAccountType) === LoginSource.BCEID
  }

  get title () {
    return this.isExtraPro ? 'pendingAffidavitReviewTitle' : 'pendingInvitationTitle'
  }
  get description () {
    return this.isExtraPro ? 'pendingAffidvitReviewMessage' : 'pendingInvitationMsg'
  }
}
</script>
