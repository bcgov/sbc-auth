<template>
  <v-container
    v-if="paramsInvalid"
    class="view-container"
  >
    <v-row justify="center">
      <v-col
        cols="12"
        lg="8"
        class="text-center"
      >
        <v-icon
          size="48"
          color="error"
          class="mb-6"
        >
          mdi-alert-circle-outline
        </v-icon>
        <h1>Unable to Connect</h1>
        <p class="mt-8 mb-10">
          This link is missing required information. Please return to the service provider
          and try again.
        </p>
      </v-col>
    </v-row>
  </v-container>
  <vendor-linking-login-card
    v-else
    :vendor-account-id="vendorAccountId"
    :return-url="returnUrl"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Pages, SessionStorageKeys } from '@/util/constants'
import ConfigHelper from '@/util/config-helper'
import VendorLinkingLoginCard from '@/components/auth/vendor-linking/VendorLinkingLoginCard.vue'
import { isValidVendorLinkingParams } from '@/util/vendor-connection-util'

@Component({
  components: {
    VendorLinkingLoginCard
  }
})
export default class VendorLinkingLandingView extends Vue {
  @Prop({ default: '' }) vendorAccountId: string
  @Prop({ default: '' }) returnUrl: string

  get paramsInvalid (): boolean {
    return !isValidVendorLinkingParams(this.vendorAccountId, this.returnUrl)
  }

  private mounted () {
    if (!this.paramsInvalid && ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)) {
      this.$router.push({
        path: `/${Pages.VENDOR_LINKING}/confirm`,
        query: { vendorAccountId: this.vendorAccountId, returnUrl: this.returnUrl }
      })
    }
  }
}
</script>
