import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import {
  BulkUsersFailed,
  BulkUsersSuccess,
  Member,
} from "@/models/Organization";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { mapActions, mapState } from "vuex";
import AddUsersForm from "@/components/auth/account-settings/team-management/AddUsersForm.vue";
import AddUsersSuccess from "@/components/auth/account-settings/team-management/AddUsersSuccess.vue";
import MemberDataTable from "@/components/auth/account-settings/team-management/MemberDataTable.vue";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import PasswordReset from "@/components/auth/account-settings/team-management/PasswordReset.vue";
import { SearchFilterCodes } from "@/util/constants";
import SearchFilterInput from "@/components/auth/common/SearchFilterInput.vue";
import { SearchFilterParam } from "@/models/searchfilter";
import TeamManagementMixin from "@/components/auth/mixins/TeamManagementMixin.vue";
import { User } from "@/models/user";
export default defineComponent({
  components: {
    PasswordReset,
    MemberDataTable,
    ModalDialog,
    AddUsersForm,
    AddUsersSuccess,
    SearchFilterInput,
  },
  props: { orgId: { default: "", type: String } },
  setup(props, ctx) {
    const createdUsers = computed(() => ctx.root.$store.state.org.createdUsers);
    const failedUsers = computed(() => ctx.root.$store.state.org.failedUsers);
    const syncActiveOrgMembers = () =>
      ctx.root.$store.dispatch("org/syncActiveOrgMembers");
    const { orgId } = toRefs(props);
    const isLoading = ref(true);
    const syncActiveOrgMembers = ref<() => Member[]>(undefined);
    const createdUsers = ref<BulkUsersSuccess[]>(undefined);
    const failedUsers = ref<BulkUsersFailed[]>(undefined);
    const user = ref<User>({ firstname: "", lastname: "", username: "" });
    const action = ref("");
    const appliedFilterValue = ref<string>("");
    const teamMembersCount = ref(0);
    const searchFilter = ref<SearchFilterParam[]>([
      {
        id: SearchFilterCodes.USERNAME,
        placeholder: "Team Member",
        labelKey: "Team Member",
        appliedFilterValue: "",
        filterInput: "",
      },
    ]);
    const $refs = ref<{
      successDialog: ModalDialog;
      errorDialog: ModalDialog;
      confirmActionDialog: ModalDialog;
      confirmActionDialogWithQuestion: ModalDialog;
      addAnonUsersDialog: ModalDialog;
      addUsersSuccessDialog: ModalDialog;
      passwordResetDialog: ModalDialog;
      passwordResetSuccessDialog: ModalDialog;
    }>(undefined);
    const showAddUsersModal = () => {
      ctx.refs.addAnonUsersDialog.open();
    };
    const cancelAddUsersModal = () => {
      ctx.refs.addAnonUsersDialog.close();
    };
    const showPasswordResetErrorModal = () => {
      ctx.refs.passwordResetDialog.close();
      errorTitle = ctx.root.$t("passwordResetFailureTitle").toString();
      errorText = ctx.root.$t("passwordResetFailureText").toString();
      ctx.refs.errorDialog.open();
    };
    const showResetPasswordModal = (payload: User) => {
      user.value = payload;
      ctx.refs.passwordResetDialog.open();
    };
    const showUpdateModal = () => {
      ctx.refs.passwordResetDialog.close();
      action.value = "resetpassword";
      successTitle = `Password Reset`;
      ctx.refs.passwordResetSuccessDialog.open();
    };
    const showSuccessModal = () => {
      ctx.refs.addAnonUsersDialog.close();
      successTitle = `${createdUsers.value.length} Team Members Added`;
      if (createdUsers.value.length) {
        successTitle = `${createdUsers.value.length} of ${
          failedUsers.value.length + createdUsers.value.length
        } Team Members Added`;
      }
      ctx.refs.addUsersSuccessDialog.open();
    };
    const setAppliedFilterValue = (filter: SearchFilterParam[]) => {
      appliedFilterValue.value = filter[0].appliedFilterValue;
    };
    const filteredTeamMembersCount = (count: number) => {
      teamMembersCount.value = count;
    };
    onMounted(async () => {
      isLoading.value = false;
      await syncActiveOrgMembers.value();
    });
    return {
      createdUsers,
      failedUsers,
      syncActiveOrgMembers,
      isLoading,
      syncActiveOrgMembers,
      createdUsers,
      failedUsers,
      user,
      action,
      appliedFilterValue,
      teamMembersCount,
      searchFilter,
      $refs,
      showAddUsersModal,
      cancelAddUsersModal,
      showPasswordResetErrorModal,
      showResetPasswordModal,
      showUpdateModal,
      showSuccessModal,
      setAppliedFilterValue,
      filteredTeamMembersCount,
    };
  },
});
