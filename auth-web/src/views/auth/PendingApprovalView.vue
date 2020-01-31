<template>
  <div>
    <div v-if="$route.params.team_name">
      <interim-landing :summary="$t('pendingInvitationTitle', { team: $route.params.team_name })" :description="$t('pendingInvitationMsg')" icon="mdi-information-outline">
      </interim-landing>
    </div>
    <div v-if="!$route.params.team_name">
      <interim-landing :summary="$t('noPendingInvitationTitle')" :description="$t('noPendingInvitationMsg')" icon="mdi-information-outline">
      </interim-landing>
    </div>
  </div>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import InterimLanding from '@/components/auth/InterimLanding.vue'
import { Role } from '@/util/constants'
import { UserInfo } from '@/models/userInfo'
import Vue from 'vue'
import { mapState } from 'vuex'

@Component({
  components: { InterimLanding }
})
export default class PendingApprovalView extends Vue { }
</script>
