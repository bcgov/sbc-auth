<template>
  <sbc-login :redirectUrl="redirectUrl" />
</template>

<script lang="ts">
// Libraries
import { Component, Vue } from 'vue-property-decorator'

// Components
import SbcLogin from 'sbc-common-components/src/components/SbcLogin.vue'

/**
 * Operation:
 * 1. When this component is first loaded (ie, we are not authenticated) then the
 *    SbcLogin component will redirect us to log in.
 */
@Component({
  components: {
    SbcLogin
  }
})
export default class LoginView extends Vue {
  get redirectUrl () {
    return (this.$route.query.redirect as string)
  }
}
</script>

<style lang="scss" scoped>
</style>
