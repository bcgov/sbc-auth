import { defineComponent, computed, ref } from "@vue/composition-api";
import {
  AccountStatus,
  LoginSource,
  Pages,
  Permission,
  Role,
  SessionStorageKeys,
} from "@/util/constants";
import {
  Member,
  MembershipStatus,
  MembershipType,
  Organization,
} from "@/models/Organization";
import { mapActions, mapGetters, mapMutations, mapState } from "vuex";
import { AccountSettings } from "@/models/account-settings";
import CommonUtils from "@/util/common-util";
import Component from "vue-class-component";
import ConfigHelper from "@/util/config-helper";
import { Contact } from "@/models/contact";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import OrgModule from "@/store/modules/org";
import { User } from "@/models/user";
import UserModule from "@/store/modules/user";
import Vue from "vue";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const userProfile = computed(() => ctx.root.$store.state.user.userProfile);
    const userContact = computed(() => ctx.root.$store.state.user.userContact);
    const redirectAfterLoginUrl = computed(
      () => ctx.root.$store.state.user.redirectAfterLoginUrl
    );
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const currentAccountSettings = computed(
      () => ctx.root.$store.state.org.currentAccountSettings
    );
    const permissions = computed(() => ctx.root.$store.state.org.permissions);
    const needMissingBusinessDetailsRedirect = computed(
      () => ctx.root.$store.getters["org/needMissingBusinessDetailsRedirect"]
    );
    const loadUserInfo = () => ctx.root.$store.dispatch("user/loadUserInfo");
    const syncUserProfile = () =>
      ctx.root.$store.dispatch("user/syncUserProfile");
    const getUserProfile = () =>
      ctx.root.$store.dispatch("user/getUserProfile");
    const syncOrganization = () =>
      ctx.root.$store.dispatch("org/syncOrganization");
    const syncMembership = () => ctx.root.$store.dispatch("org/syncMembership");
    const resetCurrentOrganization = () =>
      ctx.root.$store.dispatch("org/resetCurrentOrganization");
    const userStore = ref(getModule(UserModule, ctx.root.$store));
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const currentUser = ref<KCUserProfile>(undefined);
    const userProfile = ref<User>(undefined);
    const userContact = ref<Contact>(undefined);
    const redirectAfterLoginUrl = ref<string>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const currentMembership = ref<Member>(undefined);
    const currentAccountSettings = ref<AccountSettings>(undefined);
    const permissions = ref<string[]>(undefined);
    const setCurrentAccountSettings =
      ref<(accountSettings: AccountSettings) => void>(undefined);
    const syncUserProfile = ref<() => void>(undefined);
    const syncOrganization =
      ref<(currentAccount: number) => Promise<Organization>>(undefined);
    const syncMembership =
      ref<(currentAccount: number) => Promise<Member>>(undefined);
    const resetCurrentOrganization = ref<() => Promise<void>>(undefined);
    const needMissingBusinessDetailsRedirect = ref<boolean>(undefined);
    const anyPendingRedirect = ref<boolean>(false);
    const getAccountFromSession = (): AccountSettings => {
      return JSON.parse(
        ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || "{}")
      );
    };
    const getNextPageUrl = (): string => {
      const dashboardUrl = `${ConfigHelper.getRegistryHomeURL()}dashboard`;
      let orgName = "";
      switch (currentUser.value?.loginSource) {
        case LoginSource.IDIR:
          orgName = encodeURIComponent(
            btoa(currentAccountSettings.value?.label)
          );
          if (currentUser.value.roles.includes(Role.Staff)) {
            return `/${Pages.SEARCH_BUSINESS}`;
          } else if (!userProfile.value?.userTerms?.isTermsOfUseAccepted) {
            return `/${Pages.USER_PROFILE_TERMS}`;
          } else if (
            currentOrganization.value &&
            currentOrganization.value.statusCode ===
              AccountStatus.PENDING_INVITE_ACCEPT
          ) {
            return `/${Pages.CREATE_GOVM_ACCOUNT}`;
          } else if (
            currentMembership.value &&
            currentMembership.value.membershipStatus ===
              MembershipStatus.Pending
          ) {
            return `/${Pages.PENDING_APPROVAL}/${orgName}`;
          } else if (
            currentOrganization.value &&
            currentOrganization.value.statusCode ===
              AccountStatus.PENDING_STAFF_REVIEW
          ) {
            return `/${Pages.SETUP_GOVM_ACCOUNT_SUCCESS}`;
          } else {
            return dashboardUrl;
          }
        case LoginSource.BCROS:
          let bcrosNextStep = "/";
          if (!userProfile.value?.userTerms?.isTermsOfUseAccepted) {
            bcrosNextStep = `/${Pages.USER_PROFILE_TERMS}`;
          } else if (
            currentOrganization.value &&
            currentMembership.value.membershipStatus === MembershipStatus.Active
          ) {
            if (
              currentMembership.value.membershipTypeCode ===
                MembershipType.Admin ||
              currentMembership.value.membershipTypeCode ===
                MembershipType.Coordinator
            ) {
              bcrosNextStep = `/${Pages.MAIN}/${currentOrganization.value.id}/settings/team-members`;
            } else {
              bcrosNextStep = ConfigHelper.getDirectorSearchURL();
            }
          }
          return bcrosNextStep;
        case LoginSource.BCSC:
          let nextStep = "/";
          orgName = encodeURIComponent(
            btoa(currentAccountSettings.value?.label)
          );
          if (!userProfile.value?.userTerms?.isTermsOfUseAccepted) {
            nextStep = `/${Pages.USER_PROFILE_TERMS}`;
          } else if (!currentOrganization.value && !currentMembership.value) {
            nextStep = `/${Pages.CREATE_ACCOUNT}`;
          } else if (
            currentOrganization.value &&
            currentMembership.value.membershipStatus === MembershipStatus.Active
          ) {
            nextStep = dashboardUrl;
          } else if (
            currentMembership.value.membershipStatus ===
            MembershipStatus.Pending
          ) {
            nextStep = `/${Pages.PENDING_APPROVAL}/${orgName}`;
          } else {
            nextStep = dashboardUrl;
          }
          return nextStep;
        case LoginSource.BCEID:
          let bceidNextStep = "/";
          orgName = encodeURIComponent(
            btoa(currentAccountSettings.value?.label)
          );
          let invToken = ConfigHelper.getFromSession(
            SessionStorageKeys.InvitationToken
          );
          const affidavitNeeded = ConfigHelper.getFromSession(
            SessionStorageKeys.AffidavitNeeded
          );
          if (invToken) {
            const affidavitNeededURL =
              affidavitNeeded === "true" ? `?affidavit=true` : "";
            bceidNextStep = `/${Pages.CONFIRM_TOKEN}/${invToken}${affidavitNeededURL}`;
            ConfigHelper.removeFromSession(SessionStorageKeys.InvitationToken);
            ConfigHelper.removeFromSession(SessionStorageKeys.AffidavitNeeded);
          } else if (!userProfile.value?.userTerms?.isTermsOfUseAccepted) {
            bceidNextStep = `/${Pages.USER_PROFILE_TERMS}`;
          } else if (!currentOrganization.value && !currentMembership.value) {
            let isExtraProv = ConfigHelper.getFromSession(
              SessionStorageKeys.ExtraProvincialUser
            );
            if (isExtraProv) {
              bceidNextStep = `/${Pages.CREATE_NON_BCSC_ACCOUNT}`;
            } else {
              bceidNextStep = `/${Pages.CHOOSE_AUTH_METHOD}`;
            }
          } else if (
            currentOrganization.value &&
            currentOrganization.value.statusCode ===
              AccountStatus.PENDING_STAFF_REVIEW
          ) {
            bceidNextStep = `/${Pages.PENDING_APPROVAL}/${orgName}/true`;
          } else if (
            currentOrganization.value &&
            currentMembership.value.membershipStatus === MembershipStatus.Active
          ) {
            bceidNextStep = dashboardUrl;
          } else if (
            [
              MembershipStatus.PendingStaffReview,
              MembershipStatus.Pending,
            ].includes(currentMembership.value?.membershipStatus)
          ) {
            bceidNextStep = `/${Pages.PENDING_APPROVAL}/${orgName}`;
          } else {
            bceidNextStep = dashboardUrl;
          }
          return `${bceidNextStep}`;
        default:
          return dashboardUrl;
      }
    };
    const redirectAfterLogin = () => {
      if (redirectAfterLoginUrl.value) {
        if (CommonUtils.isUrl(redirectAfterLoginUrl.value)) {
          window.location.href = decodeURIComponent(
            redirectAfterLoginUrl.value
          );
        } else {
          ctx.root.$router.push(`/${redirectAfterLoginUrl.value}`);
        }
      } else {
        ctx.root.$router.push(getNextPageUrl());
      }
    };
    const redirectTo = (target: string): void => {
      if (CommonUtils.isUrl(target)) {
        window.location.assign(target);
      } else {
        if (ctx.root.$route.path !== target) {
          ctx.root.$router.push(target);
        }
      }
    };
    const syncUser = async () => {
      await syncUserProfile.value();
      setCurrentAccountSettings.value(getAccountFromSession());
      if (currentAccountSettings.value) {
        await syncMembership.value(currentAccountSettings.value.id);
        if (
          currentMembership.value.membershipStatus === MembershipStatus.Active
        ) {
          await syncOrganization.value(currentAccountSettings.value.id);
        }
        if (
          currentMembership.value.membershipStatus !== MembershipStatus.Active
        ) {
          await resetCurrentOrganization.value();
        }
      }
    };
    const accountFreezeRedirect = () => {
      if (
        currentOrganization.value?.statusCode === AccountStatus.NSF_SUSPENDED
      ) {
        anyPendingRedirect.value = true;
        console.log(
          "Redirecting user to Account Freeze message since the account is temporarly suspended."
        );
        if (
          permissions.value.some((code) => code === Permission.MAKE_PAYMENT)
        ) {
          ctx.root.$router.push(`/${Pages.ACCOUNT_FREEZE_UNLOCK}`);
        } else {
          ctx.root.$router.push(`/${Pages.ACCOUNT_FREEZE}`);
        }
      } else {
        if (ctx.root.$route.name?.search("account-freeze") > -1) {
          anyPendingRedirect.value = true;
          ctx.root.$router.push(
            `${Pages.MAIN}/${currentOrganization.value.id}/${Pages.ACCOUNT_SETTINGS}`
          );
        }
      }
    };
    const accountPendingRedirect = () => {
      if (needMissingBusinessDetailsRedirect.value) {
        anyPendingRedirect.value = true;
        ctx.root.$router.push(`/${Pages.UPDATE_ACCOUNT}`);
      } else if (
        currentMembership.value.membershipStatus === MembershipStatus.Active &&
        ctx.root.$route.path.indexOf(Pages.PENDING_APPROVAL) > 0
      ) {
        anyPendingRedirect.value = false;
      } else if (
        currentMembership.value.membershipStatus === MembershipStatus.Pending
      ) {
        anyPendingRedirect.value = true;
        const label = encodeURIComponent(
          btoa(currentAccountSettings.value?.label)
        );
        ctx.root.$router.push(`/${Pages.PENDING_APPROVAL}/${label}`);
      }
    };
    return {
      currentUser,
      userProfile,
      userContact,
      redirectAfterLoginUrl,
      currentOrganization,
      currentMembership,
      currentAccountSettings,
      permissions,
      needMissingBusinessDetailsRedirect,
      loadUserInfo,
      syncUserProfile,
      getUserProfile,
      syncOrganization,
      syncMembership,
      resetCurrentOrganization,
      userStore,
      orgStore,
      currentUser,
      userProfile,
      userContact,
      redirectAfterLoginUrl,
      currentOrganization,
      currentMembership,
      currentAccountSettings,
      permissions,
      setCurrentAccountSettings,
      syncUserProfile,
      syncOrganization,
      syncMembership,
      resetCurrentOrganization,
      needMissingBusinessDetailsRedirect,
      anyPendingRedirect,
      getAccountFromSession,
      getNextPageUrl,
      redirectAfterLogin,
      redirectTo,
      syncUser,
      accountFreezeRedirect,
      accountPendingRedirect,
    };
  },
});
