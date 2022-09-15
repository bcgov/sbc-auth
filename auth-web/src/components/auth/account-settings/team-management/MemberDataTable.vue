import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import { AccessType, LoginSource, Permission } from "@/util/constants";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import {
  Member,
  MembershipStatus,
  MembershipType,
  Organization,
  RoleInfo,
} from "@/models/Organization";
import { mapActions, mapState } from "vuex";
import { Business } from "@/models/business";
import CommonUtils from "@/util/common-util";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
export interface ChangeRolePayload {
  member: Member;
  targetRole: string;
}
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: { userNamefilterText: { default: "", type: String } },
  setup(props, ctx) {
    const businesses = computed(
      () => ctx.root.$store.state.business.businesses
    );
    const activeOrgMembers = computed(
      () => ctx.root.$store.state.org.activeOrgMembers
    );
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const permissions = computed(() => ctx.root.$store.state.org.permissions);
    const roleInfos = computed(() => ctx.root.$store.state.user.roleInfos);
    const getRoleInfo = () => ctx.root.$store.dispatch("user/getRoleInfo");
    const resetOTPAuthenticator = () =>
      ctx.root.$store.dispatch("user/resetOTPAuthenticator");
    const { userNamefilterText } = toRefs(props);
    const businesses = ref<Business[]>(undefined);
    const activeOrgMembers = ref<Member[]>(undefined);
    const currentMembership = ref<Member>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const getRoleInfo = ref<() => Promise<RoleInfo[]>>(undefined);
    const resetOTPAuthenticator = ref<(username: string) => any>(undefined);
    const roleInfos = ref<RoleInfo[]>(undefined);
    const SNACKBAR_TIMEOUT = ref<number>(3000);
    const confirmResetAuthDialog = ref(false);
    const showResetSnackBar = ref(false);
    const selectedUserForReset = ref(undefined);
    const loginSource = ref<LoginSource>(undefined);
    const permissions = ref<string[]>(undefined);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const $refs = ref<{
      resetAuthenticatorDialog: ModalDialog;
    }>(undefined);
    const headerMembers = ref([
      {
        text: "Team Member",
        align: "left",
        sortable: true,
        value: "name",
      },
      {
        text: "Role",
        align: "left",
        sortable: true,
        value: "role",
      },
      {
        text: "Last Activity",
        align: "left",
        sortable: true,
        value: "lastActive",
      },
      {
        text: "Actions",
        align: "right",
        value: "action",
        sortable: false,
        width: "120",
      },
    ]);
    const authHeaderMember = ref({
      text: "Authentication",
      align: "left",
      sortable: false,
      value: "authentication",
    });
    const loginSourceEnum = computed((): typeof LoginSource => {
      return LoginSource;
    });
    const indexedOrgMembers = computed(() => {
      let orgMembers = [];
      if (userNamefilterText.value) {
        orgMembers = activeOrgMembers.value.filter((element) => {
          const username = `${element.user?.firstname || ""} ${
            element.user?.lastname || ""
          }`.trim();
          const found = username.match(
            new RegExp(userNamefilterText.value, "i")
          );
          if (found?.length) {
            return element;
          }
        });
        filteredMembersCount(orgMembers.length);
      } else {
        orgMembers = activeOrgMembers.value;
      }
      return orgMembers.map((item, index) => {
        item.roleDisplayName = roleInfos.value.find(
          (role) => role.name === item.membershipTypeCode
        ).displayName;
        return {
          index,
          ...item,
        };
      });
    });
    const anonAccount = computed((): boolean => {
      return currentOrganization.value?.accessType === AccessType.ANONYMOUS;
    });
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const filteredMembersCount = (count: number) => {
      return count;
    };
    const isRoleEnabled = (role: RoleInfo, member: Member): boolean => {
      if (
        member?.user?.loginSource === LoginSource.BCEID &&
        role.name === MembershipType.Admin
      ) {
        return false;
      }
      switch (currentMembership.value.membershipTypeCode) {
        case MembershipType.Admin:
          return true;
        case MembershipType.Coordinator:
          if (role.name !== MembershipType.Admin) {
            return true;
          }
          return false;
        default:
          return false;
      }
    };
    const canChangeRole = (memberBeingChanged: Member): boolean => {
      if (
        currentMembership.value.membershipStatus !== MembershipStatus.Active
      ) {
        return false;
      }
      switch (currentMembership.value.membershipTypeCode) {
        case MembershipType.Admin:
          if (!isOwnMembership(memberBeingChanged)) {
            return true;
          }
          if (isOwnMembership(memberBeingChanged) && ownerCount() > 1) {
            return true;
          }
          return false;
        case MembershipType.Coordinator:
          return (
            isOwnMembership(memberBeingChanged) ||
            memberBeingChanged.membershipTypeCode === MembershipType.User
          );
        default:
          return false;
      }
    };
    const canRemove = (memberToRemove: Member): boolean => {
      if (
        currentMembership.value.user?.username === memberToRemove.user.username
      ) {
        return false;
      }
      if (currentMembership.value.membershipTypeCode === MembershipType.User) {
        return false;
      }
      if (
        currentMembership.value.membershipTypeCode ===
          MembershipType.Coordinator &&
        memberToRemove.membershipTypeCode === MembershipType.Coordinator
      ) {
        return false;
      }
      if (memberToRemove.membershipTypeCode === MembershipType.Admin) {
        if (
          currentMembership.value.membershipTypeCode === MembershipType.Admin
        ) {
          return true;
        } else {
          return false;
        }
      }
      return true;
    };
    const canLeave = (member: Member): boolean => {
      if (currentMembership.value.user?.username !== member.user.username) {
        return false;
      }
      return true;
    };
    const canResetAuthenticator = (member: Member): boolean => {
      return member.user.loginSource === LoginSource.BCEID;
    };
    const ownerCount = (): number => {
      return activeOrgMembers.value.filter(
        (member) => member.membershipTypeCode === MembershipType.Admin
      ).length;
    };
    const customSortActive = (items, index, isDescending) => {
      const isDesc = isDescending.length > 0 && isDescending[0];
      switch (index[0]) {
        case "name":
          items.sort((a, b) => {
            if (isDesc) {
              return a.user.firstname < b.user.firstname ? -1 : 1;
            } else {
              return b.user.firstname < a.user.firstname ? -1 : 1;
            }
          });
          break;
        case "role":
          items.sort((a, b) => {
            if (isDesc) {
              return a.membershipTypeCode < b.membershipTypeCode ? -1 : 1;
            } else {
              return b.membershipTypeCode < a.membershipTypeCode ? -1 : 1;
            }
          });
          break;
        case "lastActive":
          items.sort((a, b) => {
            if (isDesc) {
              return a.user.modified < b.user.modified ? -1 : 1;
            } else {
              return b.user.modified < a.user.modified ? -1 : 1;
            }
          });
      }
      return items;
    };
    const isAnonymousAccount = (): boolean => {
      return (
        currentOrganization.value &&
        currentOrganization.value.accessType === AccessType.ANONYMOUS
      );
    };
    const isRegularAccount = (): boolean => {
      return (
        currentOrganization.value &&
        [AccessType.ANONYMOUS.valueOf(), AccessType.GOVM.valueOf()].indexOf(
          currentOrganization.value.accessType
        ) < 0
      );
    };
    const canViewLoginSource = (): boolean => {
      return [Permission.VIEW_USER_LOGINSOURCE].some((per) =>
        permissions.value.includes(per)
      );
    };
    const confirmRemoveMember = (member: Member) => {};
    const resetPassword = (member: Member) => {
      return member.user;
    };
    const confirmChangeRole = (
      member: Member,
      targetRole: string
    ): ChangeRolePayload => {
      return {
        member,
        targetRole,
      };
    };
    const confirmLeaveTeam = (member: Member) => {
      if (
        member.membershipTypeCode === MembershipType.Admin &&
        ownerCount() === 1
      ) {
        ctx.emit("single-owner-error");
      } else {
        ctx.emit("confirm-leave-team");
      }
    };
    const isOwnMembership = (member: Member) => {
      return (
        currentMembership.value?.user?.username === member.user.username ||
        false
      );
    };
    const selectedUsername = () => {
      return `${selectedUserForReset.value?.user?.firstname} ${selectedUserForReset.value?.user?.lastname}`;
    };
    const showResetAuthenticatorDialog = (item) => {
      selectedUserForReset.value = item;
      ctx.refs.resetAuthenticatorDialog.open();
    };
    const resetAuthenticator = async () => {
      try {
        await resetOTPAuthenticator.value(
          selectedUserForReset.value?.user?.username
        );
        showResetSnackBar.value = true;
        ctx.refs.resetAuthenticatorDialog.close();
        setTimeout(() => {
          selectedUserForReset.value = undefined;
        }, SNACKBAR_TIMEOUT.value);
      } catch (error) {
        console.error(error);
      }
    };
    const closeResetAuthDialog = () => {
      ctx.refs.resetAuthenticatorDialog.close();
      selectedUserForReset.value = undefined;
    };
    onMounted(async () => {
      if (!roleInfos.value) {
        await getRoleInfo.value();
      }
      if (isRegularAccount() && canViewLoginSource()) {
        headerMembers.value.splice(1, 0, authHeaderMember.value);
      }
    });
    return {
      businesses,
      activeOrgMembers,
      currentMembership,
      currentOrganization,
      permissions,
      roleInfos,
      getRoleInfo,
      resetOTPAuthenticator,
      businesses,
      activeOrgMembers,
      currentMembership,
      currentOrganization,
      getRoleInfo,
      resetOTPAuthenticator,
      roleInfos,
      SNACKBAR_TIMEOUT,
      confirmResetAuthDialog,
      showResetSnackBar,
      selectedUserForReset,
      loginSource,
      permissions,
      formatDate,
      $refs,
      headerMembers,
      authHeaderMember,
      loginSourceEnum,
      indexedOrgMembers,
      anonAccount,
      getIndexedTag,
      filteredMembersCount,
      isRoleEnabled,
      canChangeRole,
      canRemove,
      canLeave,
      canResetAuthenticator,
      ownerCount,
      customSortActive,
      isAnonymousAccount,
      isRegularAccount,
      canViewLoginSource,
      confirmRemoveMember,
      resetPassword,
      confirmChangeRole,
      confirmLeaveTeam,
      isOwnMembership,
      selectedUsername,
      showResetAuthenticatorDialog,
      resetAuthenticator,
      closeResetAuthDialog,
    };
  },
});
