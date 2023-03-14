<template >
  <v-tooltip v-bind="location">
    <template v-slot:activator="{ on }">
      <v-icon :color="colour" v-on="on" :style="iconStyling">{{ icon }}</v-icon>
    </template>
    <div
      class="py-2"
      :class="{'top-tooltip': location.top, 'bottom-tooltip': location.bottom}"
      :style="{ 'max-width': maxWidth }"
    >
      <slot></slot>
    </div>
  </v-tooltip>
</template>
<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'IconTooltip',
  props: {
    icon: String,
    iconStyling: Object,
    maxWidth: String,
    colour: {
      type: String,
      default: 'primary'
    },
    location: {
      type: Object,
      default (rawProps) {
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
