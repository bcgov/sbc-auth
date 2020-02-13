<template>
  <v-app id="app">
    <div class="header-group" ref="headerGroup">
      <sbc-loader :show="showLoading"></sbc-loader>
      <sbc-header :key="$store.state.refreshKey"></sbc-header>
      <v-snackbar top color="primary" v-model="showNotification">
        <span v-html="notificationText"></span>
        <v-btn icon @click="showNotification = false">
          <v-icon class="white--text">mdi-close</v-icon>
        </v-btn>
      </v-snackbar>
      <pay-system-alert></pay-system-alert>
    </div>
    <div class="app-body">
      <router-view/>
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import BusinessModule from '@/store/modules/business'
import { Component } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'
import PaySystemAlert from 'sbc-common-components/src/components/PaySystemAlert.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcLoader from 'sbc-common-components/src/components/SbcLoader.vue'
import { SessionStorageKeys } from '@/util/constants'
import TokenService from 'sbc-common-components/src/services/token.services'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    SbcHeader,
    SbcFooter,
    SbcLoader,
    PaySystemAlert
  },
  computed: {
    ...mapState('org', ['currentAccountSettings'])
  },
  methods: {
    ...mapActions('org', ['syncMembership', 'syncOrganization']),
    ...mapMutations('org', ['setCurrentAccountSettings'])
  }
})
export default class App extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private readonly currentAccountSettings!: AccountSettings
  private readonly syncMembership!: (currentAccountId: string) => Promise<Member>
  private readonly syncOrganization!: (currentAccountId: string) => Promise<Organization>
  private readonly setCurrentAccountSettings!: (accountSettings: AccountSettings) => void
  private businessStore = getModule(BusinessModule, this.$store)
  showNotification = false
  notificationText = ''
  showLoading = true

  private async mounted (): Promise<void> {
    this.showLoading = false
    if (ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)) {
      this.$root.$on('accountSyncStarted', async () => {
        this.showLoading = true
      })

      let tokenService = new TokenService()
      await tokenService.initUsingUrl(`${process.env.VUE_APP_PATH}config/kc/keycloak.json`)
      tokenService.scheduleRefreshTimer()

      this.$root.$on('accountSyncReady', async (currentAccount: AccountSettings) => {
        if (currentAccount) {
          const switchingToNewAccount = !this.currentAccountSettings || this.currentAccountSettings.id !== currentAccount.id
          this.setCurrentAccountSettings(currentAccount)
          const membership = await this.syncMembership(currentAccount.id)
          if (membership.membershipStatus === MembershipStatus.Active) {
            await this.syncOrganization(currentAccount.id)
            this.notificationText = `Switched to account '${currentAccount.label}'`
            this.showNotification = switchingToNewAccount
            this.showLoading = false
          }
        }
      })
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
