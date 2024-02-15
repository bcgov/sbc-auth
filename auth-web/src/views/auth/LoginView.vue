<template>
  <SbcLogin :redirectUrl="redirectUrl" />
</template>

<script lang="ts">
// Components
import SbcLogin from 'sbc-common-components/src/components/SbcLogin.vue'
import { defineComponent } from '@vue/composition-api'

/**
 * Operation:
 * 1. When this component is first loaded (ie, we are not authenticated) then the
 *    SbcLogin component will redirect us to log in.
 */
export default defineComponent({
  name: 'LoginView',
  components: {
    SbcLogin
  },
  setup(props, { root }) {
    function redirectUrl () {
      return root.$route.query.redirect as string
    }

    return {
      redirectUrl
    }
  }

})
</script>

<style lang="scss" scoped>
</style>
