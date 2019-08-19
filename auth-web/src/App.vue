<template>
  <v-app class="app-container" id="app">
    <div class="header-group" ref="headerGroup">
      <pay-system-alert></pay-system-alert>
      <sbc-header></sbc-header>
    </div>
    <div class="app-body" v-bind:style="appBodyOffset">
      <router-view/>
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import Vue from 'vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import PaySystemAlert from '@/components/pay/PaySystemAlert.vue'

export default Vue.extend({
  name: 'app',
  components: {
    SbcHeader,
    SbcFooter,
    PaySystemAlert
  },

  data: function () {
    return {
      // The amount to offset the app body so that it is positioned correctly (below the header)
      appBodyOffset: { }
    }
  },

  methods: {
    // Set the top margin of the app body to match the height of the header group
    matchHeight () {
      var heightString = this.$refs.headerGroup.clientHeight + 'px'
      Vue.set(this.appBodyOffset, 'margin-top', heightString)
    }
  },

  mounted () {
    // When the window is resized, reset the top margin of the app body
    this.matchHeight()
    window.addEventListener('resize', this.matchHeight)
  }
})

</script>

<style lang="stylus">
  @import "./assets/styl/base.styl";
  @import "./assets/styl/layout.styl";
  @import "./assets/styl/overrides.styl";
</style>
