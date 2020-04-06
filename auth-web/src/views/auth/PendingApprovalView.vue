<template>
  <div>
    <template v-if="isDenied">
      <interim-landing :summary="$t('notAuthorized')" :description="$t('deniedInvitationMsg', { team: $route.params.team_name })" icon="mdi-alert-circle-outline" iconColor="error">
      </interim-landing>
    </template>
    <template v-else>
      <div v-if="$route.params.team_name">
        <interim-landing :summary="$t('pendingInvitationTitle', { team: $route.params.team_name })" :description="$t('pendingInvitationMsg')" icon="mdi-information-outline">
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
import { Member, MembershipStatus } from '@/models/Organization'
import { Component } from 'vue-property-decorator'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import OrgModule from '@/store/modules/org'
import { Role } from '@/util/constants'
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
}
</script>
