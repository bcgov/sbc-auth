<template>
  <div>
    <template v-if="isDenied">
      <interim-landing :summary="$t('notAuthorized')" :description="$t('deniedInvitationMsg', { team: $route.params.team_name })" icon="mdi-alert-circle-outline" iconColor="error">
      </interim-landing>
    </template>
    <template v-else>
      <div v-if="$route.params.team_name">
        <interim-landing :summary="$t('pendingAffidavitReviewTitle', { team: $route.params.team_name })" :description="$t('pendingAffidvitReviewMessage')" icon="mdi-information-outline">
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
import { OrgStatus, Organization } from '@/models/Organization'
import { Component } from 'vue-property-decorator'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  components: { InterimLanding },
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  }
})

export default class PendingApprovalView extends Vue {
  protected readonly currentOrganization!: Organization
  private isDenied: boolean = false

  mounted () {
    this.isDenied = (this.currentOrganization?.statusCode === OrgStatus.Rejected)
  }
}
</script>
