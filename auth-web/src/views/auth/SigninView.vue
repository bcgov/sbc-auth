<template>
  <sbc-signin
    :idp-hint="idpHint"
    :in-auth="true"
    :redirect-url-login-fail="redirectUrlLoginFail"
    @sync-user-profile-ready="authenticationComplete"
  />
</template>
<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapMutations } from 'vuex'
import CommonUtils from '@/util/common-util'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
import OrgModule from '@/store/modules/org'
import SbcSignin from 'sbc-common-components/src/components/SbcSignin.vue'
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
import UserModule from '@/store/modules/user'

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
    await this.loadUserInfo()
    // Check if user is authenticated, and redirect according to specified redirect
    // or fallback to default route for their login source
    if (this.$store.getters['auth/isAuthenticated']) {
      this.$root.$emit('signin-complete', () => {
        if (this.redirectUrl) {
          if (this.redirectUrl.startsWith('/')) {
            this.redirectTo(this.redirectUrl)
          } else {
            this.redirectTo(decodeURIComponent(CommonUtils.isUrl(this.redirectUrl)
              ? this.redirectUrl : `/${this.redirectUrl}`))
          }
        } else {
          this.redirectTo(this.getNextPageUrl())
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
