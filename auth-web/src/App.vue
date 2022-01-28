<template>
  <v-app id="app">
    <div class="header-group" ref="headerGroup">
      <sbc-loader :show="showLoading" />
      <sbc-header
        :key="$store.state.refreshKey"
        :in-auth="true"
        :show-product-selector="false"
        :show-login-menu="showLoginMenu"
        @account-switch-started="startAccountSwitch"
        @account-switch-completed="completeAccountSwitch"
        @hook:mounted="setup"
        ref="header" :redirect-on-logout="logoutUrl">
        <template v-slot:login-button-text>
          Log in with BC Services Card
        </template>
      </sbc-header>
      <v-snackbar
        bottom
        color="primary"
        class="mb-6"
        v-model="showNotification"
        :timeout="toastTimeout"
      >
        <span v-html="notificationText"></span>
        <v-btn
          dark
          icon
          color="default"
          aria-label="Close Notification"
          title="Close Notification"
          @click="showNotification = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-snackbar>
      <BreadCrumb v-if="showNavigationBar" :breadcrumbs="breadcrumbs" />
      <pay-system-alert />
    </div>
    <div class="app-body">
      <router-view  />
    </div>
    <sbc-footer></sbc-footer>
  </v-app>
</template>

<script lang="ts">
import { AccessType, LoginSource, Pages, Permission, Role, SessionStorageKeys } from '@/util/constants'
import { Component, Mixins } from 'vue-property-decorator'
import { MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import AuthModule from 'sbc-common-components/src/store/modules/auth'
import { BreadCrumb } from '@bcrs-shared-components/bread-crumb'
import { BreadcrumbIF } from '@bcrs-shared-components/interfaces'
import BusinessModule from './store/modules/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import KeyCloakService from 'sbc-common-components/src/services/keycloak.services'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import PaySystemAlert from 'sbc-common-components/src/components/PaySystemAlert.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcLoader from 'sbc-common-components/src/components/SbcLoader.vue'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    BreadCrumb,
    SbcHeader,
    SbcFooter,
    SbcLoader,
    PaySystemAlert
  },
  computed: {
    ...mapState('org', [
      'currentAccountSettings',
      'permissions',
      'currentOrganization'
    ]),
    ...mapState('user', ['currentUser']),
    ...mapGetters('auth', ['isAuthenticated']),
    ...mapGetters('org', ['needMissingBusinessDetailsRedirect'])
  },
  methods: {
    ...mapMutations('org', ['setCurrentOrganization']),
    ...mapActions('user', ['loadUserInfo'])
  }
})
export default class App extends Mixins(NextPageMixin) {
  private authModule = getModule(AuthModule, this.$store)
  private businessStore = getModule(BusinessModule, this.$store)
  private readonly loadUserInfo!: () => KCUserProfile
  private showNotification = false
  private notificationText = ''
  private showLoading = true
  private toastType = 'primary'
  private toastTimeout = 6000
  private logoutUrl = ''
  private readonly needMissingBusinessDetailsRedirect!: boolean
  private currentOrganization: Organization

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

  /** The route breadcrumbs list. */
  get breadcrumbs (): Array<BreadcrumbIF> {
    const currentAccountId = this.currentOrganization?.id || ''
    const breadcrumb = this.$route?.meta?.breadcrumb || []
    // updating breadcrumb url with account id if its external URL
    const breadcrumbwithAccountId = breadcrumb.map(items => {
      const newItem = { ...items }
      if (newItem && newItem.href) {
        newItem.href = appendAccountId(items.href, currentAccountId)
      }
      return newItem
    })

    return [...(breadcrumbwithAccountId || [])]
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

    this.$store.commit('updateHeader')

    this.accountFreezeRedirect()

    // Some edge cases where user needs to be redirected based on their account status and current location
    if (this.needMissingBusinessDetailsRedirect) {
      this.$router.push(`/${Pages.UPDATE_ACCOUNT}`)
    } else if (this.currentMembership.membershipStatus === MembershipStatus.Active && this.$route.path.indexOf(Pages.PENDING_APPROVAL) > 0) {
      // 1. If user was in a pending approval page and switched to an active account, take them to the home page
      this.$router.push(`/home`)
    } else if (this.currentMembership.membershipStatus === MembershipStatus.Pending) {
      const label = encodeURIComponent(btoa(this.currentAccountSettings?.label))
      // 2. If user has a pending account status, take them to pending approval page (no matter where they are)
      this.$router.push(`/${Pages.PENDING_APPROVAL}/${label}`)
    }
  }

  private async created () {
    // If session is synced, then sync user details
    if (ConfigHelper.getFromSession(SessionStorageKeys.SessionSynced) === 'true' && !CommonUtils.isSigningIn() && !CommonUtils.isSigningOut()) {
      this.loadUserInfo()
      await this.syncUser()
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
    this.logoutUrl = (this.$store.getters['auth/currentLoginSource'] === LoginSource.BCROS) ? ConfigHelper.getBcrosURL() : ''
  }

  private destroyed () {
    this.$root.$off('signin-complete')
  }

  private async setup (isSigninComplete?: boolean) {
    // Header added modules to store so can access mapped actions now
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
        this.$store.dispatch('user/reset')
        this.$store.commit('loadComplete')
        this.$router.push('/home')
      }
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
