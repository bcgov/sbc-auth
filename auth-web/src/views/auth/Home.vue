<template>
  <section>
    <home-view v-if="!featurFlag"/>
    <home-view-dev v-else />
  </section>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import HomeView from '@/views/auth/HomeView.vue'
import HomeViewDev from '@/views/auth/HomeViewDev.vue'

// This Component will be removed before launch when we revert to a single HomeView.
// Currently in place to provide a reactive means of responding to changes of state in the LdFlagging.
@Component({
  components: {
    HomeView,
    HomeViewDev
  }
})
export default class LearnMoreButton extends Vue {
  private get featurFlag () {
    return ConfigHelper.getLaunchFeatureFlag()
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';
</style>
