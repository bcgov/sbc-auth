<template>
  <sbc-signout :redirect-url="redirectbackUrl"></sbc-signout>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'

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
      return ConfigHelper.getRegistryHomeURL()
    }
    return this.redirectUrl
  }

  async mounted () {
    this.$store.replaceState({})
  }
}
</script>

<style lang="scss" scoped>
</style>
