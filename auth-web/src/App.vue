<template>
  <v-app id="app">
    <div class="header-group" ref="headerGroup">
      <sbc-header :key="$store.state.refreshKey"></sbc-header>
      <pay-system-alert></pay-system-alert>
    </div>
    <div class="app-body">
      <router-view/>
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import { Component } from 'vue-property-decorator'
import PaySystemAlert from 'sbc-common-components/src/components/PaySystemAlert.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import TokenService from 'sbc-common-components/src/services/token.services'
import Vue from 'vue'

@Component({
  components: {
    SbcHeader,
    SbcFooter,
    PaySystemAlert
  }
})
export default class App extends Vue {
  private async mounted (): Promise<void> {
    if (sessionStorage.getItem('KEYCLOAK_TOKEN')) {
      let tokenService = new TokenService()
      await tokenService.initUsingUrl(`${process.env.VUE_APP_PATH}config/kc/keycloak.json`)
      tokenService.scheduleRefreshTimer()
    }
  }
}

</script>

<style lang="scss">
  .app-container {
    display: flex;
    flex-flow: column nowrap;
    min-height: 100vh
  }

  .header-group {
    position: sticky;
    position: -webkit-sticky; /* For Safari support */
    top: 0;
    width: 100%;
    z-index: 2;
  }

  .app-body {
    flex: 1 1 auto;
    position: relative;
  }
</style>
