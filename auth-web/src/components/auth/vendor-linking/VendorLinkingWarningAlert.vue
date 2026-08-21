<template>
  <v-alert
    class="vendor-linking-warning-alert mb-6"
    icon="$error"
  >
    <div
      v-if="title"
      class="font-weight-bold mb-2"
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
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component
export default class VendorLinkingWarningAlert extends Vue {
  @Prop({ default: '' }) title: string
  @Prop({ required: true }) body: string
  @Prop({ default: '' }) note: string
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.vendor-linking-warning-alert {
  border-radius: 4px;
  border: 1px solid $BCgovGold5 !important;
  background: $BCgovGold0 !important;
  color: $gray7;
}

::v-deep .v-icon {
  color: $app-alert-orange !important;
}
</style>
