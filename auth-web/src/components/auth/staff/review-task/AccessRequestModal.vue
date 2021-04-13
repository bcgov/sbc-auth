<template>
<div>
 <ModalDialog
    max-width="680"
    :isPersistent="true"
    ref="accessRequest"
    icon="mdi-check"
    :title="modalData.title"
    data-test="dialog-access-request"
    dialog-class="notify-dialog"

    >
      <template v-slot:icon>
        <v-icon large :color="modalData.color">{{modalData.icon}}</v-icon>
      </template>
      <template v-slot:text>
        <p class="mb-4 mr-7">{{modalData.text}}</p>

      </template>
      <template v-slot:actions>
        <v-btn large :color="modalData.color" @click="callAction()"
        class="font-weight-bold px-4"
        :loading="isSaving"
        data-test="btn-access-request"
        >{{modalData.btnLabel}}</v-btn>
        <v-btn large outlined color="primary" @click="close()" data-test="btn-close-access-request-dialog">Cancel</v-btn>
      </template>
    </ModalDialog>

    <!-- confirmation modal -->
    <ModalDialog
      ref="accessRequestConfirmationDialog"
      :title="confirmModalData.title"
      :text="confirmModalData.text"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="primary">mdi-check</v-icon>
      </template>

      <template v-slot:actions>
        <v-btn
          large
          color="primary"
          class="font-weight-bold"
          @click="onConfirmCloseClick"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>

</div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

@Component({
  components: {
    ModalDialog
  }
})
export default class AccessRequestModal extends Vue {
  @Prop({ default: false }) private isRejectModal: boolean
  @Prop({ default: false }) private isConfirmationModal: boolean
  @Prop({ default: false }) private isSaving: boolean
  @Prop({ default: '' }) private orgName: string

  $refs: {
    accessRequest: ModalDialog,
    accessRequestConfirmationDialog: ModalDialog,
  }

  get modalData () {
    // meed to change Wills Registry to product
    let title = 'Approve Access Request?'
    let text = 'Approving the request will give this account access to Wills Registry'
    let icon = 'mdi-check'
    let color = 'primary'
    let btnLabel = 'Yes, Approve Request'
    if (this.isRejectModal) {
      title = 'Reject Access Request?'
      text = 'Rejecting the request will reject this account to access Wills Registry'
      icon = 'mdi-alert-circle-outline'
      color = 'error'
      btnLabel = 'Yes, Reject Request'
    }
    return { title, text, icon, color, btnLabel }
  }

  get confirmModalData () {
    let title = 'Request has been Approved'
    let text = `The account <strong>${this.orgName}</strong> has been approved to access Wills Registry`

    if (this.isRejectModal) {
      title = 'Request has been Rejected'
      // eslint-disable-next-line no-irregular-whitespace
      text = `The account <strong>${this.orgName}</strong> has been rejected to access Wills Registry`
    }
    return { title, text }
  }
  public open () {
    this.$refs.accessRequest.open()
  }

  public close () {
    this.$refs.accessRequest.close()
  }

  public openConfirm () {
    this.$refs.accessRequestConfirmationDialog.open()
  }

  public closeConfirm () {
    this.$refs.accessRequestConfirmationDialog.close()
  }

 @Emit('after-confirm-action')
  public onConfirmCloseClick () {
    this.closeConfirm()
  }

  @Emit('approve-reject-action')
 public callAction () {
   return this.isRejectModal
 }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

</style>
