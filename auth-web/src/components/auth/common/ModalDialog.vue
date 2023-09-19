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
          <span
            id="help-button"
            class="pl-2 pr-2 mr-auto"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            Help
          </span>
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
  setup (_, { emit }) {
    const isOpen = ref(false)

    const openHelp = () => {
      emit('open-help')
      isOpen.value = false
    }
    const closeDialog = () => {
      emit('close-dialog')
    }

    const open = () => {
      isOpen.value = true
    }
    const close = () => {
      isOpen.value = false
    }

    return {
      open,
      close,
      isOpen,
      openHelp,
      closeDialog
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/ModalDialog';
  #help-button {
    cursor: pointer;
    color: var(--v-primary-base) !important;
    .v-icon {
      transform: translate(0, -2px) !important;
      color: var(--v-primary-base) !important;
    }
  }
  .notify-dialog {
    background: red;
  }
  .modal-dialog-title {
    width: 100%;
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
