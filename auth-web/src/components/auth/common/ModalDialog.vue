<template>
  <v-dialog
    v-model="isOpen"
    :persistent="isPersistent"
    :fullscreen="fullscreenOnMobile"
    :scrollable="isScrollable"
    :content-class="dialogClass"
    :max-width="maxWidth"
    @keydown.esc="close()"
  >
    <v-card>
      <!-- title -->
      <v-card-title data-test="dialog-header">
        <!-- optional check icon -->
        <slot
          v-if="showIcon"
          name="icon"
        >
          <v-icon
            large
            color="success"
          >
            mdi-check
          </v-icon>
        </slot>

        <span class="modal-dialog-title">
          <slot name="title">{{ title }}</slot>
        </span>

        <!-- optional close button -->
        <v-btn
          v-if="showCloseIcon"
          icon
          @click="close()"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- text -->
      <v-card-text>
        <slot name="text">
          <div
            class="modal-dialog-text"
            v-html="text"
          />
        </slot>
      </v-card-text>

      <!-- actions -->
      <v-card-actions v-if="showActions">
        <slot name="actions">
          <v-btn
            large
            color="success"
            data-test="dialog-ok-button"
            @click="close()"
          >
            <span>Close</span>
          </v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent, ref } from '@vue/composition-api'

export default defineComponent({
  name: 'ModalDialog',
  props: {
    title: { type: String, default: '' },
    text: { type: String, default: '' },
    showIcon: { type: Boolean, default: true },
    showActions: { type: Boolean, default: true },
    isPersistent: { type: Boolean, default: false },
    fullscreenOnMobile: { type: Boolean, default: false },
    isScrollable: { type: Boolean, default: false },
    dialogClass: { type: String, default: '' },
    maxWidth: { type: String, default: '' },
    showCloseIcon: { type: Boolean, default: false }
  },
  setup () {
    const isOpen = ref(false)

    const open = () => {
      isOpen.value = true
    }

    const close = () => {
      isOpen.value = false
    }

    return {
      open,
      close,
      isOpen
    }
  }
})
</script>

<style lang="scss" scoped>
  .notify-dialog {
    background: red;
  }
  .modal-dialog-title {
    text-align: center;
    word-break: break-word;
    font-size: var(--FONT_SIZE_TITLE);
    color: var(--COLOR_GRAY9);
  }
  .modal-dialog-text {
    text-align: center;
    font-size: var(--FONT_SIZE_TEXT);
    color: var(--COLOR_GRAY7);
  }
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
  [title] {
    text-align: center;
  }
</style>
