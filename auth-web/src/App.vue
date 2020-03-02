<template>
  <v-app id="app">
    <div class="header-group" ref="headerGroup">
      <sbc-loader :show="showLoading" />
      <sbc-header :key="$store.state.refreshKey" in-auth=true />
       <v-snackbar top :color="toastType" v-model="showNotification" :timeout="toastTimeout">
        <span v-html="notificationText"></span>
        <v-btn icon @click="showNotification = false">
          <v-icon class="white--text">mdi-close</v-icon>
        </v-btn>
      </v-snackbar>
      <navigation-bar :configuration="navigationBarConfig" />
      <pay-system-alert />
    </div>
    <div class="app-body">
      <router-view/>
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { Pages, SessionStorageKeys } from '@/util/constants'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import BusinessModule from '@/store/modules/business'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import NavigationBar from 'sbc-common-components/src/components/NavigationBar.vue'
import { NavigationBarConfig } from 'sbc-common-components/src/models/NavigationBarConfig'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import PaySystemAlert from 'sbc-common-components/src/components/PaySystemAlert.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcLoader from 'sbc-common-components/src/components/SbcLoader.vue'
import TokenService from 'sbc-common-components/src/services/token.services'
import Vue from 'vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    SbcHeader,
    SbcFooter,
    SbcLoader,
    PaySystemAlert,
    NavigationBar
  },
  computed: {
    ...mapState('org', ['currentAccountSettings'])
  },
  methods: {
    ...mapActions('org', ['syncMembership', 'syncOrganization']),
    ...mapMutations('org', ['setCurrentAccountSettings', 'setCurrentOrganization'])
  }
})
export default class App extends Mixins(NextPageMixin) {
  private orgStore = getModule(OrgModule, this.$store)
  private readonly syncMembership!: (currentAccountId: string) => Promise<Member>
  private readonly syncOrganization!: (currentAccountId: string) => Promise<Organization>
  private readonly setCurrentAccountSettings!: (accountSettings: AccountSettings) => void
  private readonly setCurrentOrganization!: (org: Organization) => void
  private tokenService = new TokenService()
  private businessStore = getModule(BusinessModule, this.$store)
  private showNotification = false
  private notificationText = ''
  private showLoading = true
  private toastType = 'primary'
  private toastTimeout = 6000
  private navigationBarConfig: NavigationBarConfig = {
    titleItem: {
      name: '',
      url: ''
    },
    menuItems: []
  }

  get signingIn (): boolean {
    return this.$route.name === 'signin' ||
           this.$route.name === 'signin-redirect' ||
           this.$route.name === 'signin-redirect-full'
  }

  private setupNavigationBar (): void {
    this.navigationBarConfig = {
      titleItem: {
        name: 'Cooperatives Online',
        url: `/home`
      },
      menuItems: [
        {
          name: 'Manage Businesses',
          url: `/account/${this.currentOrganization?.id || ''}/business`
        }
      ]
    }
  }

  private async mounted (): Promise<void> {
    // set keycloak config file's location to the sbc-common-components
    await KeyCloakService.setKeycloakConfigUrl(`${process.env.VUE_APP_PATH}config/kc/keycloak.json`)
    this.showLoading = false

    EventBus.$on('show-toast', (eventInfo:Event) => {
      this.showNotification = true
      this.notificationText = eventInfo.message
      this.toastType = eventInfo.type
      this.toastTimeout = eventInfo.timeout
    })
    this.$root.$on('accountSyncStarted', async () => {
      this.showLoading = true
    })
    if (ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)) {
      await this.tokenService.init()
      this.tokenService.scheduleRefreshTimer()
    }
    this.$root.$on('accountSyncReady', async (currentAccount: AccountSettings) => {
      if (currentAccount) {
        const switchingToNewAccount = !this.currentAccountSettings || this.currentAccountSettings.id !== currentAccount.id
        this.setCurrentAccountSettings(currentAccount)
        const membership = await this.syncMembership(currentAccount.id)
        if (membership.membershipStatus === MembershipStatus.Active) {
          await this.syncOrganization(currentAccount.id)
          if (!this.signingIn) {
            this.toastType = 'primary'
            this.notificationText = `Switched to account '${currentAccount.label}'`
            this.showNotification = switchingToNewAccount
          }
          this.showLoading = false
          // if user was in a pending approval page and switched to an active account, take him to home page
          if (this.$route.path.indexOf(Pages.PENDING_APPROVAL) > 0) {
            this.$router.push(`/home`)
          }
        } else if (membership.membershipStatus === MembershipStatus.Pending) {
          this.setCurrentOrganization({ id: +currentAccount.id, name: currentAccount.label })
          this.$router.push(`/${Pages.PENDING_APPROVAL}/${currentAccount.label}`)
          this.showLoading = false
          return
        }
      }
      this.setupNavigationBar()

      if (this.signingIn) {
        this.redirectAfterLogin()
      }
    })
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
