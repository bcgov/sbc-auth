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
      appBodyOffset: { },
      lines: ['one', 'two', 'three']
    }
  },

  methods: {
    matchHeight () {
      var heightString = this.$refs.headerGroup.clientHeight + 'px'
      Vue.set(this.appBodyOffset, 'margin-top', heightString)
    }
  },

  mounted () {
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
