<template>
  <div>
    <ModalDialog
      ref="accessRequest"
      max-width="643"
      :isPersistent="true"
      icon="mdi-check"
      data-test="dialog-access-request"
      dialog-class="notify-dialog"
    >
      <template #icon>
        <v-icon
          large
          :color="getModalData.color"
        >
          {{ getModalData.icon }}
        </v-icon>
      </template>
      <template #title>
        <span
          class="font-weight-bold text-size mb-1"
          data-test="dialog-header"
        > {{ getModalData.title }} </span>
      </template>
      <template #text>
        <div class="mx-8">
          <p
            class="mb-4 text-color sub-text-size text-justify"
            data-test="p-modal-text"
            v-html="getModalData.text"
          />
          <v-form
            v-if="isRejectModal && isMhrSubProductReview"
            ref="rejectForm"
          >
            <v-textarea
              id="rejection-reason-text-area"
              v-model="otherRejectReasonText"
              class="mb-n2 sub-text-size gray-9"
              content-class="sub-text-size gray-9"
              filled
              label="Reason for Rejection"
              aria-label="Reason for Rejection"
              counter="250"
              :rules="onholdOrRejectReasonRules"
            />
          </v-form>
          <v-form
            v-if="isOnHoldModal"
            ref="rejectForm"
            lazy-validation
            class="reject-form"
            data-test="reject-form"
          >
            <v-row justify="center">
              <v-col
                cols="6"
                class="pa-0"
              >
                <v-radio-group
                  v-model="accountToBeOnholdOrRejected"
                  :rules="accountToBeOnholdOrRejectedRules"
                  data-test="radio-group-hold-or-reject"
                  class="mt-0"
                >
                  <v-row
                    dense
                    class="d-flex flex-column align-items-center"
                  >
                    <v-col>
                      <v-radio
                        :key="OnholdOrRejectCode.REJECTED"
                        label="Reject Account"
                        :value="OnholdOrRejectCode.REJECTED"
                        data-test="radio-reject"
                      />
                    </v-col>
                    <v-col>
                      <v-radio
                        :key="OnholdOrRejectCode.ONHOLD"
                        label="On Hold"
                        :value="OnholdOrRejectCode.ONHOLD"
                        data-test="radio-on-hold"
                      />
                    </v-col>
                  </v-row>
                  <template #message="{ message }">
                    <span class="error-size"> {{ message }} </span>
                  </template>
                </v-radio-group>
              </v-col>
            </v-row>
            <v-select
              v-if="accountToBeOnholdOrRejected === OnholdOrRejectCode.ONHOLD"
              v-model="onHoldOrRejectReasons"
              filled
              label="Reason(s) why account is on hold "
              :items="onholdReasonCodes"
              item-text="desc"
              item-value="desc"
              data-test="hold-reason-type"
              class="my-0"
              :rules="onholdOrRejectReasonRules"
              multiple
            >
              <template #selection="{ item, index }">
                <span v-if="index === 0">{{ item.desc }}</span>
                <span
                  v-if="index === 1"
                  class="grey--text text-caption"
                >
                  (+{{ onHoldOrRejectReasons.length - 1 }} {{ onHoldOrRejectReasons.length > 2 ? 'others' : 'other' }})
                </span>
              </template>
            </v-select>
          </v-form>
          <v-form
            v-if="isMoveToPendingModal"
            ref="rejectForm"
            lazy-validation
            class="reject-form"
            data-test="reject-form"
          >
            <v-row justify="start">
              <v-col
                cols="6"
                class="pa-0"
              >
                <v-row
                  dense
                  class="d-flex flex-column align-items-center"
                >
                  <v-checkbox
                    class="mt-0 ml-4"
                    @change="toggleReason('Request was rejected in error')"
                  >
                    <template #label>
                      Request was rejected in error
                    </template>
                  </v-checkbox>
                </v-row>
                <v-row
                  dense
                  class="d-flex flex-column align-items-start"
                >
                  <v-checkbox class="mt-0 ml-4">
                    <template #label>
                      Other reason
                    </template>
                  </v-checkbox>
                </v-row>
              </v-col>
            </v-row>
            <v-row
              dense
              class="d-flex"
              justify="end"
            >
              <v-col
                cols="11"
                class="pa-0"
              >
                <v-text-field
                  v-model="otherRejectReasonText"
                  filled
                  label="Reason will be displayed in the email sent to user"
                  req
                  persistent-hint
                  full-width
                  :counter="50"
                />
              </v-col>
            </v-row>
          </v-form>
        </div>
      </template>
      <template #actions>
        <v-btn
          large
          :color="getModalData.color"
          class="font-weight-bold px-4"
          :loading="isSaving"
          data-test="btn-access-request"
          @click="callAction()"
        >
          {{ getModalData.btnLabel }}
        </v-btn>
        <v-btn
          large
          outlined
          color="primary"
          data-test="btn-close-access-request-dialog"
          @click="close()"
        >
          Cancel
        </v-btn>
      </template>
    </ModalDialog>

    <!-- confirmation modal -->
    <ModalDialog
      ref="accessRequestConfirmationDialog"
      :isPersistent="true"
      :title="getConfirmModalData.title"
      :text="getConfirmModalData.text"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="primary"
        >
          mdi-check
        </v-icon>
      </template>
      <template #text>
        <p
          class="mx-5"
          v-html="getConfirmModalData.text"
        />
      </template>
      <template #actions>
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
import { OnholdOrRejectCode, TaskRelationshipType } from '@/util/constants'
import { PropType, Ref, computed, defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import { Code } from '@/models/Code'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { useI18n } from 'vue-i18n-composable'
import { userAccessDisplayNames } from '@/resources/QualifiedSupplierAccessResource'

export default defineComponent({
  name: 'AccessRequestModal',
  components: {
    ModalDialog
  },
  props: {
    isRejectModal: {
      type: Boolean,
      default: false
    },
    isTaskRejected: {
      type: Boolean,
      default: false
    },
    isConfirmationModal: {
      type: Boolean,
      default: false
    },
    isSaving: {
      type: Boolean,
      default: false
    },
    isOnHoldModal: { // for BECID need hold or reject options
      type: Boolean,
      default: false
    },
    isMoveToPendingModal: {
      type: Boolean,
      default: false
    },
    isMhrSubProductReview: { // For Mhr sub-product review tasks
      type: Boolean,
      default: false
    },
    orgName: {
      type: String,
      default: ''
    },
    accountType: {
      type: String,
      default: ''
    },
    taskName: {
      type: String,
      default: ''
    },
    onholdReasonCodes: {
      type: Array as PropType<Code[]>,
      required: true
    }
  },
  setup (props, { emit }) {
    const { t } = useI18n()
    const onHoldOrRejectReasons: Ref<string[]> = ref([])
    const accountToBeOnholdOrRejected: Ref<string> = ref('')
    const accessRequest: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const accessRequestConfirmationDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const rejectForm: Ref<HTMLFormElement> = ref(null)
    const otherRejectReasonText: Ref<string> = ref('')

    const localState = reactive({
      mhrRejectionReason: '',
      mhrSubProductAccessText: computed((): string =>
        `Qualified Supplier - ${userAccessDisplayNames[props.taskName]} access to Manufactured Home Registry.`
      )
    })

    const onholdOrRejectReasonRules = [
      (v) => v.length > 0 || `${props.isMhrSubProductReview ? '' : 'This field is required'}`,
      (v) => (!props.isMhrSubProductReview || v.length <= 250) || 'Maximum 250 characters'
    ]
    const accountToBeOnholdOrRejectedRules = [
      (v) => !!v || 'Choose reject or on hold to proceed.'
    ]

    function openConfirm () {
      accessRequestConfirmationDialog.value.open()
    }

    function closeConfirm () {
      accessRequestConfirmationDialog.value.close()
    }

    function onConfirmCloseClick () {
      emit('after-confirm-action')
      closeConfirm()
    }

    function callAction () {
      let isValidForm = true
      let accountToBeOnHoldOrRejected

      if (props.isOnHoldModal) {
        isValidForm = rejectForm.value.validate()
      } else if (props.isMoveToPendingModal) {
        accountToBeOnHoldOrRejected = OnholdOrRejectCode.ONHOLD
      }

      if (props.isMoveToPendingModal && otherRejectReasonText.value) {
        onHoldOrRejectReasons.value.push(otherRejectReasonText.value)
      }

      if (props.isMhrSubProductReview && props.isRejectModal) {
        isValidForm = rejectForm.value.validate()

        if (isValidForm) onHoldOrRejectReasons.value.push(otherRejectReasonText.value)
      }

      emit('approve-reject-action', {
        isValidForm,
        accountToBeOnHoldOrRejected,
        onHoldOrRejectReasons: onHoldOrRejectReasons.value
      })
    }

    const getTitle = (isProductApproval: boolean) => {
      if (isProductApproval) {
        if (props.isTaskRejected) return 'Re-approve Access Request?'
        else return 'Approve Access Request?'
      } else {
        return 'Approve Account Creation Request?'
      }
    }

    const getText = (isProductApproval: boolean) => {
      if (isProductApproval) {
        let baseText = `By ${props.isTaskRejected ? 're-approving' : 'approving'} the request, this account will have`

        return props.isMhrSubProductReview
          ? `${baseText} ${localState.mhrSubProductAccessText}`
          : `${baseText} access to ${props.taskName}.`
      }
      return `Approving the request will activate this account.`
    }

    const getIcon = (isRejectModal: boolean) => {
      if (isRejectModal) return 'mdi-alert-circle-outline'
      return 'mdi-help-circle-outline'
    }

    const getColor = (isRejectedModal: boolean) => {
      if (isRejectedModal) return 'error'
      return 'primary'
    }

    const getModalData = computed(() => {
      const isProductApproval =
        props.accountType === TaskRelationshipType.PRODUCT

      let title: string = getTitle(isProductApproval)
      let text: string = getText(isProductApproval)

      let icon = getIcon(props.isRejectModal)
      let color = getColor(props.isRejectModal)
      let btnLabel = props.isTaskRejected ? 'Re-approve' : 'Approve'

      if (props.isRejectModal) {
        title = isProductApproval
          ? 'Reject Access Request?'
          : 'Reject Account Creation Request?'

        const rejectionDescText = props.isMhrSubProductReview
          ? `${localState.mhrSubProductAccessText} Enter your reason(s) for this decision. (Reasons will appear in the
            applicant's notification email).`
          : `access to ${props.taskName}.`

        text = isProductApproval // eslint-disable-next-line no-irregular-whitespace
          ? `By rejecting the request, this account will not have ${rejectionDescText}`
          : 'Rejecting the request will not activate this account'

        btnLabel = isProductApproval ? 'Reject' : 'Yes, Reject Account'
      } else if (props.isOnHoldModal) {
        // if we need to show on hold modal
        title = 'Reject or Hold Account Creation Request'

        text = t('onHoldOrRejectModalText').toString()

        btnLabel = 'Confirm'
      } else if (props.isMoveToPendingModal) {
        title = 'Move to Pending'
        text =
          'To place a rejected access request on hold, please select a reason. An email will be sent to the user to notify the action.'
        btnLabel = 'Confirm'
      }
      return { title, text, icon, color, btnLabel }
    })

    const getConfirmModalData = computed(() => {
      const isProductApproval =
        props.accountType === TaskRelationshipType.PRODUCT

      let title = isProductApproval
        ? `Request has been Approved`
        : `Account has been Approved`

      const baseText = `The account <strong>${props.orgName}</strong> has been approved`
      const productText = props.isMhrSubProductReview
        ? `for ${localState.mhrSubProductAccessText}`
        : `to access ${props.taskName}`

      let text = isProductApproval
        ? `${baseText} ${productText}`
        : `Account creation request has been approved`

      if (props.isRejectModal) {
        title = isProductApproval
          ? `Request has been Rejected`
          : `Account has been Rejected`
        // eslint-disable-next-line no-irregular-whitespace
        text = isProductApproval
          ? `The account <strong>${props.orgName}</strong> has been rejected ${productText}`
          : `Account creation request has been rejected`
      } else if (props.isOnHoldModal || props.isMoveToPendingModal) {
        title = 'Request is On Hold'
        text =
          'An email has been sent to the user presenting the reason why the account is on hold, ' +
          'and a link to resolve the issue.'
      }
      return { title, text }
    })

    const resetRejectForm = () => {
      onHoldOrRejectReasons.value = []
      otherRejectReasonText.value = ''
      rejectForm.value?.resetValidation()
    }

    const open = () => {
      accessRequest.value.open()
    }

    const close = () => {
      // Clear local rejection reasons on dialog close
      resetRejectForm()
      accessRequest.value.close()
    }

    const toggleReason = (reason: string) => {
      if (onHoldOrRejectReasons.value.includes(reason)) {
        onHoldOrRejectReasons.value = onHoldOrRejectReasons.value.filter((r) => r !== reason)
      } else {
        onHoldOrRejectReasons.value.push(reason)
      }
    }

    onMounted(() => {
      if (!props.isOnHoldModal) { onHoldOrRejectReasons.value = [] }
    })

    return {
      OnholdOrRejectCode,
      accessRequest,
      accessRequestConfirmationDialog,
      accountToBeOnholdOrRejected,
      accountToBeOnholdOrRejectedRules,
      callAction,
      close,
      closeConfirm,
      getConfirmModalData,
      getModalData,
      onholdOrRejectReasonRules,
      onHoldOrRejectReasons,
      onConfirmCloseClick,
      open,
      openConfirm,
      otherRejectReasonText,
      rejectForm,
      toggleReason,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';
  .reject-form{
    margin-bottom: -30px !important;
  }
  .reject-form .v-messages__message{
    color: var(--v-error-darken2) !important;
    caret-color: var(--v-error-darken2) !important;
  }
  .text-color {
    color: $gray7;
  }
  .text-size {
    font-size: 1.75rem !important;
  }
  .sub-text-size {
    font-size: 1rem !important;
  }
  .align-items-center {
    align-self: center !important;
  }
  .error-size {
    font-size: 16px;
  }
  ::v-deep {
    .v-textarea textarea {
      color: $gray9 !important;
      font-size: 1rem;
    }
  }
</style>
