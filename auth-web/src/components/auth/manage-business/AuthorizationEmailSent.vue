<template>
  <v-card>
    <v-card-title>
      <span>Authorization Email Sent</span>
    </v-card-title>
    <v-card-text>
      <p>An email was sent to <b>{{ email }}</b></p>
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
        OK
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script lang="ts">
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'AuthorizationEmailSent',
  props: {
    email: {
      type: String,
      default: ''
    }
  },
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
.v-card {
    > div {
      &:first-of-type {
        padding: 40px 40px 0 40px;
      }
      &:nth-of-type(2) {
        padding: 16px 40px 0 40px;
      }
      &:last-of-type {
        padding: 40px 40px 40px 40px;
        button {
          padding: 0 20px;
        }
      }
    }
  }

#help-button {
  color: var(--v-primary-base) !important;
  .v-icon {
    transform: translate(0, -2px) !important;
    color: var(--v-primary-base) !important;
  }
}
</style>
