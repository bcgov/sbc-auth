<template>
  <sbc-signin
    :idp-hint="idpHint"
    :redirect-url-login-fail="redirectUrlLoginFail"
    @keycloak-session-ready="loadUserInfo()"
    @sync-user-profile-ready="syncUser()"
  ></sbc-signin>
</template>
<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import SbcSignin from 'sbc-common-components/src/components/SbcSignin.vue'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapMutations('org', ['setCurrentAccountSettings']),
    ...mapMutations('user', ['setRedirectAfterLoginUrl']),
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
  private readonly setRedirectAfterLoginUrl!: (url: string) => void
  private readonly loadUserInfo!: () => KCUserProfile

  @Prop({ default: 'bcsc' }) idpHint: string
  @Prop({ default: '' }) redirectUrl: string
  @Prop({ default: '' }) redirectUrlLoginFail: string

  private async mounted () {
    if (this.redirectUrl) {
      this.setRedirectAfterLoginUrl(decodeURIComponent(this.redirectUrl))
    } else {
      this.setRedirectAfterLoginUrl(this.idpHint === 'idir' ? 'searchbusiness' : '')
    }
  }

  private async syncUser () {
    await this.syncUserProfile()
    this.$store.commit('updateHeader')
  }
}
</script>

<style lang="scss" scoped>
</style>
