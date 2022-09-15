import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
import {
  LDFlags,
  Pages,
  Role,
  StaffCreateAccountsTypes,
} from "@/util/constants";
import { mapActions, mapGetters, mapState } from "vuex";
import { Code } from "@/models/Code";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import { Organization } from "@/models/Organization";
import StaffActiveAccountsTable from "@/components/auth/staff/account-management/StaffActiveAccountsTable.vue";
import StaffCreateAccountModal from "@/components/auth/staff/account-management/StaffCreateAccountModal.vue";
import StaffModule from "@/store/modules/staff";
import StaffPendingAccountInvitationsTable from "@/components/auth/staff/account-management/StaffPendingAccountInvitationsTable.vue";
import StaffPendingAccountsTable from "@/components/auth/staff/account-management/StaffPendingAccountsTable.vue";
import StaffRejectedAccountsTable from "@/components/auth/staff/account-management/StaffRejectedAccountsTable.vue";
import { getModule } from "vuex-module-decorators";
import { namespace } from "vuex-class";
enum TAB_CODE {
  Active = "active-tab",
  PendingReview = "pending-review-tab",
  Rejected = "rejected-tab",
  Invitations = "invitations-tab",
  Suspended = "suspended-tab",
}
const CodesModule = namespace("codes");
const TaskModule = namespace("task");
export default defineComponent({
  components: {
    StaffActiveAccountsTable,
    StaffPendingAccountsTable,
    StaffRejectedAccountsTable,
    StaffPendingAccountInvitationsTable,
    StaffCreateAccountModal,
  },
  props: {},
  setup(_props, ctx) {
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const pendingInvitationsCount = computed(
      () => ctx.root.$store.getters["staff/pendingInvitationsCount"]
    );
    const suspendedReviewCount = computed(
      () => ctx.root.$store.getters["staff/suspendedReviewCount"]
    );
    const syncPendingInvitationOrgs = () =>
      ctx.root.$store.dispatch("staff/syncPendingInvitationOrgs");
    const syncSuspendedStaffOrgs = () =>
      ctx.root.$store.dispatch("staff/syncSuspendedStaffOrgs");
    const staffStore = ref(getModule(StaffModule, ctx.root.$store));
    const tab = ref(0);
    const currentUser = ref<KCUserProfile>(undefined);
    const syncRejectedStaffOrgs = ref<() => Organization[]>(undefined);
    const syncPendingInvitationOrgs = ref<() => Organization[]>(undefined);
    const syncSuspendedStaffOrgs = ref<() => Organization[]>(undefined);
    const pendingInvitationsCount = ref<number>(undefined);
    const suspendedReviewCount = ref<number>(undefined);
    const pagesEnum = ref(Pages);
    const $refs = ref<{
      staffCreateAccountDialog: any;
    }>(undefined);
    const tabs = ref([
      {
        id: 0,
        tabName: "Active",
        code: TAB_CODE.Active,
      },
      {
        id: 1,
        tabName: "Invitations",
        code: TAB_CODE.Invitations,
      },
      {
        id: 2,
        tabName: "Pending Review",
        code: TAB_CODE.PendingReview,
      },
      {
        id: 3,
        tabName: "Rejected",
        code: TAB_CODE.Rejected,
      },
      {
        id: 4,
        tabName: "Suspended",
        code: TAB_CODE.Suspended,
      },
    ]);
    const isGovmInviteEnable = computed((): boolean => {
      return LaunchDarklyService.getFlag(LDFlags.EnableGovmInvite) || false;
    });
    const canManageAccounts = computed(() => {
      return currentUser.value?.roles?.includes(Role.StaffManageAccounts);
    });
    const canCreateAccounts = computed(() => {
      return currentUser.value?.roles?.includes(Role.StaffCreateAccounts);
    });
    const canViewAccounts = computed(() => {
      return currentUser.value?.roles?.includes(Role.StaffViewAccounts);
    });
    const canSuspendAccounts = computed(() => {
      return (
        currentUser.value?.roles?.includes(Role.StaffSuspendAccounts) ||
        currentUser.value?.roles?.includes(Role.StaffViewAccounts)
      );
    });
    const openCreateAccount = () => {
      if (isGovmInviteEnable.value) {
        ctx.refs.staffCreateAccountDialog.open();
      } else {
        ctx.root.$router.push({ path: `/${Pages.STAFF_SETUP_ACCOUNT}` });
      }
    };
    const tabChange = async (tabIndex) => {
      const selected = tabs.value.filter((tab) => tab.id === tabIndex);
      if (selected[0]?.code === TAB_CODE.Invitations) {
        await syncPendingInvitationOrgs.value();
      }
    };
    onMounted(async () => {
      await getCodes();
      await syncTasks();
      await syncSuspendedStaffOrgs.value();
      if (canCreateAccounts.value) {
        await syncPendingInvitationOrgs.value();
      }
    });
    return {
      currentUser,
      pendingInvitationsCount,
      suspendedReviewCount,
      syncPendingInvitationOrgs,
      syncSuspendedStaffOrgs,
      staffStore,
      tab,
      currentUser,
      syncRejectedStaffOrgs,
      syncPendingInvitationOrgs,
      syncSuspendedStaffOrgs,
      pendingInvitationsCount,
      suspendedReviewCount,
      pagesEnum,
      $refs,
      tabs,
      isGovmInviteEnable,
      canManageAccounts,
      canCreateAccounts,
      canViewAccounts,
      canSuspendAccounts,
      openCreateAccount,
      tabChange,
    };
  },
});
