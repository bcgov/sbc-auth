import { defineComponent, computed, ref } from "@vue/composition-api";
import { AccessType, LoginSource, SessionStorageKeys } from "@/util/constants";
import { Component, Prop, Vue } from "vue-property-decorator";
import {
  Member,
  MembershipStatus,
  MembershipType,
  Organization,
  PendingUserRecord,
  UpdateMemberPayload,
} from "@/models/Organization";
import MemberDataTable, {
  ChangeRolePayload,
} from "@/components/auth/account-settings/team-management/MemberDataTable.vue";
import { mapActions, mapState } from "vuex";
import { Business } from "@/models/business";
import ConfigHelper from "@/util/config-helper";
import { Event } from "@/models/event";
import { EventBus } from "@/event-bus";
import { Invitation } from "@/models/Invitation";
import InvitationsDataTable from "@/components/auth/account-settings/team-management/InvitationsDataTable.vue";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import OrgModule from "@/store/modules/org";
import PendingMemberDataTable from "@/components/auth/account-settings/team-management/PendingMemberDataTable.vue";
import UserModule from "@/store/modules/user";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const updateMember = () => ctx.root.$store.dispatch("org/updateMember");
    const leaveTeam = () => ctx.root.$store.dispatch("org/leaveTeam");
    const dissolveTeam = () => ctx.root.$store.dispatch("org/dissolveTeam");
    const deleteUser = () => ctx.root.$store.dispatch("org/deleteUser");
    const userStore = ref(getModule(UserModule, ctx.root.$store));
    const successTitle = ref<string>("");
    const successText = ref<string>("");
    const errorTitle = ref<string>("");
    const errorText = ref<string>("");
    const memberToBeRemoved = ref<Member>(undefined);
    const roleChangeToAction = ref<ChangeRolePayload>(undefined);
    const confirmActionTitle = ref<string>("");
    const confirmActionText = ref<string>("");
    const primaryActionText = ref<string>("");
    const primaryActionType = ref<string>("");
    const secondaryActionText = ref("Cancel");
    const confirmHandler = ref<(modal: ModalDialog) => void>(undefined);
    const currentMembership = ref<Member>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const updateMember =
      ref<(updateMemberPayload: UpdateMemberPayload) => void>(undefined);
    const deleteUser = ref<(userName: string) => void>(undefined);
    const leaveTeam = ref<(memberId: number) => void>(undefined);
    const dissolveTeam = ref<() => void>(undefined);
    const currentUser = ref<KCUserProfile>(undefined);
    const notifyUser = ref(true);
    const modal = ref<ModalDialog>(undefined);
    const isAccountGovM = computed((): boolean => {
      return currentOrganization.value.accessType === AccessType.GOVM;
    });
    const inviteUserFormText = computed((): string => {
      return isAccountGovM.value
        ? ctx.root.$t("inviteUsersFormTextGovM").toString()
        : ctx.root.$t("inviteUsersFormText").toString();
    });
    const showConfirmRemoveModal = (
      member: Member,
      confirmActionDialog: ModalDialog
    ) => {
      modal.value = confirmActionDialog;
      if (member.membershipStatus === MembershipStatus.Pending) {
        confirmActionTitle.value = ctx.root
          .$t("confirmDenyMemberTitle")
          .toString();
        confirmActionText.value = `Deny account access to <strong>${member?.user?.firstname} ${member?.user?.lastname}</strong?`;
        confirmHandler.value = deny;
        primaryActionText.value = "Deny";
        primaryActionType.value = "error";
      } else {
        confirmActionTitle.value = ctx.root
          .$t("confirmRemoveMemberTitle")
          .toString();
        confirmActionText.value = `Remove team member <strong>${member?.user?.firstname} ${member?.user?.lastname}</strong> from this account?`;
        confirmHandler.value = removeMember;
        primaryActionText.value = "Remove";
        primaryActionType.value = "error";
      }
      memberToBeRemoved.value = member;
      confirmActionDialog.open();
    };
    const showConfirmChangeRoleModal = (
      payload: ChangeRolePayload,
      confirmActionDialogWithQuestion: ModalDialog
    ) => {
      if (
        payload.member.membershipTypeCode.toString() ===
        payload.targetRole.toString()
      ) {
        return;
      }
      const username = `${payload.member?.user?.firstname || ""} ${
        payload.member?.user?.lastname || ""
      }`.trim();
      modal.value = confirmActionDialogWithQuestion;
      confirmActionTitle.value = ctx.root
        .$t("confirmRoleChangeTitle")
        .toString();
      confirmActionText.value = `Change <strong>${username}</strong>'s role to ${payload.targetRole}?`;
      roleChangeToAction.value = payload;
      confirmHandler.value = changeRole;
      primaryActionText.value = "Change";
      primaryActionType.value = "primary";
      confirmActionDialogWithQuestion.open();
    };
    const showConfirmLeaveTeamModal = (confirmActionDialog: ModalDialog) => {
      modal.value = confirmActionDialog;
      confirmActionTitle.value = ctx.root
        .$t("confirmLeaveTeamTitle")
        .toString();
      confirmActionText.value = ctx.root.$t("confirmLeaveTeamText").toString();
      confirmHandler.value = leave;
      primaryActionText.value = "Leave";
      confirmActionDialog.open();
    };
    const showConfirmDissolveModal = (confirmActionDialog: ModalDialog) => {
      modal.value = confirmActionDialog;
      confirmActionTitle.value = ctx.root
        .$t("confirmDissolveTeamTitle")
        .toString();
      confirmActionText.value = ctx.root
        .$t("confirmDissolveTeamText")
        .toString();
      confirmHandler.value = dissolve;
      primaryActionText.value = "Dissolve";
      confirmActionDialog.open();
    };
    const showSingleOwnerErrorModal = (errorDialog: ModalDialog) => {
      modal.value = errorDialog;
      errorTitle.value = ctx.root.$t("singleOwnerErrorTitle").toString();
      errorText.value = ctx.root.$t("singleOwnerErrorText").toString();
      errorDialog.open();
    };
    const close = (modal: ModalDialog) => {
      modal.close();
    };
    const removeMember = async () => {
      if (isAnonymousUser()) {
        await deleteUser.value(memberToBeRemoved.value.user.username);
      } else {
        await updateMember.value({
          memberId: memberToBeRemoved.value.id,
          status: MembershipStatus.Inactive,
        });
      }
      modal.value.close();
    };
    const isAnonymousUser = (): boolean => {
      return currentUser.value?.loginSource === LoginSource.BCROS;
    };
    const changeRole = async () => {
      await updateMember.value({
        memberId: roleChangeToAction.value.member.id,
        role: roleChangeToAction.value.targetRole.toString().toUpperCase(),
        notifyUser:
          currentUser.value?.loginSource !== LoginSource.BCROS
            ? notifyUser.value
            : false,
      });
      modal.value.close();
    };
    const deny = async () => {
      await updateMember.value({
        memberId: memberToBeRemoved.value.id,
        status: MembershipStatus.Rejected,
      });
      ctx.root.$store.commit("updateHeader");
      modal.value.close();
    };
    const leave = async () => {
      if (isAnonymousUser()) {
        await deleteUser.value(currentMembership.value.user.username);
      } else {
        await leaveTeam.value(currentMembership.value.id);
      }
      modal.value.close();
      ctx.root.$store.commit("updateHeader");
      ctx.root.$router.push("/leaveteam");
    };
    const dissolve = async () => {
      await dissolveTeam.value();
      await leaveTeam.value(currentMembership.value.id);
      modal.value.close();
      ctx.root.$store.commit("updateHeader");
      const event: Event = {
        message: "Dissolved the account",
        type: "error",
        timeout: 1000,
      };
      EventBus.$emit("show-toast", event);
      ConfigHelper.removeFromSession(SessionStorageKeys.CurrentAccount);
      ctx.root.$router.push("/");
    };
    return {
      currentMembership,
      currentOrganization,
      currentUser,
      updateMember,
      leaveTeam,
      dissolveTeam,
      deleteUser,
      userStore,
      successTitle,
      successText,
      errorTitle,
      errorText,
      memberToBeRemoved,
      roleChangeToAction,
      confirmActionTitle,
      confirmActionText,
      primaryActionText,
      primaryActionType,
      secondaryActionText,
      confirmHandler,
      currentMembership,
      currentOrganization,
      updateMember,
      deleteUser,
      leaveTeam,
      dissolveTeam,
      currentUser,
      notifyUser,
      modal,
      isAccountGovM,
      inviteUserFormText,
      showConfirmRemoveModal,
      showConfirmChangeRoleModal,
      showConfirmLeaveTeamModal,
      showConfirmDissolveModal,
      showSingleOwnerErrorModal,
      close,
      removeMember,
      isAnonymousUser,
      changeRole,
      deny,
      leave,
      dissolve,
    };
  },
});
