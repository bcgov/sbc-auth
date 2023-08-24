<template>
  <v-tooltip v-bind="location">
    <template #activator="{ on }">
      <v-icon
        :color="colour"
        :style="iconStyling"
        v-on="on"
      >
        {{ icon }}
      </v-icon>
    </template>
    <div
      class="py-2"
      :class="{'top-tooltip': location.top, 'bottom-tooltip': location.bottom}"
      :style="{ 'max-width': maxWidth }"
    >
      <slot />
    </div>
  </v-tooltip>
</template>
<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'IconTooltip',
  props: {
    icon: {
      type: String,
      required: true
    },
    iconStyling: {
      type: Object,
      default: () => ({})
    },
    maxWidth: {
      type: String,
      default: '300px'
    },
    colour: {
      type: String,
      default: 'primary'
    },
    location: {
      type: Object,
      default () {
        return { bottom: true }
      }
    }
  }
})
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
.bottom-tooltip:before {
  content: ' ';
  position: absolute;
  top: -20px;
  left: 50%;
  margin-left: -10px;
  width: 20px;
  height: 20px;
  border-width: 10px 10px 10px 10px;
  border-style: solid;
  border-color: transparent transparent RGBA(73, 80, 87, .95) transparent;
}

.top-tooltip:after {
  content: ' ';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -10px;
  width: 20px;
  height: 20px;
  border-width: 10px 10px 10px 10px;
  border-style: solid;
  border-color: transparent transparent RGBA(73, 80, 87, .95) transparent;
  transform: rotate(180deg);
}
.v-tooltip__content {
  background-color: RGBA(73, 80, 87, .95);
}

</style>
