<template>
  <div>
    <template v-if="isDenied">

      <interim-landing :summary="$t('notAuthorized')" :description="$t('deniedInvitationMsg', { team: teamName })" icon="mdi-alert-circle-outline" iconColor="error">
      </interim-landing>
    </template>
    <template v-else>
      <div v-if="teamName">
        <interim-landing :summary="$t(title, { team: teamName })" :description="$t(description)" icon="mdi-information-outline">
        </interim-landing>
      </div>
      <div v-if="!teamName">
        <interim-landing :summary="$t('noPendingInvitationTitle')" :description="$t('noPendingInvitationMsg')" icon="mdi-information-outline">
        </interim-landing>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus } from '@/models/Organization'

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
  @Prop({ default: '' }) teamName: string
  @Prop({ default: '' }) pendingAffidavit: string

  mounted () {
    this.isDenied = (this.currentMembership?.membershipStatus === MembershipStatus.Rejected || this.currentMembership?.membershipStatus === MembershipStatus.Inactive)
  }

  get title () {
    return this.pendingAffidavit === 'true' ? 'pendingAffidavitReviewTitle' : 'pendingInvitationTitle'
  }
  get description () {
    return this.pendingAffidavit === 'true' ? 'pendingAffidvitReviewMessage' : 'pendingInvitationMsg'
  }
}
</script>
