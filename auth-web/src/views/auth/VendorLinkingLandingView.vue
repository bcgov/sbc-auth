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
  <VendorLinkingLoginCard
    v-else
    :vendor-account-id="vendorAccountId"
    :return-url="returnUrl"
  />
</template>

<script lang="ts">
import { Pages, SessionStorageKeys } from '@/util/constants'
import { computed, defineComponent, getCurrentInstance, onMounted } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import VendorLinkingLoginCard from '@/components/auth/vendor-linking/VendorLinkingLoginCard.vue'
import { isValidVendorLinkingParams } from '@/util/vendor-connection-util'

export default defineComponent({
  name: 'VendorLinkingLandingView',
  components: {
    VendorLinkingLoginCard
  },
  props: {
    vendorAccountId: {
      type: String,
      default: ''
    },
    returnUrl: {
      type: String,
      default: ''
    }
  },
  setup (props) {
    const instance = getCurrentInstance()

    const paramsInvalid = computed(() => !isValidVendorLinkingParams(props.vendorAccountId, props.returnUrl))

    onMounted(() => {
      if (!paramsInvalid.value && ConfigHelper.getFromSession(SessionStorageKeys.KeyCloakToken)) {
        instance.proxy.$router.push({
          path: `/${Pages.VENDOR_LINKING}/confirm`,
          query: { vendorAccountId: props.vendorAccountId, returnUrl: props.returnUrl }
        })
      }
    })

    return {
      paramsInvalid
    }
  }
})
</script>
