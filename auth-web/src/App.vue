<template>
  <v-app class="app-container" id="app">
    <pay-system-alert></pay-system-alert>
    <sbc-layout>
      <router-view/>
    </sbc-layout>
  </v-app>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import SbcLayout from 'sbc-common-components/src/components/SbcLayout.vue'
import PaySystemAlert from '@/components/pay/PaySystemAlert.vue'

  @Component({
    components: {
      SbcLayout,
      PaySystemAlert
    }
  })

export default class App extends Vue {
}
</script>

<style lang="stylus">
  @import "./assets/styl/base.styl";
  @import "./assets/styl/layout.styl";
  @import "./assets/styl/overrides.styl";
</style>
