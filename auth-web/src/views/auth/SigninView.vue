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
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import { SessionStorageKeys } from '@/util/constants'
import TokenService from 'sbc-common-components/src/services/token.services'
import { User } from '@/models/user'
import { UserInfo } from '@/models/userInfo'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapMutations('org', ['setCurrentAccountSettings']),
    ...mapMutations('user', ['setRedirectAfterLoginUrl']),
    ...mapActions('user',
      [
        'initKeycloak',
        'initializeSession',
        'syncUserProfile'
      ]
    ),
    ...mapActions('org', ['syncOrganization', 'syncMembership'])
  }
})
export default class Signin extends Mixins(NextPageMixin) {
  private userStore = getModule(UserModule, this.$store)
  private orgStore = getModule(OrgModule, this.$store)
  private isLoading = true
  private readonly initKeycloak!: (idpHint: string) => Promise<KeycloakPromise<boolean, KeycloakError>>
  private readonly initializeSession!: () => UserInfo
  private readonly syncUserProfile!: () => User
  private readonly syncOrganization!: (currentAccount: string) => Promise<Organization>
  private readonly syncMembership!: (currentAccount: string) => Promise<Member>
  private readonly setCurrentAccountSettings!: (accountSettings: AccountSettings) => void
  private readonly setRedirectAfterLoginUrl!: (url: string) => void

  @Prop({ default: 'bcsc' }) idpHint: string
  @Prop({ default: '' }) redirectUrl: string
  @Prop({ default: '' }) redirectUrlLoginFail: string

  private async mounted () {
    if (this.redirectUrl) {
      this.setRedirectAfterLoginUrl(decodeURIComponent(this.redirectUrl))
    } else {
      this.setRedirectAfterLoginUrl(this.idpHint === 'idir' ? 'searchbusiness' : '')
    }

    // Initialize keycloak session
    const kcInit = await this.userStore.initKeycloak(this.idpHint)
    await new Promise((resolve, reject) => {
      kcInit
        .success(async authenticated => {
          if (authenticated) {
            this.initializeSession()
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
            resolve()
          }
        })
        .error(() => {
          if (this.redirectUrlLoginFail) {
            window.location.assign(decodeURIComponent(this.redirectUrlLoginFail))
          }
        })
    })
    this.$store.commit('updateHeader') // Force a remount of header so it can retrieve account (now that is has token)
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 0;
    right: 0;
    left: 0;
    bottom: 0;
    z-index: 2;
    background: $gray2;
  }
</style>
