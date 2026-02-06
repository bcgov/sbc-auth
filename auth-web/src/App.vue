<template>
  <v-app id="app">
    <div
      ref="headerGroup"
      class="header-group"
    >
      <sbc-loader :show="showLoading" />
      <sbc-header
        :key="refreshKey"
        ref="header"
        class="flex-column"
        :in-auth="true"
        :show-product-selector="false"
        :show-login-menu="showLoginMenu"
        :redirect-on-logout="logoutUrl"
        @account-switch-started="startAccountSwitch"
        @account-switch-completed="completeAccountSwitch"
        @account-data-loaded="setup"
      >
        <template #login-button-text>
          Log in with BC Services Card
        </template>
      </sbc-header>
      <v-snackbar
        v-model="showNotification"
        bottom
        :color="toastType"
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
      <!-- Alert banner -->
      <v-alert
        v-if="bannerText"
        id="alert-banner"
        class="pa-0 ma-0"
        tile
      >
        <div class="banner-content d-flex align-center">
          <v-icon
            class="banner-icon"
            size="28"
          >
            mdi-information
          </v-icon>
          <div
            class="banner-text pl-2"
            v-html="bannerText"
          />
        </div>
      </v-alert>
      <BreadCrumb
        v-if="showNavigationBar"
        :breadcrumbs="breadcrumbs"
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
import { LDFlags, Pages } from '@/util/constants'
import { mapActions, mapState } from 'pinia'
import { useAppStore, useOrgStore, useUserStore } from '@/stores'
import { BreadCrumb } from '@bcrs-shared-components/bread-crumb'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
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
import { useAuthStore } from 'sbc-common-components/src/stores'

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
    ...mapState(useUserStore, ['currentUser'])
  },
  methods: {
    ...mapActions(useOrgStore, ['setCurrentOrganization']),
    ...mapActions(useUserStore, ['loadUserInfo']),
    ...mapActions(useAppStore, ['updateHeader', 'loadComplete'])
  }
})
export default class App extends Mixins(NextPageMixin) {
  private appStore = useAppStore()
  authStore = useAuthStore()
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
    // Dont show the login menu if the user is on login page
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

  get refreshKey () {
    return this.appStore.refreshKey
  }

  get isAuthenticated (): boolean {
    return this.authStore.isAuthenticated
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

    this.appStore.updateHeader()

    this.accountFreezeRedirect()
    this.accountPendingRedirect()
  }

  private async mounted (): Promise<void> {
    this.showLoading = false

    EventBus.$on('show-toast', (eventInfo: Event) => {
      this.showNotification = true
      this.notificationText = eventInfo.message
      this.toastType = eventInfo.type || 'primary'
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
    this.logoutUrl = ''
  }

  private destroyed () {
    this.$root.$off('signin-complete')
  }

  async setup (isSigninComplete?: boolean) {
    const authStore = useAuthStore()
    if (authStore.isAuthenticated) {
      try {
        if (!isSigninComplete) {
          await KeyCloakService.initializeToken()
        }
        this.loadUserInfo()
        await this.syncUser()
      } catch (e) {
        // eslint-disable-next-line no-console
        console.log('App.vue.setup Errors: ' + e)
        const userStore = useUserStore()
        await userStore.reset()
        this.appStore.loadComplete()
        this.$router.push('/home')
      }
    }
    this.appStore.loadComplete()
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

  #alert-banner {
    background-color: #fcba19 !important;
    border-color: #fcba19 !important;
    box-shadow: none !important;

    .banner-content {
      max-width: 1360px;
      margin: 0 auto;
      padding: 8px 16px;
    }

    .banner-icon {
      color: #212429 !important;
      flex-shrink: 0;
    }

    .banner-text {
      color: #212429;
      font-size: 0.875rem;
    }

    :deep(a) {
      color: #212429 !important;
    }
  }

</style>
