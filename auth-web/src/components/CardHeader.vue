<template>
  <header class="v-card-header rounded-t">
    <v-icon
      v-if="icon"
      color="bcgovblue2"
    >
      {{ icon }}
    </v-icon>
    <label
      v-if="label"
      class="v-card-label"
      :class="{ 'pl-2': !!icon }"
    >
      {{ label }}
    </label>
    <v-chip
      v-if="showBadge"
      class="primary pointer-events-none ml-2 mt-1"
      small
      label
      text-color="white"
    >
      {{ badgeText }}
    </v-chip>
  </header>
</template>

<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'CardHeader',
  props: {
    badgeText: { type: String, default: 'Paused' },
    icon: { type: String, default: null },
    label: { type: String, default: null },
    showBadge: { type: Boolean, default: false }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.v-card-header {
  display: flex;
  background-color: $BCgovBlue5O;
  padding: 1.25rem;

  .v-card-label {
    font-weight: bold;
    color: $gray9;
  }
}

// Vuetify override for the color of the v-chip
.v-application .primary {
  background-color: $BCgovOrangeWarning !important;
}

// Vuetify override for the sizes of the v-chip
.v-chip.v-size--small {
  font-size: $px-12;
  height: 19px;
}
</style>
