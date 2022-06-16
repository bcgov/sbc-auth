<template>
  <div><sbc-loader :show="showLoading" /></div>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
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
    const redirect:any = this.$route?.query?.redirectToUrl
    const accountId:any = this.$route?.query?.accountid
    // if no redirect URL redirect back to dashboard
    let redirectToUrl = redirect || this.dashboardUrl
    // if we have account id in URL set that as account id inredirect URL else it will get from session
    redirectToUrl = appendAccountId(redirectToUrl, accountId)

    window.location.replace(redirectToUrl)
    this.showLoading = false
  }
}

</script>
