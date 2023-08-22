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
import CommonUtils from '@/util/common-util'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import SbcSignin from 'sbc-common-components/src/components/SbcSignin.vue'
import { mapActions } from 'pinia'
import { useUserStore } from '@/store/user'

@Component({
  methods: {
    ...mapActions(useUserStore, ['loadUserInfo', 'setRedirectAfterLoginUrl'])
  },
  components: {
    SbcSignin
  }
})
export default class Signin extends Mixins(NextPageMixin) {
  readonly setRedirectAfterLoginUrl!: (url: string) => void
  readonly loadUserInfo!: () => KCUserProfile

  @Prop({ default: 'bcsc' }) idpHint: string
  @Prop({ default: '' }) redirectUrl: string
  @Prop({ default: '' }) redirectUrlLoginFail: string

  async authenticationComplete () {
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
