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
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class CardHeader extends Vue {
  @Prop({ default: 'Paused' }) readonly badgeText!: boolean
  @Prop({ default: null }) readonly icon!: string
  @Prop({ default: null }) readonly label!: string
  @Prop({ default: false }) readonly showBadge!: boolean
}
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
  background-color: $BCgovPausedWarning !important;
}

// Vuetify override for the sizes of the v-chip
.v-chip.v-size--small {
  font-size: 12px;
  height: 19px;
}
</style>
