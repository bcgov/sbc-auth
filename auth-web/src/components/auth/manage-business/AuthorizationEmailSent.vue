<template>
    <v-card>
        <v-card-title>
          <span>Authorization Email Sent</span>
        </v-card-title>
        <v-card-text>
          An email was sent to {{  email }}

          Confirm your access by clicking the link inside. This will add the business to your Business Registry List.

          The link is valid for 15 minutes.
        </v-card-text>
        <v-card-actions class="form__btns">
          <span
            class="pl-2 pr-2 mr-auto"
            id="help-button"
            @click.stop="openHelp()"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
            Help
          </span>
          <v-spacer></v-spacer>
          <v-btn large color="primary" @click="closeAuthEmailSentDialog()">OK</v-btn>
        </v-card-actions>
    </v-card>
</template>
<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  setup (props, { emit }) {
    const openHelp = () => {
      emit('open-help')
    }
    const closeAuthEmailSentDialog = () => {
      emit('close-dialog')
    }

    return {
      openHelp,
      closeAuthEmailSentDialog
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

#help-button {
  color: var(--v-primary-base) !important;
  .v-icon {
    transform: translate(0, -2px) !important;
    color: var(--v-primary-base) !important;
  }
}
</style>
