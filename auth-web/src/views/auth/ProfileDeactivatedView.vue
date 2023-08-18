<template>
  <interim-landing
    :summary="$t('profileDeactivatedTitle')"
    :description="$t('profileDeactivatedMsg')"
    icon="mdi-information-outline"
  />
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import InterimLanding from '@/components/auth/common/InterimLanding.vue'
import Vue from 'vue'

@Component({
  components: { InterimLanding }
})
export default class ProfileDeactivatedView extends Vue {
}
</script>
