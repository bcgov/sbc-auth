<template>
  <v-app id="app">
    <div class="header-group" ref="headerGroup">
      <sbc-loader :show="showLoading" />
      <sbc-header
        :key="$store.state.refreshKey"
        :in-auth="true"
        :show-product-selector="false"
        @account-switch-started="startAccountSwitch"
        @account-switch-completed="completeAccountSwitch"
        @hook:mounted="setup"
        idpHint="bcsc"
        ref="header">
        <template v-slot:login-button-text>
          Log in with BC Services Cardss
        </template>
      </sbc-header>
       <v-snackbar top :color="toastType" v-model="showNotification" :timeout="toastTimeout">
        <span v-html="notificationText"></span>
        <v-btn icon @click="showNotification = false">
          <v-icon class="white--text">mdi-close</v-icon>
        </v-btn>
      </v-snackbar>
      <navigation-bar :configuration="navigationBarConfig" :hide="!showNavigationBar" />
      <pay-system-alert />
    </div>
    <div class="app-body">
      <router-view  />
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { Pages, SessionStorageKeys } from '@/util/constants'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import BusinessModule from '@/store/modules/business'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import NavigationBar from 'sbc-common-components/src/components/NavigationBar.vue'
import { NavigationBarConfig } from 'sbc-common-components/src/models/NavigationBarConfig'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import PaySystemAlert from 'sbc-common-components/src/components/PaySystemAlert.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcLoader from 'sbc-common-components/src/components/SbcLoader.vue'
import TokenService from 'sbc-common-components/src/services/token.services'
import UserModule from '@/store/modules/user'
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
    ...mapState('org', ['currentAccountSettings']),
    ...mapState('user', ['currentUser'])
  },
  methods: {
    ...mapMutations('org', ['setCurrentOrganization']),
    ...mapActions('user', ['loadUserInfo'])
  }
})
export default class App extends Mixins(NextPageMixin) {
  private readonly setCurrentOrganization!: (org: Organization) => void
  private readonly isAuthenticated!: boolean
  private readonly loadUserInfo!: () => KCUserProfile
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
      url: '',
      meta: {
        requiresAuth: false,
        requiresAccount: false
      }
    },
    menuItems: []
  }

  $refs: {
    header: SbcHeader
  }

  get signingIn (): boolean {
    return this.$route.name === 'signin' ||
           this.$route.name === 'signin-redirect' ||
           this.$route.name === 'signin-redirect-full'
  }

  get showNavigationBar (): boolean {
    return this.$route.meta.showNavBar
  }

  private setupNavigationBar (): void {
    this.navigationBarConfig = {
      titleItem: {
        name: 'Cooperatives Online',
        url: `/home`,
        meta: {
          requiresAuth: false,
          requiresAccount: false
        }
      },
      menuItems: [
        {
          name: 'Manage Businesses',
          url: `/account/${this.currentAccountSettings?.id || '0'}/business`,
          meta: {
            requiresAuth: true,
            requiresAccount: true
          }
        }
      ]
    }
  }

  private startAccountSwitch () {
    this.showLoading = true
  }

  private async completeAccountSwitch () {
    await this.syncUser()
    this.showLoading = false
    this.toastType = 'primary'
    this.notificationText = `Switched to account '${this.currentAccountSettings.label}'`
    this.showNotification = true

    // Some edge cases where user needs to be redirected based on their account status and current location
    if (this.currentMembership.membershipStatus === MembershipStatus.Active && this.$route.path.indexOf(Pages.PENDING_APPROVAL) > 0) {
      // 1. If user was in a pending approval page and switched to an active account, take them to the home page
      this.$router.push(`/home`)
    } else if (this.currentMembership.membershipStatus === MembershipStatus.Pending) {
      // 2. If user has a pending account status, take them to pending approval page (no matter where they are)
      this.$router.push(`/${Pages.PENDING_APPROVAL}/${this.currentAccountSettings.label}`)
    }
  }

  private async mounted (): Promise<void> {
    // set keycloak config file's location to the sbc-common-components
    await KeyCloakService.setKeycloakConfigUrl(`${process.env.VUE_APP_PATH}config/kc/keycloak.json`)
    this.showLoading = false

    EventBus.$on('show-toast', (eventInfo: Event) => {
      this.showNotification = true
      this.notificationText = eventInfo.message
      this.toastType = eventInfo.type
      this.toastTimeout = eventInfo.timeout
    })

    // Listen for event from signin component so it can initiate setup
    this.$root.$on('signin-complete', async (callback) => {
      await this.setup()
      callback()
    })
  }

  private destroyed () {
    this.$root.$off('signin-complete')
  }

  private async setup () {
    // Header added modules to store so can access mapped actions now
    if (this.$store.getters['auth/isAuthenticated']) {
      this.loadUserInfo()
      await this.syncUser()
      this.setupNavigationBar()
      await this.tokenService.init()
      this.tokenService.scheduleRefreshTimer()
    }
    this.$store.commit('loadComplete')
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
