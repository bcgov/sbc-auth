import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { AccessType, Account } from "@/util/constants";
import { Component, Emit, Mixins, Prop, Vue } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { DataOptions } from "vuetify";
import { Event } from "@/models/event";
import { EventBus } from "@/event-bus";
import { Invitation } from "@/models/Invitation";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import { Organization } from "@/models/Organization";
import PaginationMixin from "@/components/auth/mixins/PaginationMixin.vue";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const pendingInvitationOrgs = computed(
      () => ctx.root.$store.state.staff.pendingInvitationOrgs
    );
    const resendPendingOrgInvitation = () =>
      ctx.root.$store.dispatch("staff/resendPendingOrgInvitation");
    const syncPendingInvitationOrgs = () =>
      ctx.root.$store.dispatch("staff/syncPendingInvitationOrgs");
    const deleteOrg = () => ctx.root.$store.dispatch("staff/deleteOrg");
    const $refs = ref<{
      confirmActionDialog: ModalDialog;
    }>(undefined);
    const pendingInvitationOrgs = ref<Organization[]>(undefined);
    const resendPendingOrgInvitation =
      ref<(invitation: Invitation) => void>(undefined);
    const syncPendingInvitationOrgs = ref<() => Organization[]>(undefined);
    const deleteOrg = ref<(org: Organization) => void>(undefined);
    const tableDataOptions = ref<Partial<DataOptions>>({});
    const orgToBeRemoved = ref<Organization>(null);
    const columnSort = ref(CommonUtils.customSort);
    const headerAccounts = ref([
      {
        text: "Expiry Date",
        align: "left",
        value: "expires",
        sortable: false,
        width: "150",
      },
      {
        text: "Name",
        align: "left",
        sortable: false,
        value: "name",
      },
      {
        text: "Contact Email",
        align: "left",
        sortable: false,
        value: "contactEmail",
      },
      {
        text: "Created By",
        align: "left",
        sortable: false,
        value: "createdBy",
      },
      {
        text: "Actions",
        align: "left",
        value: "action",
        sortable: false,
        width: "210",
      },
    ]);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const resend = async (invitation: Invitation) => {
      try {
        await resendPendingOrgInvitation.value(invitation);
        const event: Event = {
          message: `Invitation resent to ${invitation.recipientEmail}`,
          type: "success",
          timeout: 1000,
        };
        EventBus.$emit("show-toast", event);
      } catch (err) {
        const event: Event = {
          message: "Invitation resend failed",
          type: "error",
          timeout: 1000,
        };
        EventBus.$emit("show-toast", event);
      }
      await syncPendingInvitationOrgs.value();
    };
    const deleteInvitation = async () => {
      try {
        await deleteOrg.value(orgToBeRemoved.value);
        close();
        const event: Event = {
          message: "Invitation removed",
          type: "success",
          timeout: 1000,
        };
        EventBus.$emit("show-toast", event);
        await syncPendingInvitationOrgs.value();
      } catch (err) {
        const event: Event = {
          message: "Invitation remove failed",
          type: "error",
          timeout: 1000,
        };
        EventBus.$emit("show-toast", event);
      }
    };
    const showConfirmRemoveInviteModal = (org: Organization) => {
      orgToBeRemoved.value = org;
      ctx.refs.confirmActionDialog.open();
    };
    const close = () => {
      ctx.refs.confirmActionDialog.close();
    };
    onMounted(() => {
      tableDataOptions.value = DEFAULT_DATA_OPTIONS;
    });
    return {
      pendingInvitationOrgs,
      resendPendingOrgInvitation,
      syncPendingInvitationOrgs,
      deleteOrg,
      $refs,
      pendingInvitationOrgs,
      resendPendingOrgInvitation,
      syncPendingInvitationOrgs,
      deleteOrg,
      tableDataOptions,
      orgToBeRemoved,
      columnSort,
      headerAccounts,
      formatDate,
      getIndexedTag,
      resend,
      deleteInvitation,
      showConfirmRemoveInviteModal,
      close,
    };
  },
});
