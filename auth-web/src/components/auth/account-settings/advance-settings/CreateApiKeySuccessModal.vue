<template>
  <ModalDialog
    ref="createKeySuccessDialog"
    title="API Key Successfully Created"
    dialog-class="info-dialog"
    max-width="600"
    :show-icon="false"
    show-close-icon
    data-test="create-api-key-success-modal"
  >
    <template #text>
      <div class="d-flex align-start mb-6">
        <v-icon
          color="warning"
          class="mr-2"
        >
          mdi-alert
        </v-icon>
        <span class="text-left">
          Copy or download your key to somewhere safe. This key is non-recoverable. You will not see it again once you leave this window.
        </span>
      </div>
      <p
        class="font-weight-bold text-left mb-2"
        data-test="created-key-summary"
      >
        {{ environmentLabel }} key
      </p>
      <div
        class="d-flex align-center mb-6"
        data-test="created-key-row"
      >
        <span class="key-value mr-2">{{ apiKey }}</span>
        <v-btn
          icon
          small
          aria-label="Copy API Key"
          title="Copy API Key"
          data-test="copy-api-key-button"
          @click="copyApiKey()"
        >
          <v-icon small>
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

@Component({
  components: {
    ModalDialog
  }
})
export default class CreateApiKeySuccessModal extends Vue {
  @Prop({ default: '' }) readonly apiKey: string
  @Prop({ default: '' }) readonly environmentLabel: string

  $refs: {
    createKeySuccessDialog: InstanceType<typeof ModalDialog>
  }

  public open () {
    this.$refs.createKeySuccessDialog.open()
  }

  public close () {
    this.$refs.createKeySuccessDialog.close()
  }

  public async copyApiKey () {
    try {
      await navigator.clipboard.writeText(this.apiKey)
    } catch (e) {
      // nothing to do here
    }
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
  font-family: monospace;
  font-size: 1rem;
  word-break: break-all;
}
</style>
