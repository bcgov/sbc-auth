import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { LoginSource, Pages, SearchFilterCodes } from "@/util/constants";
import { Member, MembershipStatus, Organization } from "@/models/Organization";
import { mapActions, mapState } from "vuex";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import AccountMixin from "@/components/auth/mixins/AccountMixin.vue";
import { Invitation } from "@/models/Invitation";
import InvitationsDataTable from "@/components/auth/account-settings/team-management/InvitationsDataTable.vue";
import InviteUsersForm from "@/components/auth/account-settings/team-management/InviteUsersForm.vue";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import MemberDataTable from "@/components/auth/account-settings/team-management/MemberDataTable.vue";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import PendingMemberDataTable from "@/components/auth/account-settings/team-management/PendingMemberDataTable.vue";
import SearchFilterInput from "@/components/auth/common/SearchFilterInput.vue";
import { SearchFilterParam } from "@/models/searchfilter";
import TeamManagementMixin from "@/components/auth/mixins/TeamManagementMixin.vue";
export default defineComponent({
  components: {
    MemberDataTable,
    InvitationsDataTable,
    PendingMemberDataTable,
    InviteUsersForm,
    ModalDialog,
    SearchFilterInput,
  },
  props: { orgId: { default: "", type: String } },
  setup(props, ctx) {
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const resending = computed(() => ctx.root.$store.state.org.resending);
    const sentInvitations = computed(
      () => ctx.root.$store.state.org.sentInvitations
    );
    const pendingOrgMembers = computed(
      () => ctx.root.$store.state.org.pendingOrgMembers
    );
    const memberLoginOption = computed(
      () => ctx.root.$store.state.org.memberLoginOption
    );
    const currentBusiness = computed(
      () => ctx.root.$store.state.business.currentBusiness
    );
    const resendInvitation = () =>
      ctx.root.$store.dispatch("org/resendInvitation");
    const deleteInvitation = () =>
      ctx.root.$store.dispatch("org/deleteInvitation");
    const syncPendingOrgInvitations = () =>
      ctx.root.$store.dispatch("org/syncPendingOrgInvitations");
    const syncPendingOrgMembers = () =>
      ctx.root.$store.dispatch("org/syncPendingOrgMembers");
    const syncActiveOrgMembers = () =>
      ctx.root.$store.dispatch("org/syncActiveOrgMembers");
    const syncMemberLoginOption = () =>
      ctx.root.$store.dispatch("org/syncMemberLoginOption");
    const { orgId } = toRefs(props);
    const tab = ref(null);
    const isLoading = ref(true);
    const memberToBeApproved = ref<Member>(undefined);
    const invitationToBeRemoved = ref<Invitation>(undefined);
    const sentInvitations = ref<Invitation[]>(undefined);
    const memberLoginOption = ref<string>(undefined);
    const syncMemberLoginOption =
      ref<(currentAccount: number) => string>(undefined);
    const resendInvitation = ref<(invitation: Invitation) => void>(undefined);
    const deleteInvitation = ref<(invitationId: number) => void>(undefined);
    const syncPendingOrgMembers = ref<() => Member[]>(undefined);
    const syncPendingOrgInvitations = ref<() => Invitation[]>(undefined);
    const syncActiveOrgMembers = ref<() => Member[]>(undefined);
    const currentUser = ref<KCUserProfile>(undefined);
    const appliedFilterValue = ref<string>("");
    const teamMembersCount = ref(0);
    const pendingMembersCount = ref(0);
    const searchFilter = ref<SearchFilterParam[]>([
      {
        id: SearchFilterCodes.USERNAME,
        placeholder: "Team Member",
        labelKey: "Team Member",
        appliedFilterValue: "",
        filterInput: "",
      },
    ]);
    const pendingOrgMembers = ref<Member[]>(undefined);
    const $refs = ref<{
      successDialog: ModalDialog;
      errorDialog: ModalDialog;
      inviteUsersDialog: ModalDialog;
      confirmActionDialog: ModalDialog;
      confirmActionDialogWithQuestion: ModalDialog;
    }>(undefined);
    const pendingApprovalCount = computed(() => {
      return pendingOrgMembers.value.length;
    });
    const isBCEIDUser = computed((): boolean => {
      return currentUser.value?.loginSource === LoginSource.BCEID;
    });
    const filteredMembersCount = computed(() => {
      switch (tab.value) {
        case 0:
          return teamMembersCount.value;
        case 1:
          return pendingMembersCount.value;
        default:
          return 0;
      }
    });
    const setup = async () => {
      isLoading.value = true;
      await syncActiveOrgMembers.value();
      await syncPendingOrgInvitations.value();
      await syncPendingOrgMembers.value();
      isLoading.value = false;
    };
    const redirectIfNoAuthMethodSetup = async () => {
      if (!memberLoginOption.value) {
        await syncMemberLoginOption.value(currentOrganization.id);
      }
      if (!memberLoginOption.value) {
        await ctx.root.$router.push(
          `/${Pages.MAIN}/${currentOrganization.id}/settings/login-option`
        );
      }
    };
    const showInviteUsersModal = () => {
      ctx.refs.inviteUsersDialog.open();
    };
    const cancelInviteUsersModal = () => {
      ctx.refs.inviteUsersDialog.close();
    };
    const showSuccessModal = () => {
      ctx.refs.inviteUsersDialog.close();
      successTitle = `Invited ${sentInvitations.value.length} Team Members`;
      successText =
        "Once team members accept the invitation and log in, you will need to approve their access to this account.";
      ctx.refs.successDialog.open();
    };
    const resend = async (invitation: Invitation) => {
      await resendInvitation.value(invitation);
      showSuccessModal();
    };
    const showConfirmRemoveInviteModal = (invitation: Invitation) => {
      confirmActionTitle = ctx.root.$t("confirmRemoveInviteTitle").toString();
      confirmActionText = `Remove the invitation to sent to <strong>${invitation.recipientEmail}</strong>?`;
      invitationToBeRemoved.value = invitation;
      confirmHandler = removeInvite;
      primaryActionText = "Remove";
      secondaryActionText = "Cancel";
      primaryActionType = "error";
      ctx.refs.confirmActionDialog.open();
    };
    const showConfirmApproveModal = (member: Member) => {
      confirmActionTitle = ctx.root.$t("confirmApproveMemberTitle").toString();
      confirmActionText = `Approve account access for <strong>${member?.user?.firstname} ${member?.user?.lastname}</strong>?`;
      memberToBeApproved.value = member;
      confirmHandler = approve;
      primaryActionText = "Approve";
      secondaryActionText = "Cancel";
      primaryActionType = "primary";
      ctx.refs.confirmActionDialog.open();
    };
    const removeInvite = async () => {
      await deleteInvitation.value(invitationToBeRemoved.value.id);
      ctx.refs.confirmActionDialog.close();
    };
    const approve = async () => {
      await updateMember({
        memberId: memberToBeApproved.value.id,
        status: MembershipStatus.Active,
      });
      ctx.root.$store.commit("updateHeader");
      ctx.refs.confirmActionDialog.close();
    };
    const setAppliedFilterValue = (filter: SearchFilterParam[]) => {
      appliedFilterValue.value = filter[0].appliedFilterValue;
    };
    const filteredTeamMembersCount = (count: number) => {
      teamMembersCount.value = count;
    };
    const filteredPendingMembersCount = (count: number) => {
      pendingMembersCount.value = count;
    };
    onMounted(async () => {
      setAccountChangedHandler(setup);
      await setup();
    });
    return {
      currentUser,
      resending,
      sentInvitations,
      pendingOrgMembers,
      memberLoginOption,
      currentBusiness,
      resendInvitation,
      deleteInvitation,
      syncPendingOrgInvitations,
      syncPendingOrgMembers,
      syncActiveOrgMembers,
      syncMemberLoginOption,
      tab,
      isLoading,
      memberToBeApproved,
      invitationToBeRemoved,
      sentInvitations,
      memberLoginOption,
      syncMemberLoginOption,
      resendInvitation,
      deleteInvitation,
      syncPendingOrgMembers,
      syncPendingOrgInvitations,
      syncActiveOrgMembers,
      currentUser,
      appliedFilterValue,
      teamMembersCount,
      pendingMembersCount,
      searchFilter,
      pendingOrgMembers,
      $refs,
      pendingApprovalCount,
      isBCEIDUser,
      filteredMembersCount,
      setup,
      redirectIfNoAuthMethodSetup,
      showInviteUsersModal,
      cancelInviteUsersModal,
      showSuccessModal,
      resend,
      showConfirmRemoveInviteModal,
      showConfirmApproveModal,
      removeInvite,
      approve,
      setAppliedFilterValue,
      filteredTeamMembersCount,
      filteredPendingMembersCount,
    };
  },
});
