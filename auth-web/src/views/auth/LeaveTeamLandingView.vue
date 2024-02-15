<template>
  <InterimLanding
    :summary="$t('leaveTeamTitle')"
    :description="$t('leaveTeamMsg')"
  />
</template>

<script lang="ts">
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'LeaveTeamLandingView',
  components: { InterimLanding }
})
</script>
