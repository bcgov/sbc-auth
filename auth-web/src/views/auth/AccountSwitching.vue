<template>
  <div><sbc-loader :show="showLoading" /></div>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import SbcLoader from 'sbc-common-components/src/components/SbcLoader.vue'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({
  components: {
    SbcLoader
  }
})
export default class AccountSwitching extends Mixins(NextPageMixin) {
  private dashboardUrl = `${ConfigHelper.getRegistryHomeURL()}dashboard`
  public showLoading = true

  private async completeAccountSwitch () {
    this.accountFreezeRedirect()
    this.accountPendingRedirect()
  }

  private async created () {
    // before coming to this page App.vue will load and loadUserInfo() will  get called
    await this.syncUser()
    // check all the coindtions before redirect
    await this.completeAccountSwitch()
    // if any pending redirect , prevent redirection to redirectToUrl
    if (!this.anyPendingRedirect) {
      // redirect URL is given from common component.
      const redirectToUrl:any = this.$route?.query?.redirectToUrl
      const accountId:any = this.$route?.query?.accountid
      // check for allowed redirect to determine whether need to redirect back to that page or dashboard
      // list of Allowed URLs
      const allowedRedirectURls = ConfigHelper.getAllowedUrlForRedirectToSamePage()
      // default redirect to dashboard
      let redirect = this.dashboardUrl

      if (allowedRedirectURls.indexOf(CommonUtils.trimTrailingSlashURL(redirectToUrl)) > -1) {
        redirect = redirectToUrl
      }

      // if no redirect URL or not valid URL, redirect back to dashboard
      redirect = CommonUtils.isUrl(redirect) ? redirect : this.dashboardUrl
      // if we have account id in URL set that as account id inredirect URL else it will get from session
      redirect = appendAccountId(redirect, accountId)

      // redirect to new URL, its outside sbc auth so using window
      window.location.replace(redirect)
    }
    this.showLoading = false
  }
}

</script>
