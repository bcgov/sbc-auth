import {
  defineComponent,
  toRefs,
  ref,
  computed,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { OnholdOrRejectCode, TaskRelationshipType } from "@/util/constants";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {
    isRejectModal: { default: false, type: Boolean },
    isConfirmationModal: { default: false, type: Boolean },
    isSaving: { default: false, type: Boolean },
    isOnHoldModal: { default: false, type: Boolean },
    orgName: { default: "", type: String },
    accountType: { default: "", type: String },
    taskName: { default: "", type: String },
    onholdReasonCodes: { type: Object as PropType<[]> },
  },
  setup(props, ctx) {
    const {
      isRejectModal,
      isConfirmationModal,
      isSaving,
      isOnHoldModal,
      orgName,
      accountType,
      taskName,
      onholdReasonCodes,
    } = toRefs(props);
    const onholdReasons = ref<any[]>([]);
    const accountToBeOnholdOrRejected = ref("");
    const OnholdOrRejectCode = ref(OnholdOrRejectCode);
    const $refs = ref<{
      accessRequest: ModalDialog;
      accessRequestConfirmationDialog: ModalDialog;
      rejectForm: HTMLFormElement;
    }>(undefined);
    const onholdReasonRules = ref([
      (v) => v.length > 0 || "This field is required",
    ]);
    const accountToBeOnholdOrRejectedRules = ref([
      (v) => !!v || "Choose reject or on hold to proceed.",
    ]);
    const modalData = computed(() => {
      const isProductApproval =
        accountType.value === TaskRelationshipType.PRODUCT;
      let title = isProductApproval
        ? "Approve Access Request ?"
        : "Approve Account Creation Request ?";
      let text = isProductApproval
        ? `By approving the request, this account will access to  ${taskName.value}`
        : `Approving the request will activate this account`;
      let icon = "mdi-help-circle-outline";
      let color = "primary";
      let btnLabel = "Approve";
      if (isRejectModal.value) {
        title = isProductApproval
          ? "Reject Access Request ?"
          : "Reject Account Creation Request ?";
        text = isProductApproval
          ? `By rejecting the request, this account won't have access to ${taskName.value}`
          : "Rejecting the request will not activate this account";
        icon = "mdi-alert-circle-outline";
        color = "error";
        btnLabel = isProductApproval ? "Reject" : "Yes,\u00A0Reject Account";
      } else if (isOnHoldModal.value) {
        title = "Reject or Hold Account Creation Request";
        text = ctx.root.$t("onHoldOrRejectModalText").toString();
        btnLabel = "Confirm";
      }
      return { title, text, icon, color, btnLabel };
    });
    const confirmModalData = computed(() => {
      const isProductApproval =
        accountType.value === TaskRelationshipType.PRODUCT;
      let title = isProductApproval
        ? `Request has been Approved`
        : `Account has been Approved`;
      let text = isProductApproval
        ? `The account <strong>${orgName.value}</strong> has been approved to access ${taskName.value}`
        : `Account creation request has been approved`;
      if (isRejectModal.value) {
        title = isProductApproval
          ? `Request has been Rejected`
          : `Account has been Rejected`;
        text = isProductApproval
          ? `The account <strong>${orgName.value}</strong> has been rejected to access ${taskName.value}`
          : `Account creation request has been rejected`;
      } else if (isOnHoldModal.value) {
        title = "Request is On Hold";
        text =
          "An email has been sent to the user presenting the reason\u00A0why the account is on hold, and\u00A0a link to resolve the issue.";
      }
      return { title, text };
    });
    const open = () => {
      ctx.refs.accessRequest.open();
    };
    const close = () => {
      ctx.refs.accessRequest.close();
    };
    const openConfirm = () => {
      ctx.refs.accessRequestConfirmationDialog.open();
    };
    const closeConfirm = () => {
      ctx.refs.accessRequestConfirmationDialog.close();
    };
    const onConfirmCloseClick = () => {
      closeConfirm();
    };
    const callAction = () => {
      let isValidForm = true;
      if (isOnHoldModal.value) {
        isValidForm = ctx.refs.rejectForm.validate();
      }
      return {
        isValidForm,
        accountToBeOnholdOrRejected: accountToBeOnholdOrRejected.value,
        onholdReasons: onholdReasons.value,
      };
    };
    onMounted(() => {
      if (!isOnHoldModal.value) {
        onholdReasons.value = [];
      }
    });
    return {
      onholdReasons,
      accountToBeOnholdOrRejected,
      OnholdOrRejectCode,
      $refs,
      onholdReasonRules,
      accountToBeOnholdOrRejectedRules,
      modalData,
      confirmModalData,
      open,
      close,
      openConfirm,
      closeConfirm,
      onConfirmCloseClick,
      callAction,
    };
  },
});
