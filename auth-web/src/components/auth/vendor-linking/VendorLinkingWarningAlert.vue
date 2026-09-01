<template>
  <v-alert
    class="vendor-linking-warning-alert mb-6"
    icon="$error"
  >
    <div
      v-if="title"
      class="vendor-linking-warning-alert-title font-weight-bold mb-2"
    >
      {{ title }}
    </div>
    <div>{{ body }}</div>
    <div
      v-if="note"
      class="mt-3"
    >
      <strong>Note:</strong> {{ note }}
    </div>
  </v-alert>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'VendorLinkingWarningAlert',
  props: {
    title: {
      type: String,
      default: ''
    },
    body: {
      type: String,
      required: true
    },
    note: {
      type: String,
      default: ''
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.vendor-linking-warning-alert {
  border-radius: 4px;
  border: 1px solid $BCgovGold5 !important;
  background: $BCgovGold0 !important;
  color: $gray7 !important;
}

.vendor-linking-warning-alert-title {
  color: $gray9 !important;
}

::v-deep .v-icon {
  color: $app-alert-orange !important;
}
</style>
