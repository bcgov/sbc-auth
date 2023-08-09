<template>
  <v-dialog
    :persistent="isPersistent"
    :fullscreen="fullscreenOnMobile"
    :scrollable="isScrollable"
    :content-class="dialogClass"
    :max-width="maxWidth"
    v-model="isOpen"
    @keydown.esc="close()"
  >
    <v-card>
      <!-- title -->
      <v-card-title data-test="dialog-header">
        <!-- optional check icon -->
        <slot v-if="showIcon" name="icon">
          <v-icon large color="success">mdi-check</v-icon>
        </slot>

        <span>
          <slot name="title">{{ title }}</slot>
        </span>

        <!-- optional close button -->
        <v-btn v-if="showCloseIcon" icon @click="close()">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- text -->
      <v-card-text>
        <slot name="text">
          <div v-html="text"></div>
        </slot>
      </v-card-text>

      <!-- actions -->
      <v-card-actions v-if="showActions">
        <slot name="actions">
          <v-btn large color="success" @click="close()" data-test="dialog-ok-button">
            <span>OK</span>
          </v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class ModalDialog extends Vue {
  protected isOpen = false

  @Prop({ default: '' }) readonly title: string
  @Prop({ default: '' }) readonly text: string
  @Prop({ default: true }) readonly showIcon: boolean
  @Prop({ default: true }) readonly showActions: boolean
  @Prop({ default: false }) readonly isPersistent: boolean
  @Prop({ default: false }) readonly fullscreenOnMobile: boolean
  @Prop({ default: false }) readonly isScrollable: boolean
  @Prop({ default: '' }) readonly dialogClass: string
  @Prop({ default: '' }) readonly maxWidth: string
  @Prop({ default: false }) readonly showCloseIcon: boolean

  public open () {
    this.isOpen = true
  }

  public close () {
    this.isOpen = false
  }
}
</script>

<style lang="scss" scoped>
  // Notify Dialog Variant
  // Vertical stacked title container (icon w/ text)
  // Center-aligned text throughout
  .notify-dialog .v-card__title {
    flex-direction: column;

    ::v-deep i {
      margin-top: 1rem;
      margin-bottom: 1rem;
    }
  }

  .notify-dialog .v-card__text {
    text-align: center;
  }

  .notify-dialog .v-card__actions {
    justify-content: center;
    padding: 1.5rem;
  }
  // Info Dialog Variant
 .info-dialog .v-card__actions {
    justify-content: center;
    padding: 1.5rem;
  }
</style>
