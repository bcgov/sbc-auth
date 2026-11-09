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
        data-test="developer-access-subtitle"
        v-html="$t(subtitleKey, { url: APIDOCUMENTATION_URL })"
      />
    </div>
    <ExistingAPIKeys />
    <RedirectUrls v-if="!isAccountLinkingDisabled" />
  </v-container>
</template>

<script lang="ts">

import { Component, Mixins } from 'vue-property-decorator'

import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { ApiKeyEnvironment } from '@/models/Organization'
import ConfigHelper from '@/util/config-helper'
import ExistingAPIKeys from '@/components/auth/account-settings/advance-settings/ExistingAPIKeys.vue'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import RedirectUrls from '@/components/auth/account-settings/advance-settings/RedirectUrls.vue'
import { State } from 'pinia-class'
import { isAccountLinkingDisabled } from '@/util/vendor-connection-util'
import { useOrgStore } from '@/stores/org'

const SUBTITLE_KEYS: Record<ApiKeyEnvironment, string> = {
  prod: 'developerAccessSubtitleProd',
  sandbox: 'developerAccessSubtitleSandbox'
}

@Component({
  components: {
    ExistingAPIKeys,
    RedirectUrls
  }
})
export default class DeveloperAccess extends Mixins(AccountChangeMixin) {
  APIDOCUMENTATION_URL = ConfigHelper.apiDocumentationUrl() || ''

  // set in the store when the API keys are loaded
  @State(useOrgStore) readonly apiKeysEnvironment!: ApiKeyEnvironment | ''

  get enableCreateApiKey (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableCreateApiKey)
  }

  // the legacy subtitle is used until the env is known (or if it fails to load)
  get subtitleKey (): string {
    return (this.enableCreateApiKey && SUBTITLE_KEYS[this.apiKeysEnvironment]) || 'developerAccessSubtitle'
  }

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
