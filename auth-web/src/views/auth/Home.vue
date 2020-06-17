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
