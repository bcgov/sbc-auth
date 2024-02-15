<template>
  <InterimLanding
    :summary="$t('pageNotFoundTitle')"
    :description="$t('pageNotFoundMsg')"
    icon="mdi-alert-circle-outline"
    iconColor="error"
  />
</template>

<script lang="ts">
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import { defineComponent } from '@vue/composition-api'
export default defineComponent({
  name: 'PageNotFound',
  components: { InterimLanding }
})
</script>
