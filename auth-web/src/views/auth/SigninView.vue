<template>
  <sbc-signin :idp-hint="idpHint"></sbc-signin>
</template>
<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import SbcSignin from 'sbc-common-components/src/components/SbcSignin.vue'
import { User } from '@/models/user'
import { UserInfo } from 'sbc-common-components/src/models/userInfo'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapMutations('org', ['setCurrentAccountSettings']),
    ...mapActions('user',
      [
        'loadUserInfo',
        'syncUserProfile'
      ]
    ),
    ...mapActions('org', ['syncOrganization', 'syncMembership'])
  },
  components: {
    SbcSignin
  }
})
export default class Signin extends Mixins(NextPageMixin) {
  private userStore = getModule(UserModule, this.$store)
  private orgStore = getModule(OrgModule, this.$store)
  private readonly syncUserProfile!: () => User
  private readonly syncOrganization!: (currentAccount: string) => Promise<Organization>
  private readonly syncMembership!: (currentAccount: string) => Promise<Member>
  private readonly setCurrentAccountSettings!: (accountSettings: AccountSettings) => void
  private readonly loadUserInfo!: () => UserInfo

  @Prop({ default: 'bcsc' }) idpHint: string
  @Prop() redirectUrl: string

  private async mounted () {
    // refreshing the header once the token is receieved from the common component
    this.$root.$on('keycloakSessionReady', async () => {
      this.$store.commit('updateHeader')
      this.loadUserInfo()
    })
    // Set up a listener for the account sync event from SbcHeader
    // This event signals that the current account has been loaded, and we are ready to sync against it
    this.$root.$on('accountSyncReady', async (currentAccount: AccountSettings) => {
      if (currentAccount) {
        this.setCurrentAccountSettings(currentAccount)
        const membership = await this.syncMembership(currentAccount.id)
        if (membership.membershipStatus === MembershipStatus.Active) {
          await this.syncOrganization(currentAccount.id)
        }
      }
      if (this.$route.name === 'signin' || this.$route.name === 'signin-redirect') {
        this.redirectToNext()
      }
    })

    // sync user profile once the signin completed from sbc-common-component
    this.$root.$on('syncUserProfileReady', async () => {
      await this.syncUserProfile()
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
