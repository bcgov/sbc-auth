<template>
  <div>
    <div
      class="help-btn top mb-8"
    >
      <v-icon color="primary">
        mdi-help-circle-outline
      </v-icon>
      <span
        class="pl-2 help-label"
        @click="helpToggle = !helpToggle"
      >{{ !helpToggle ? helpLabel : 'Hide Help' }}</span>
    </div>

    <v-expand-transition>
      <div
        v-show="helpToggle"
        class="help-section pa-6 my-3 mb-8"
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
import { Component, Prop } from 'vue-property-decorator'
import Vue from 'vue'

@Component({})
export default class ExpandableHelp extends Vue {
  private helpToggle = false

  @Prop({ default: 'Show Help' }) readonly helpLabel!: string
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.help-label {
  cursor: pointer;
}

.help-btn {
  color: $app-blue;
}

.v-icon {
  margin-top: -3px;
}

.help-section {
  border-top: 1px dashed $gray7;
  border-bottom: 1px dashed $gray7;
}

.help-btn.bottom {
  font-size: $app-blue;
  text-decoration: underline;
  display: flex;
  direction: rtl;
}
</style>
