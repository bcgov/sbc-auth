<template>
  <v-app class="app-container" id="app">
    <sbc-layout>
      <router-view/>
    </sbc-layout>
  </v-app>
</template>

<script>
  import Vue from 'vue'
  import SbcLayout from 'sbc-common-components/src/components/SbcLayout.vue'

  export default Vue.extend({
    name: 'app',
    components: {
      SbcLayout
    }
  })
</script>

<style lang="stylus">
  @import "./assets/styl/base.styl";
  @import "./assets/styl/layout.styl";
  @import "./assets/styl/overrides.styl";
</style>
