<template>
  <ModalDialog
    ref="createKeyDialog"
    dialog-class="info-dialog"
    max-width="720"
    :show-icon="false"
    show-close-icon
    data-test="create-api-key-modal"
    @close-dialog="resetForm()"
  >
    <template #title>
      <span data-test="create-api-key-title">Create API Key</span>
    </template>
    <template #text>
      <p
        class="modal-subtitle mt-n4 mb-8"
        data-test="create-api-key-subtitle"
      >
        Use this to test functionality before going live.
      </p>
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
        hint="This will help you identify the key in the list later"
        persistent-hint
        data-test="key-name-input"
        :error-messages="nameErrorMessages"
        @input="newKeyNameError = false"
      />
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
.modal-subtitle {
  font-size: 16px;
  color: var(--v-grey-darken1);
}
</style>
