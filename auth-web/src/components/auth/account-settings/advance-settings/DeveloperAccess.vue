<template>
  <v-container class="transaction-container">
    <div class="view-header flex-column mb-3">
      <h2
        class="view-header__title"
        data-test="account-settings-title"
      >
        Developer Access
      </h2>
      <p
        class="mt-3 payment-page-sub"
        v-html="$t('developerAccessSubtitle',{ url: APIDOCUMENTATION_URL } )"
      />
    </div>
    <RedirectUrls v-if="!isAccountLinkingDisabled" />
    <ExistingAPIKeys />
  </v-container>
</template>

<script lang="ts">

import { Component, Mixins } from 'vue-property-decorator'

import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import ConfigHelper from '@/util/config-helper'
import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'
import RedirectUrls from '@/components/auth/account-settings/advance-settings/RedirectUrls.vue'
import { isAccountLinkingDisabled } from '@/util/vendor-connection-util'

@Component({
  components: {
    ExistingAPIKeys,
    RedirectUrls
  }
})
export default class DeveloperAccess extends Mixins(AccountChangeMixin) {
  APIDOCUMENTATION_URL = ConfigHelper.apiDocumentationUrl() || ''

  get isAccountLinkingDisabled (): boolean {
    return isAccountLinkingDisabled()
  }
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

</style>
