<template>
  <sbc-signout :redirect-url="redirectbackUrl" />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'
import { resetAllStores } from '@/stores'

@Component({
  methods: {
  },
  components: {
    SbcSignout
  }
})

export default class SignoutView extends Vue {
  @Prop() redirectUrl: string

  get redirectbackUrl () {
    // redirect to dashboard on logout
    // TODO need to fix for one URL
    if (!this.redirectUrl) {
      return `${ConfigHelper.getRegistryHomeURL()}/login`
    }
    return this.redirectUrl
  }

  async mounted () {
    // Remove with Vue 3
    this.$store.replaceState({})
    resetAllStores()
  }
}
</script>

<style lang="scss" scoped>
</style>
