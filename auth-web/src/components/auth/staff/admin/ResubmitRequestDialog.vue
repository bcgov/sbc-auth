<template>
  <v-dialog
    v-model="dialog"
    persistent
    :attach="attach"
    content-class="resubmit-request-dialog"
  >
    <v-card flat>
      <v-card-title id="dialog-title">Modify Request</v-card-title>
      <v-card-text>
        <v-textarea
          ref="textarea"
          filled
          outlined
          auto-grow
          rows="5"
          id="resubmit-request-textarea"
          :value="xmlData"
          :autofocus="true"
          spellcheck="false"
          @input="emitInput($event)"
        />
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <div class="form__btns">
          <v-btn
            large
            color="primary"
            id="dialog-resubmit-button"
            :disabled="submitActive"
            :loading="submitActive"
            @click.native="resubmit()"
          >Resubmit</v-btn>
          <v-btn
            large depressed
            id="dialog-cancel-button"
            class="ml-2"
            :disabled="submitActive"
            :loading="submitActive"
            @click.native="emitClose()"
          >Cancel</v-btn>
        </div>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { namespace } from 'vuex-class'

const BusinessModule = namespace('business')

@Component({})
export default class ResubmitRequest extends Vue {
  @Prop() readonly dialog: boolean

  @Prop() readonly attach: string

  @Prop({ default: '' })
  readonly xmlData: string

  @Prop({ default: false })
  readonly submitActive: boolean

  private modifiedXml: string
  private emitInput (val: string): void {
    this.modifiedXml = val
  }

  @Emit('resubmit')
  private resubmit (): string {
    return this.modifiedXml
  }

  @Emit('close')
  private emitClose (): void { }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

::v-deep .v-textarea textarea {
  line-height: 1.5rem !important;
  font-size: $px-14 !important;
}

</style>
