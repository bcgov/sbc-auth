<template>
  <v-alert
    class="vendor-linking-account-select-alert mb-6"
    type="warning"
    prominent
    data-test="vendor-linking-account-select-alert"
  >
    {{ $t('vendorLinkingAccountSelectAlert') }}
  </v-alert>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'VendorLinkingAccountSelectAlert'
})
</script>
