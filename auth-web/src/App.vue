<template>
  <v-app id="app">
    <div class="header-group" ref="headerGroup">
      <sbc-header
        :key="$route.fullPath"
        :account-name="currentOrganization && currentOrganization.name"
        :pending-approval-count="pendingActionCount"></sbc-header>
      <pay-system-alert></pay-system-alert>
    </div>
    <div class="app-body">
      <router-view/>
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import { Component, Watch } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import PaySystemAlert from '@/components/pay/PaySystemAlert.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import TokenService from 'sbc-common-components/src/services/token.services'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    SbcHeader,
    SbcFooter,
    PaySystemAlert
  },
  computed: {
    ...mapState('org', ['currentOrganization', 'pendingOrgMembers', 'myOrgMembership']),
    ...mapGetters('org', ['myOrgMembership'])
  }
})
export default class App extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private readonly currentOrganization!: Organization
  private readonly pendingOrgMembers!: Member[]
  private readonly myOrgMembership!: Member

  get pendingActionCount (): number {
    return (this.myOrgMembership &&
            this.myOrgMembership.membershipStatus === MembershipStatus.Active &&
            this.myOrgMembership.membershipTypeCode !== MembershipType.Member &&
            this.pendingOrgMembers.length) || 0
  }

  private async mounted (): Promise<void> {
    if (sessionStorage.getItem('KEYCLOAK_TOKEN')) {
      var self = this
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
