<template>
  <v-row>
    <v-col class="py-0" sm="8" md="6">
      <v-file-input
        label="Select File"
        filled
        dense
        v-model="fileUpload"
        accept="image/*, .pdf"
        class="file-upload-preview"
        prepend-icon=""
        @change="fileChange"
      >
      </v-file-input>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import Vue from 'vue'
import { mapActions } from 'vuex'

@Component({
  components: {
    ModalDialog
  },
  methods: {
    ...mapActions('org', [
      'resetAccountSetupProgress'
    ])
  }
})
export default class FileUploadPreview extends Vue {
  @Prop() inputFile: File
  private fileUpload = null

  mounted () {
    if (this.inputFile) {
      this.fileUpload = this.inputFile
    }
  }
  private fileChange (file) {
    this.emitFileSelected(file)
  }

  @Emit('file-selected')
  emitFileSelected (file) {
    return file
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
  }
}

</style>
