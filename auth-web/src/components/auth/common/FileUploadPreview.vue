<template>
  <v-row>
    <v-col
      class="py-0"
      sm="12"
      md="12"
    >
      <v-form
        ref="fileUploadInput"
        lazy-validation
      >
        <v-file-input
          v-model="fileUpload"
          label="Upload File"
          filled
          dense
          accept="image/*, .pdf"
          class="file-upload-preview"
          :rules="fileUploadRules"
          show-size
          color="primary"
          @change="fileChange"
        />
      </v-form>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Vue from 'vue'
import { mapActions } from 'pinia'
import { useOrgStore } from '@/store/org'

@Component({
  components: {
    ModalDialog
  },
  methods: {
    ...mapActions(useOrgStore, [
      'resetAccountSetupProgress'
    ])
  }
})
export default class FileUploadPreview extends Vue {
  @Prop() inputFile: File
  @Prop({ default: true }) isRequired: boolean
  @Prop({ default: 0 }) maxSize: number // in KB
  private fileUpload = null

  $refs: {
    fileUploadInput: HTMLFormElement,
  }

  private fileUploadRules = [
    (v) => {
      if (this.isRequired) {
        return !!v || 'Affidavit file is required'
      }
      return true
    },
    (file) => {
      if (this.maxSize) {
        return (file?.size <= (this.maxSize * 1000)) || 'File size exceed max allowed size'
      }
      return true
    }
  ]

  mounted () {
    if (this.inputFile) {
      this.fileUpload = this.inputFile
      this.$nextTick(() => {
        this.isFileValid()
      })
    }
  }

  private fileChange (file) {
    this.emitFileSelected(file)
  }

  @Emit('file-selected')
  emitFileSelected (file) {
    this.isFileValid()
    return file
  }

  @Emit('is-file-valid')
  isFileValid () {
    return this.$refs.fileUploadInput.validate()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

::v-deep {
  .file-upload-preview {
    .v-input__append-outer {
      margin-top: 10px !important
    }
    .v-input__slot{
      background-color: $BCgovInputBG !important;
    }
    .v-file-input__text{
     color: var(--v-primary-base) !important;

    }
  }
}

</style>
