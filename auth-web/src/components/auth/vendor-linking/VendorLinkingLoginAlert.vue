<template>
  <v-alert
    class="vendor-linking-login-alert mb-6"
    type="warning"
    prominent
    data-test="vendor-linking-login-alert"
  >
    <div class="font-weight-bold mb-2">
      {{ $t('vendorLinkingLoginAlertTitle') }}
    </div>
    <div>{{ $t('vendorLinkingLoginAlertBody') }}</div>
    <div class="mt-3">
      {{ $t('vendorLinkingLoginAlertNote') }}
    </div>
  </v-alert>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'VendorLinkingLoginAlert'
})
</script>
