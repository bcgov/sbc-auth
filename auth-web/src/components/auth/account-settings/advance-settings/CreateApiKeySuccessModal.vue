<template>
  <ModalDialog
    ref="createKeySuccessDialog"
    title="API Key Successfully Created"
    dialog-class="info-dialog"
    max-width="700"
    :show-icon="false"
    show-close-icon
    data-test="create-api-key-success-modal"
  >
    <template #text>
      <p
        class="font-weight-bold text-left mt-6 mb-6"
        data-test="created-key-summary"
      >
        {{ displayName }} - {{ environmentLabel }} key
      </p>
      <div
        class="d-flex align-center mb-6"
        data-test="created-key-row"
      >
        <span class="key-value mr-2">{{ apiKey }}</span>
        <v-btn
          icon
          aria-label="Copy API Key"
          title="Copy API Key"
          data-test="copy-api-key-button"
          @click="copyApiKey()"
        >
          <v-icon color="primary">
            mdi-content-copy
          </v-icon>
        </v-btn>
      </div>
      <v-btn
        text
        color="primary"
        class="pl-0"
        aria-label="Download API Key"
        data-test="download-api-key-button"
        @click="downloadApiKey()"
      >
        <v-icon class="mr-1">
          mdi-file-download-outline
        </v-icon>
        <span class="text-decoration-underline">Download API Key</span>
      </v-btn>
    </template>
    <template #actions>
      <v-btn
        outlined
        large
        depressed
        color="primary"
        class="px-8"
        data-test="close-create-api-key-success-button"
        @click="close()"
      >
        Close
      </v-btn>
    </template>
  </ModalDialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { copyApiKeyToClipboard } from '@/util/api-key-util'

@Component({
  components: {
    ModalDialog
  }
})
export default class CreateApiKeySuccessModal extends Vue {
  @Prop({ default: '' }) readonly apiKey: string
  @Prop({ default: '' }) readonly environmentLabel: string
  @Prop({ default: '' }) readonly apiKeyName: string

  get displayName (): string {
    return this.apiKeyName || 'Unnamed Key'
  }

  $refs: {
    createKeySuccessDialog: InstanceType<typeof ModalDialog>
  }

  public open () {
    this.$refs.createKeySuccessDialog.open()
  }

  public close () {
    this.$refs.createKeySuccessDialog.close()
  }

  public async copyApiKey (): Promise<void> {
    await copyApiKeyToClipboard(this.apiKey, this.displayName)
  }

  public downloadApiKey () {
    const blob = new Blob([this.apiKey], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'api-key.txt'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }
}
</script>

<style lang="scss" scoped>
.key-value {
  font-size: 1rem;
  word-break: break-all;
}
</style>
