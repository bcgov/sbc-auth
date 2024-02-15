<template>
  <InterimLanding
    :summary="$t('profileDeactivatedTitle')"
    :description="$t('profileDeactivatedMsg')"
    icon="mdi-information-outline"
  />
</template>

<script lang="ts">
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'ProfileDeactivatedView',
  components: { InterimLanding }
})
</script>
