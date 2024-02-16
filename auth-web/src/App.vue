<template>
  <v-app id="app">
    <div
      ref="headerGroup"
      class="header-group"
    >
      <sbc-loader :show="showLoading" />
      <sbc-header
        :key="$store.state.refreshKey"
        ref="header"
        class="flex-column"
        :in-auth="true"
        :show-product-selector="false"
        :show-login-menu="showLoginMenu"
        :redirect-on-logout="logoutUrl"
        @account-switch-started="startAccountSwitch"
        @account-switch-completed="completeAccountSwitch"
        @hook:mounted="setup"
      >
        <template #login-button-text>
          Log in with BC Services Card
        </template>
      </sbc-header>
      <v-snackbar
        v-model="showNotification"
        bottom
        color="primary"
        class="mb-6"
        :timeout="toastTimeout"
      >
        <span v-html="notificationText" />
        <v-btn
          dark
          icon
          color="default"
          aria-label="Close Notification"
          title="Close Notification"
          @click="showNotification = false"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-snackbar>
      <BreadCrumb
        v-if="showNavigationBar"
        :breadcrumbs="breadcrumbs"
      />

      <!-- Alert banner -->
      <v-alert
        v-if="bannerText"
        tile
        dense
        type="warning"
        class="mb-0 text-center colour-dk-text"
        v-html="bannerText"
      />
    </div>
    <div class="app-body">
      <router-view />
    </div>
    <sbc-footer :aboutText="aboutText" />
  </v-app>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { LDFlags, LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import { mapActions, mapState } from 'pinia'
import { useOrgStore, useUserStore } from '@/stores'
import AuthModule from 'sbc-common-components/src/store/modules/auth'
import { BreadCrumb } from '@bcrs-shared-components/bread-crumb'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcLoader from 'sbc-common-components/src/components/SbcLoader.vue'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'
import { getModule } from 'vuex-module-decorators'
import { mapGetters } from 'vuex'

@Component({
  components: {
    BreadCrumb,
    SbcHeader,
    SbcFooter,
    SbcLoader
  },
  computed: {
    ...mapState(useOrgStore, [
      'currentAccountSettings',
      'permissions'
    ]),
    ...mapState(useUserStore, ['currentUser']),
    ...mapGetters('auth', ['isAuthenticated'])
  },
  methods: {
    ...mapActions(useOrgStore, ['setCurrentOrganization']),
    ...mapActions(useUserStore, ['loadUserInfo'])
  }
})
export default class App extends Mixins(NextPageMixin) {
  // Remove these with sbc-common-components and Vue3 upgrade.
  private authModule = getModule(AuthModule, this.$store)
  private readonly loadUserInfo!: () => KCUserProfile
  showNotification = false
  notificationText = ''
  showLoading = true
  toastType = 'primary'
  toastTimeout = 6000
  logoutUrl = ''

  $refs: {
    header: SbcHeader
  }

  get showNavigationBar (): boolean {
    return this.$route.meta.showNavBar
  }

  get showLoginMenu (): boolean {
    // Don't show the login menu if the user is on login page
    return this.$route.path !== `/${Pages.LOGIN}`
  }

  get bannerText (): string | null {
    const bannerText: string = LaunchDarklyService.getFlag(LDFlags.BannerText)
    // remove spaces so that " " becomes falsy
    return bannerText?.trim()
  }

  /** The route breadcrumbs list. */
  get breadcrumbs (): Array<BreadcrumbIF> {
    const currentAccountId = this.currentOrganization?.id || ''
    const breadcrumb = this.$route?.meta?.breadcrumb || []
    // updating breadcrumb url with account id if its external URL
    const breadcrumbwithAccountId = breadcrumb.map(items => {
      const newItem = { ...items }
      if (newItem && newItem.href) {
        newItem.href = appendAccountId(items.href, currentAccountId.toString())
      }
      return newItem
    })

    return [...(breadcrumbwithAccountId || [])]
  }

  /** The About text. */
  get aboutText (): string {
    return import.meta.env.ABOUT_TEXT
  }

  startAccountSwitch () {
    this.showLoading = true
  }

  async completeAccountSwitch () {
    await this.syncUser()
    this.showLoading = false
    this.toastType = 'primary'
    this.notificationText = `Switched to account '${this.currentAccountSettings.label}'`
    this.showNotification = true

    // Remove Vuex with Vue 3
    this.$store.commit('updateHeader')

    this.accountFreezeRedirect()
    this.accountPendingRedirect()
  }

  private async created () {
    // If session is synced, then sync user details
    if (ConfigHelper.getFromSession(SessionStorageKeys.SessionSynced) === 'true' && !CommonUtils.isSigningIn() && !CommonUtils.isSigningOut()) {
      this.loadUserInfo()
      await this.syncUser()
      // Remove Vuex with Vue 3
      this.$store.commit('loadComplete')
    }
  }

  private async mounted (): Promise<void> {
    this.showLoading = false

    EventBus.$on('show-toast', (eventInfo: Event) => {
      this.showNotification = true
      this.notificationText = eventInfo.message
      this.toastType = eventInfo.type
      this.toastTimeout = eventInfo.timeout
    })

    // set logout url after refresh
    this.setLogOutUrl()

    // Listen for event from signin component so it can initiate setup
    this.$root.$on('signin-complete', async (callback) => {
      await this.setup(true)
      // set logout url on first time sigin
      this.setLogOutUrl()
      callback()
    })
  }

  private setLogOutUrl () {
    // Auth store, still exists in sbc-common-components v2, uses pinia in Vue 3 version.
    // Remove Vuex with Vue 3
    this.logoutUrl = (this.$store.getters['auth/currentLoginSource'] === LoginSource.BCROS) ? ConfigHelper.getBcrosURL() : ''
  }

  private destroyed () {
    this.$root.$off('signin-complete')
  }

  async setup (isSigninComplete?: boolean) {
    // Header added modules to store so can access mapped actions now
    // Remove Vuex with Vue 3
    if (this.$store.getters['auth/isAuthenticated']) {
      try {
        if (!isSigninComplete) {
          await KeyCloakService.initializeToken(this.$store)
        }
        this.loadUserInfo()
        await this.syncUser()
      } catch (e) {
        // eslint-disable-next-line no-console
        console.log('App.vue.setup Error: ' + e)
        const userStore = useUserStore()
        await userStore.reset()
        // Remove Vuex with Vue 3
        this.$store.commit('loadComplete')
        this.$router.push('/home')
      }
    }
    // Remove Vuex with Vue 3
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
