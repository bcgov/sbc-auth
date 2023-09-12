<template>
  <v-dialog
    v-model="isVisible"
    attach="#entity-management"
    persistent
    scrollable
    max-width="50rem"
    data-test-tag="authorization-email-sent-dialog"
  >
    <v-card>
      <v-card-title>
        <slot name="title">
          <span>ADD TITLE</span>
        </slot>
      </v-card-title>
      <v-card-text>
        <slot name="content">
          <p>ADD CONTENT</p>
        </slot>
      </v-card-text>
      <v-card-actions class="form__btns">
        <span
          id="help-button"
          class="mr-auto pl-0 help-text d-flex justify-start"
          @click.stop="openHelp()"
        >
          <v-icon>mdi-help-circle-outline</v-icon>
          Help
        </span>
        <v-spacer />
        <v-btn
          large
          color="primary"
          @click="closeDialog()"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'AuthorizationRequestSentDialog',
  props: {
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['open-help', 'close-dialog'],
  setup (_, { emit }) {
    const openHelp = () => {
      emit('open-help')
    }
    const closeDialog = () => {
      emit('close-dialog')
    }

    return {
      openHelp,
      closeDialog
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
@import '@/assets/scss/ModalDialog';

.email-address {
  font-weight: 600;
}

#help-button {
  cursor: pointer;
  color: var(--v-primary-base) !important;
  .v-icon {
    transform: translate(0, -2px) !important;
    color: var(--v-primary-base) !important;
  }
}
</style>
