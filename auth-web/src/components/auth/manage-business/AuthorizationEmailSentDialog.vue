<template>
  <v-dialog
    v-model="computedIsVisible"
    attach="#entity-management"
    persistent
    scrollable
    max-width="50rem"
    data-test-tag="authorization-email-sent-dialog"
  >
    <v-card>
      <v-card-title>
        <h1>Authorization Email Sent</h1>
      </v-card-title>
      <v-card-text>
        <p>An email was sent to <span class="email-address">{{ email }}</span></p>
        <p>Confirm your access by clicking the link inside. This will add the business to your Business Registry List. The link is valid for 15 minutes.</p>
      </v-card-text>
      <v-card-actions class="form__btns">
        <span
          id="help-button"
          class="pl-2 pr-2 mr-auto"
          @click.stop="openHelp()"
        >
          <v-icon>mdi-help-circle-outline</v-icon>
          Help
        </span>
        <v-spacer />
        <v-btn
          large
          color="primary"
          @click="closeAuthEmailSentDialog()"
        >
          Close
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script lang="ts">
import { computed, defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'AuthorizationEmailSent',
  props: {
    email: {
      type: String,
      default: ''
    },
    isVisible: {
      type: Boolean,
      default: false
    },
  },
  setup (props, { emit }) {
    const openHelp = () => {
      emit('open-help')
    }
    const closeAuthEmailSentDialog = () => {
      emit('close-dialog')
    }

    const computedIsVisible = computed(() => {
      return props.isVisible
    })

    return {
      computedIsVisible,
      openHelp,
      closeAuthEmailSentDialog
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
@import '@/assets/scss/ModalDialog.scss';

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
