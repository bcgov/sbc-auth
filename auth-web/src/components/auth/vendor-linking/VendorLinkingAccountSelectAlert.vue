<template>
  <v-alert
    class="vendor-linking-account-select-alert custom-warning mb-6"
    type="warning"
    icon="$error"
    data-test="vendor-linking-account-select-alert"
  >
    <div>{{ $t('vendorLinkingAccountSelectAlertBody') }}</div>
    <div class="mt-1">
      <strong>Note:</strong> {{ $t('vendorLinkingAccountSelectAlertNote') }}
    </div>
  </v-alert>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'VendorLinkingAccountSelectAlert'
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
