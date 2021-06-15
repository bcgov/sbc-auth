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
        <div class="mx-6">
          <p class="mb-4 mr-7" v-html="modalData.text"></p>
          <v-select
            filled
            label="Reject Reason"
            :items="rejectReasonCodes"
            item-text="desc"
            item-value="code"
            v-model="rejectReason"
            data-test="reject-reason-type"
            :menu-props="{  contentClass: 'reject-reason-item' }"
            class="mt-5"
            hide-details
            v-if="isOnHoldModal"
            />

        </div>
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
       :isPersistent="true"
      :title="confirmModalData.title"
      :text="confirmModalData.text"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="primary">mdi-check</v-icon>
      </template>
      <template v-slot:text>
        <p class="mx-5" v-html="confirmModalData.text"></p>
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
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { TaskRelationshipType } from '@/util/constants'

@Component({
  components: {
    ModalDialog
  }
})
export default class AccessRequestModal extends Vue {
  @Prop({ default: false }) private isRejectModal: boolean
  @Prop({ default: false }) private isConfirmationModal: boolean
  @Prop({ default: false }) private isSaving: boolean
  @Prop({ default: false }) private isOnHoldModal: boolean // for BECID need hold or reject options
  @Prop({ default: '' }) private orgName: string
  @Prop({ default: '' }) private accountType: string
  @Prop({ default: '' }) private taskName: string
  @Prop() private rejectReasonCodes: []

  private rejectReason:string=''

  $refs: {
    accessRequest: ModalDialog,
    accessRequestConfirmationDialog: ModalDialog,
  }

  get modalData () {
    const isProductApproval = this.accountType === TaskRelationshipType.PRODUCT
    let title = isProductApproval
      ? 'Approve Access Request ?'
      : 'Approve Account Creation Request ?'
    let text = isProductApproval
      ? `By approving the request, this account will access to  ${this.taskName}`
      : `Approving the request will activate this account`
    let icon = 'mdi-help-circle-outline'
    let color = 'primary'
    let btnLabel = 'Approve'

    if (this.isRejectModal) {
      title = isProductApproval
        ? 'Reject Access Request ?'
        : 'Reject Account Creation Request ?'

      text = isProductApproval
        // eslint-disable-next-line no-irregular-whitespace
        ? `By rejecting the request, this account won't have access to ${this.taskName}`
        : 'Rejecting the request will not activate this account'

      btnLabel = 'Reject'
    } else if (this.isOnHoldModal) { // if we need to show on hold modal
      title = 'Reject or Hold Account Creation Request'

      text = 'To place account on hold, please choose a reason. An email will be sent to the user to resolve the issue. Or choose "Reject Account" in the drop down to reject the request'

      btnLabel = 'Confirm'
    }
    return { title, text, icon, color, btnLabel }
  }

  get confirmModalData () {
    const isProductApproval = this.accountType === TaskRelationshipType.PRODUCT

    let title = isProductApproval
      ? `Request has been Approved`
      : `Account has been Approved`

    let text = isProductApproval
      ? `The account <strong>${this.orgName}</strong> has been approved to access ${this.taskName}`
      : `Account creation request has been approved`

    if (this.isRejectModal) {
      title = isProductApproval
        ? `Request has been Rejected`
        : `Account has been Rejected`
      // eslint-disable-next-line no-irregular-whitespace
      text = isProductApproval
        ? `The account <strong>${this.orgName}</strong> has been rejected to access ${this.taskName}`
        : `Account creation request has been rejected`
    } else if (this.isOnHoldModal) {
      title = 'Request is On Hold'

      text = 'An email has been sent to the user presenting the reason why the account is on hold, and a link to resolve the issue.'
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
    // return reject reason since we need to pass to API
    return this.rejectReason
  }
}
</script>

<style lang="scss" >
  @import '$assets/scss/theme.scss';

  .reject-reason-item .v-list-item:last-child {
      border-top: 1px solid $gray5;
    }

</style>
