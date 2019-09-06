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
  }
})

</script>

<style lang="scss">
  @import "./assets/scss/base.scss";
  @import "./assets/scss/layout.scss";
  @import "./assets/scss/overrides.scss";

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
    flex: 1 1 auto
  }

  @media (min-width: 1264px) {
    .app-body
      > .container:first-child {
        padding-top: 3rem;
        padding-bottom: 3rem
      }
  }
</style>
