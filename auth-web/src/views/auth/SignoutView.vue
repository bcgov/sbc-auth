<template>
  <SbcSignout :redirect-url="redirectbackUrl" />
</template>

<script lang="ts">
import { computed, defineComponent, onMounted } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'
import { resetAllStores } from '@/stores'

export default defineComponent({
  name: 'SignoutView',
  components: {
    SbcSignout
  },
  props: {
    redirectUrl: {
      type: String,
      default: ''
    }
  },
  setup (props, { root }) {
    const redirectbackUrl = computed(() => {
      // redirect to dashboard on logout
      // TODO need to fix for one URL
      if (!props.redirectUrl) {
        return `${ConfigHelper.getRegistryHomeURL()}/login`
      }
      return props.redirectUrl
    })

    onMounted(() => {
      // Remove with Vue 3
      // TODO test this.
      root.$store.replaceState({})
      resetAllStores()
    })

    return {
      redirectbackUrl
    }
  }
})

</script>

<style lang="scss" scoped>
</style>
