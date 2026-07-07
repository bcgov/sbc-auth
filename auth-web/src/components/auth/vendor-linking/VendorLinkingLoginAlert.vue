<template>
  <v-alert
    class="vendor-linking-login-alert custom-warning mb-6"
    type="warning"
    icon="$error"
    data-test="vendor-linking-login-alert"
  >
    <div class="font-weight-bold mb-2">
      {{ $t('vendorLinkingLoginAlertTitle') }}
    </div>
    <div>{{ $t('vendorLinkingLoginAlertBody') }}</div>
    <div class="mt-3">
      <strong>Note:</strong> {{ $t('vendorLinkingLoginAlertNote') }}
    </div>
  </v-alert>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'VendorLinkingLoginAlert'
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.custom-warning {
  border-radius: 4px;
  border: 1px solid $BCgovGold5 !important;
  background: $BCgovGold0 !important;
  color: $gray7;
}

::v-deep .v-icon {
  color: $app-alert-orange !important;
}
</style>
