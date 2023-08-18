<template>
  <interim-landing
    :summary="$t('leaveTeamTitle')"
    :description="$t('leaveTeamMsg')"
  />
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'

import Vue from 'vue'

@Component({
  components: { InterimLanding }
})
export default class LeaveTeamLandingView extends Vue {

}
</script>
