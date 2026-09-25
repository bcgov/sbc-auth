<template>
  <ModalDialog
    ref="createKeyDialog"
    title="Create API Key"
    dialog-class="info-dialog"
    max-width="720"
    :show-icon="false"
    show-close-icon
    data-test="create-api-key-modal"
    @close-dialog="resetForm()"
  >
    <template #text>
      <p class="font-weight-bold mb-2">
        API Key Name
      </p>
      <v-text-field
        v-model="newKeyName"
        filled
        hide-details="auto"
        placeholder="Enter an API key name"
        aria-label="Enter an API key name"
        maxlength="100"
        hint="Give this key a name you will recognize later"
        persistent-hint
        data-test="key-name-input"
        :error-messages="nameErrorMessages"
        @input="newKeyNameError = false"
      />
      <p class="font-weight-bold mt-7 mb-2">
        Environment
      </p>
      <v-radio-group
        v-model="newKeyEnvironment"
        hide-details="auto"
        class="environment-radio-group"
        data-test="key-environment-radio-group"
      >
        <v-radio
          value="sandbox"
          data-test="key-environment-sandbox"
        >
          <template #label>
            <div>
              <div class="radio-label">
                Sandbox
              </div>
              <div class="radio-hint">
                Use this to test functionality before going live.
              </div>
            </div>
          </template>
        </v-radio>
        <v-radio
          value="production"
          disabled
          data-test="key-environment-production"
        >
          <template #label>
            <div>
              <div class="radio-label d-flex align-center">
                Production
                <v-chip
                  x-small
                  label
                  color="grey lighten-2"
                  class="font-weight-bold ml-2"
                  data-test="production-not-available-chip"
                >
                  NOT AVAILABLE
                </v-chip>
              </div>
              <div class="radio-hint">
                Create a Sandbox key first to enable this option.
              </div>
            </div>
          </template>
        </v-radio>
      </v-radio-group>
    </template>
    <template #actions>
      <v-btn
        outlined
        large
        depressed
        color="primary"
        class="px-7"
        aria-label="Cancel"
        data-test="cancel-create-key-button"
        :loading="loading"
        :disabled="loading"
        @click="close()"
      >
        Cancel
      </v-btn>
      <v-btn
        large
        depressed
        color="primary"
        class="ml-3 px-8 font-weight-bold"
        aria-label="Create"
        data-test="confirm-create-key-button"
        :loading="loading"
        :disabled="loading"
        @click="createKey()"
      >
        Create
      </v-btn>
    </template>
  </ModalDialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

@Component({
  components: {
    ModalDialog
  }
})
export default class CreateApiKeyModal extends Vue {
  @Prop({ default: false }) readonly loading: boolean

  public newKeyName = ''
  public newKeyNameError = false
  // not validated and not sent to the API yet - UI only until the new design is done
  public newKeyEnvironment = ''

  $refs: {
    createKeyDialog: InstanceType<typeof ModalDialog>
  }

  get nameErrorMessages (): string[] {
    return this.newKeyNameError ? ['Enter an API key name.'] : []
  }

  public open () {
    this.resetForm()
    this.$refs.createKeyDialog.open()
  }

  public close () {
    this.$refs.createKeyDialog.close()
  }

  public resetForm () {
    this.newKeyName = ''
    this.newKeyNameError = false
    this.newKeyEnvironment = ''
  }

  public createKey () {
    if (!this.newKeyName.trim()) {
      this.newKeyNameError = true
      return
    }
    this.$emit('create', {
      apiKeyName: this.newKeyName
    })
  }
}
</script>

<style lang="scss" scoped>
.environment-radio-group {
  ::v-deep {
    .v-radio {
      align-items: flex-start;
      margin-bottom: 1rem;
    }

    // Vuetify applies the radio-group's error color to every label, even
    // disabled ones, so force disabled radios back to the standard disabled
    // (grey) label color instead of the error (red) one.
    .v-radio--is-disabled .v-label {
      color: rgba(0, 0, 0, 0.38) !important;
    }

    // Suppress Vuetify's default shake animation on error.
    .v-label {
      animation: none !important;
    }
  }
}

.radio-hint {
  font-size: 0.875rem;
  color: var(--v-grey-darken1);
}
</style>
