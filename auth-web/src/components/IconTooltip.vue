<template >
  <v-tooltip v-bind="location" color="grey darken-4"  >
    <template v-slot:activator="{ on }">
      <v-icon :color="colour" v-on="on" :style="iconStyling">{{ icon }}</v-icon>
    </template>
    <div
      class="py-2"
      :class="{'top-tooltip': location.top, 'bottom-tooltip': location.bot}"
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
        return { bot: true }
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
      border-color: transparent transparent var(--v-grey-darken4) transparent;
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
    border-color: transparent transparent var(--v-grey-darken4) transparent;
    transform: rotate(180deg);
  }

</style>
