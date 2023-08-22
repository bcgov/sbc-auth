<template>
  <div>
    <div
      class="help-btn top mb-8"
      @click="helpToggle = !helpToggle"
    >
      <v-icon color="primary">
        mdi-help-circle-outline
      </v-icon>
      <span
        v-if="!helpToggle"
        class="pl-2"
      >Help with Starting and Managing a Business</span>
      <span
        v-else
        class="pl-2"
      >Hide Help</span>
    </div>
    <v-expand-transition>
      <div
        v-show="helpToggle"
        class="help-section pa-4 my-3 mb-8"
      >
        <slot name="content" />
        <div
          class="help-btn bottom text-right d-flex"
          @click="helpToggle = !helpToggle"
        >
          Hide Help
        </div>
      </div>
    </v-expand-transition>
  </div>
</template>

<script lang="ts">
import { ref } from '@vue/composition-api'

export default {
  setup () {
    const helpToggle = ref(false)
    return { helpToggle }
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

      .help-btn {
        cursor: pointer;
        color: $app-blue;
        vertical-align: middle;
      }

      .v-icon {
        margin-top: -3px;
      }

      .help-section {
        border-top: 1px dashed $gray6;
        border-bottom: 1px dashed $gray6;
      }

      .help-btn.bottom {
        font-size: $app-blue;
        text-decoration: underline;
        display: flex;
        direction: rtl;
      }
</style>
