<template>
  <SbcAuthenticationOptions
    :in-auth="true"
  />
</template>

<script lang="ts">
import SbcAuthenticationOptions from 'sbc-common-components/src/components/SbcAuthenticationOptions.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'AuthenticationOptionsView',
  components: {
    SbcAuthenticationOptions
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
</style>
