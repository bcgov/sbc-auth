<template>
  <v-app id="app">
    <div class="header-group" ref="headerGroup">
      <sbc-header :key="$route.fullPath"></sbc-header>
      <pay-system-alert></pay-system-alert>
    </div>
    <div class="app-body">
      <router-view/>
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import PaySystemAlert from '@/components/pay/PaySystemAlert.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import Vue from 'vue'

export default Vue.extend({
  name: 'app',
  components: {
    SbcHeader,
    SbcFooter,
    PaySystemAlert
  },
  mounted (): void {
    // eslint-disable-next-line no-console
    console.log('APP.vue mounted')
    if (sessionStorage.getItem('KEYCLOAK_TOKEN')) {
      // eslint-disable-next-line no-console
      console.info('[APP.vue] Token exists.So start the refreshtimer')
      var self = this
      this.$tokenService.initUsingUrl(`/${process.env.VUE_APP_PATH}/config/kc/keycloak.json`).then(function (success) {
        self.$tokenService.scheduleRefreshTimer()
      })
    }
  }
})

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

    > .container:first-child {
      padding-top: 3rem;
      padding-bottom: 4rem;
    }
  }

  ::v-deep .v-alert__wrapper {
    max-width: 1224px;
  }
</style>
