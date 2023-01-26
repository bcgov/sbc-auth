<template>
  <v-tooltip bottom color="grey darken-4">
    <template v-slot:activator="{ on }">
      <v-icon color="primary" v-on="on">{{ icon }}</v-icon>
    </template>
    <div class="py-2" v-html="text" :style="{ 'max-width': maxWidth }" />
  </v-tooltip>
</template>
<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'IconTooltip',
  props: {
    icon: String,
    maxWidth: String,
    text: String
  }
})
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
.v-tooltip__content:before {
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
</style>
