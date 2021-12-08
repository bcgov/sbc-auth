<template>
<div>
 <ModalDialog
    max-width="643"
    :isPersistent="true"
    ref="accessRequest"
    icon="mdi-check"
    data-test="dialog-access-request"
    dialog-class="notify-dialog"
    >

      <template v-slot:icon>
        <v-icon large :color="modalData.color">{{modalData.icon}}</v-icon>
      </template>
      <template v-slot:title>
        <span class="font-weight-bold text-size mb-1" data-test="dialog-header"> {{ modalData.title }} </span>
      </template>
      <template v-slot:text>
        <div class="mx-8">
          <p class="mb-4 text-color sub-text-size" v-html="modalData.text" data-test="p-modal-text"></p>
          <v-form ref="rejectForm" lazy-validation class="reject-form" data-test="reject-form" v-if="isOnHoldModal">
            <v-row justify="center">
              <v-col cols="6" class="pa-0">
                <v-radio-group
                  v-model="accountToBeOnholdOrRejected"
                  :rules="accountToBeOnholdOrRejectedRules"
                  data-test="radio-group-hold-or-reject"
                  class="mt-0"
                >
                  <v-row dense class="d-flex flex-column align-items-center">
                    <v-col>
                      <v-radio
                        label="Reject Account"
                        :key="OnholdOrRejectCode.REJECTED"
                        :value="OnholdOrRejectCode.REJECTED"
                        data-test="radio-reject"
                      >
                      </v-radio>
                    </v-col>
                    <v-col>
                      <v-radio
                        label="On Hold"
                        :key="OnholdOrRejectCode.ONHOLD"
                        :value="OnholdOrRejectCode.ONHOLD"
                        data-test="radio-on-hold"
                      ></v-radio>
                    </v-col>
                  </v-row>
                  <template v-slot:message="{ message }">
                    <span class="error-size"> {{ message }} </span>
                  </template>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-select
              filled
              label="Reason(s) why account is on hold "
              :items="onholdReasonCodes"
              item-text="desc"
              item-value="desc"
              v-model="onholdReasons"
              data-test="hold-reason-type"
              class="my-0"
              :rules="onholdReasonRules"
              multiple
              v-if="accountToBeOnholdOrRejected === OnholdOrRejectCode.ONHOLD"
            >
              <template v-slot:selection="{ item, index }">
                <span v-if="index === 0">{{ item.desc }}</span>
                <span
                  v-if="index === 1"
                  class="grey--text text-caption"
                >
                  (+{{ onholdReasons.length - 1 }} {{ onholdReasons.length > 2 ? 'others' : 'other' }})
                </span>
              </template>
          </v-select>

          </v-form>
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
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { OnholdOrRejectCode, TaskRelationshipType } from '@/util/constants'
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
  @Prop({ default: false }) private isOnHoldModal: boolean // for BECID need hold or reject options
  @Prop({ default: '' }) private orgName: string
  @Prop({ default: '' }) private accountType: string
  @Prop({ default: '' }) private taskName: string
  @Prop() public onholdReasonCodes: []

  public onholdReasons: any[] = []
  public accountToBeOnholdOrRejected = ''

  OnholdOrRejectCode = OnholdOrRejectCode

  $refs: {
    accessRequest: ModalDialog,
    accessRequestConfirmationDialog: ModalDialog,
    rejectForm: HTMLFormElement,
  }
  readonly onholdReasonRules = [v => v.length > 0 || 'This field is required']
  readonly accountToBeOnholdOrRejectedRules = [v => !!v || 'Choose reject or on hold to proceed.']

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
      icon = 'mdi-alert-circle-outline'
      color = 'error'
      btnLabel = isProductApproval ? 'Reject' : 'Yes, Reject Account'
    } else if (this.isOnHoldModal) { // if we need to show on hold modal
      title = 'Reject or Hold Account Creation Request'

      text = this.$t('onHoldOrRejectModalText').toString()

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

  mounted () {
    if (!this.isOnHoldModal) {
      this.onholdReasons = []
    }
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
    let isValidForm = true
    if (this.isOnHoldModal) {
      isValidForm = this.$refs.rejectForm.validate()
    }
    // all other time passing form as valid since there is no values
    return { isValidForm, accountToBeOnholdOrRejected: this.accountToBeOnholdOrRejected, onholdReasons: this.onholdReasons }
  }
}
</script>

<style lang="scss" >
  @import '$assets/scss/theme.scss';
  .reject-form{
    margin-bottom: -30px !important;
  }
  .reject-form .v-messages__message{
    color: var(--v-error-darken2) !important;
    caret-color: var(--v-error-darken2) !important;
  }
  .text-color {
    color: $TextColorGray;
  }
  .text-size {
    font-size: 1.7142rem !important;
  }
  .sub-text-size {
    font-size: 1.1428rem !important;
  }
  .align-items-center {
    align-self: center !important;
  }
  .error-size {
    font-size: 16px;
  }
</style>
