<template>
  <sbc-signin
    :idp-hint="idpHint"
    :redirect-url-login-fail="redirectUrlLoginFail"
    @sync-user-profile-ready="authenticationComplete()"
  ></sbc-signin>
</template>
<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapGetters, mapMutations } from 'vuex'
import { AccountSettings } from '@/models/account-settings'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/NextPageMixin.vue'
import OrgModule from '@/store/modules/org'
import SbcSignin from 'sbc-common-components/src/components/SbcSignin.vue'
import { SessionStorageKeys } from '@/util/constants'
import { User } from '@/models/user'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapMutations('user', ['setRedirectAfterLoginUrl']),
    ...mapActions('user', ['loadUserInfo'])
  },
  components: {
    SbcSignin
  }
})
export default class Signin extends Mixins(NextPageMixin) {
  private readonly setRedirectAfterLoginUrl!: (url: string) => void
  private readonly loadUserInfo!: () => KCUserProfile

  @Prop({ default: 'bcsc' }) idpHint: string
  @Prop({ default: '' }) redirectUrl: string
  @Prop({ default: '' }) redirectUrlLoginFail: string

  private async authenticationComplete () {
    // Check if user is authenticated, and redirect according to specified redirect
    // or fallback to default route for their login source
    await this.syncUser()
    this.loadUserInfo()
    if (this.$store.getters['auth/isAuthenticated']) {
      this.$root.$emit('signin-complete')
      if (this.redirectUrl) {
        this.redirectTo(decodeURIComponent(CommonUtils.isUrl(this.redirectUrl) ? this.redirectUrl : `/${this.redirectUrl}`))
      } else {
        switch (this.idpHint) {
          case 'bcsc':
            this.redirectTo(this.getNextPageUrl())
            break
          case 'idir':
            this.redirectTo('/searchbusiness')
            break
          case 'bcros':
            this.redirectTo('/userprofileterms') // TEMP - need to check account and redirect based on role
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
