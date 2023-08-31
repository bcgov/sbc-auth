<template>
  <v-dialog
    v-model="dialog"
    persistent
    scrollable
    :attach="attach"
    content-class="resubmit-request-dialog"
  >
    <v-card flat>
      <v-card-title id="dialog-title">
        Modify Request
      </v-card-title>
      <v-divider />
      <v-card-text class="pt-1 pb-1">
        <v-textarea
          id="resubmit-request-textarea"
          ref="requestTextarea"
          filled
          outlined
          no-resize
          hide-details
          :value="xmlData"
          spellcheck="false"
          @input="emitInput($event)"
        />
      </v-card-text>
      <v-divider />
      <v-card-actions>
        <v-spacer />
        <div class="form__btns">
          <v-btn
            id="dialog-resubmit-button"
            large
            color="primary"
            :disabled="submitActive"
            :loading="submitActive"
            @click.native="resubmit()"
          >
            Resubmit
          </v-btn>
          <v-btn
            id="dialog-cancel-button"
            large
            depressed
            class="ml-2"
            :disabled="submitActive"
            :loading="submitActive"
            @click.native="emitClose()"
          >
            Cancel
          </v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'

@Component({})
export default class ResubmitRequest extends Vue {
  @Prop() readonly dialog: boolean

  @Prop() readonly attach: string

  @Prop({ default: '' })
  readonly xmlData: string

  @Prop({ default: false })
  readonly submitActive: boolean

  private modifiedXml: string
  emitInput (val: string): void {
    this.calculateInputHeight()
    this.modifiedXml = val
  }

  private mounted () {
    this.modifiedXml = this.xmlData
    this.calculateInputHeight()
  }

  private calculateInputHeight () {
    // alternate to auto-grow in v-textarea.
    // unable to use auto-grow (in an editable textarea) due to a bug in this version.
    // we can use auto-grow and remove this when we upgrade vuetify to v3.0.0

    // eslint-disable-next-line
    // @ts-ignore
    const input = this.$refs.requestTextarea.$refs.input
    if (!input) return

    const height = input.scrollHeight

    // eslint-disable-next-line
    // @ts-ignore
    const minHeight = parseInt(this.$refs.requestTextarea.rows, 10) * parseFloat(this.$refs.requestTextarea.rowHeight)
    input.style.height = Math.max(minHeight, height) + 'px'
  }

  @Emit('resubmit')
  resubmit (): string {
    return this.modifiedXml
  }

  @Emit('close')
  emitClose (): void { }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

::v-deep .v-textarea textarea {
  line-height: 1.5rem !important;
  font-size: $px-14 !important;
}

</style>
