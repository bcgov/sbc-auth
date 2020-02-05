<template>
  <div>
    <v-fade-transition>
      <div class="loading-container" v-if="isLoading">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>
  </div>
</template>
<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { KeycloakError, KeycloakPromise } from 'keycloak-js'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import { SessionStorageKeys } from '@/util/constants'
import TokenService from 'sbc-common-components/src/services/token.services'
import { User } from '@/models/user'
import { UserInfo } from '@/models/userInfo'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapActions('user',
      [
        'initKeycloak',
        'initializeSession',
        'syncUserProfile'
      ]
    ),
    ...mapActions('org', ['syncOrganization'])
  }
})
export default class Signin extends Mixins(NextPageMixin) {
  private userStore = getModule(UserModule, this.$store)
  private orgStore = getModule(OrgModule, this.$store)
  private isLoading = true
  private readonly initKeycloak!: (idpHint: string) => Promise<KeycloakPromise<boolean, KeycloakError>>
  private readonly initializeSession!: () => UserInfo
  private readonly syncUserProfile!: () => User
  private readonly syncOrganization!: (currentAccount: string) => Promise<void>

  @Prop({ default: 'bcsc' }) idpHint: string
  @Prop() redirectUrl: string

  private async mounted () {
    const kcInit = await this.userStore.initKeycloak(this.idpHint)
    kcInit.success(async authenticated => {
      if (authenticated) {
        this.initializeSession()
        this.$store.commit('updateHeader') // Force a remount of header so it can retrieve account (now that is has token)
        // Make a POST to the users endpoint if it's bcsc (only need for BCSC)
        if (this.idpHint === 'bcsc') {
          await this.syncUserProfile()
          // eslint-disable-next-line no-console
          console.info('[SignIn.vue]Logged in User.Starting refreshTimer')
          var self = this
          let tokenService = new TokenService()
          tokenService.initUsingUrl(`${process.env.VUE_APP_PATH}config/kc/keycloak.json`).then(function (success) {
            tokenService.scheduleRefreshTimer()
          })
        }
        // Set up a listener for the account sync event from SbcHeader
        // This event signals that the current account has been loaded, and we are ready to sync against it
        this.$root.$once('accountSyncReady', async (accountId: string) => {
          const currentAccountId = ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccountId) || null
          if (currentAccountId) {
            await this.syncOrganization(currentAccountId)
          }
          this.redirectToNext()
        })
      }
    })
  }

  redirectToNext () {
    // If a redirect url is given, redirect to that page else continue to dashboard or userprofile
    if (this.redirectUrl) {
      if (CommonUtils.isUrl(this.redirectUrl)) {
        window.location.href = decodeURIComponent(this.redirectUrl)
      } else {
        this.$router.push('/' + this.redirectUrl)
      }
    } else {
      if (this.idpHint === 'idir') {
        this.$router.push('/searchbusiness')
      } else {
        this.$router.push(this.getNextPageUrl())
      }
    }
  }

  redirectToLogin () {
    this.$router.push('/')
  }
}
</script>
