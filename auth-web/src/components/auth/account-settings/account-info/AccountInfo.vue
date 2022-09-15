import {
  defineComponent,
  ref,
  computed,
  onMounted,
} from "@vue/composition-api";
import {
  AccountStatus,
  Pages,
  Permission,
  Role,
  SessionStorageKeys,
} from "@/util/constants";
import { Component, Mixins } from "vue-property-decorator";
import {
  CreateRequestBody,
  OrgBusinessType,
  Organization,
} from "@/models/Organization";
import AccountAccessType from "@/components/auth/account-settings/account-info/AccountAccessType.vue";
import AccountBusinessTypePicker from "@/components/auth/common/AccountBusinessTypePicker.vue";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import AccountDetails from "@/components/auth/account-settings/account-info/AccountDetails.vue";
import AccountMailingAddress from "@/components/auth/account-settings/account-info/AccountMailingAddress.vue";
import AccountMixin from "@/components/auth/mixins/AccountMixin.vue";
import { AccountSettings } from "@/models/account-settings";
import { Address } from "@/models/address";
import { Code } from "@/models/Code";
import ConfigHelper from "@/util/config-helper";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import LinkedBCOLBanner from "@/components/auth/common/LinkedBCOLBanner.vue";
import ModalDialog from "../../common/ModalDialog.vue";
import OrgAdminContact from "@/components/auth/account-settings/account-info/OrgAdminContact.vue";
import { namespace } from "vuex-class";
const CodesModule = namespace("codes");
const OrgModule = namespace("org");
const userModule = namespace("user");
export default defineComponent({
  components: {
    OrgAdminContact,
    LinkedBCOLBanner,
    ModalDialog,
    AccountBusinessTypePicker,
    AccountDetails,
    AccountMailingAddress,
    AccountAccessType,
  },
  props: {},
  setup(_props, ctx) {
    const dialogTitle = ref<string>("");
    const dialogText = ref<string>("");
    const selectedSuspensionReasonCode = ref<string>("");
    const suspensionCompleteDialogText = ref<string>("");
    const isSuspensionReasonFormValid = ref<boolean>(false);
    const addressChanged = ref(false);
    const originalAddress = ref<Address>(undefined);
    const errorMessage = ref<string>("");
    const isBaseAddressValid = ref<boolean>(false);
    const isCompleteAccountInfo = ref(true);
    const accountDetails = ref<OrgBusinessType>({});
    const isAddressViewOnly = ref(true);
    const isAccountInfoViewOnly = ref(true);
    const isAccessTypeViewOnly = ref(true);
    const $refs = ref<{
      editAccountForm: HTMLFormElement;
      mailingAddress: HTMLFormElement;
      suspendAccountDialog: ModalDialog;
      suspensionCompleteDialog: ModalDialog;
      suspensionReasonForm: HTMLFormElement;
      accountBusinessTypePickerRef: HTMLFormElement;
    }>(undefined);
    const suspensionSelectRules = ref([
      (v) => !!v || "A reason for suspension is required",
    ]);
    const isStaff = computed((): boolean => {
      return currentUser.roles.includes(Role.Staff);
    });
    const isSuspendButtonVisible = computed((): boolean => {
      return (
        (currentOrganization.statusCode === AccountStatus.ACTIVE ||
          currentOrganization.statusCode === AccountStatus.SUSPENDED) &&
        currentUser.roles.includes(Role.StaffSuspendAccounts)
      );
    });
    const editAccountUrl = computed(() => {
      return Pages.EDIT_ACCOUNT_TYPE;
    });
    const canChangeAccessType = computed((): boolean => {
      return currentUser.roles.includes(Role.StaffManageAccounts);
    });
    const baseAddress = computed({
      get() {
        return currentOrgAddress;
      },
      set(address) {
        setCurrentOrganizationAddress(address);
      },
    });
    const nameChangeNotAllowed = computed(() => {
      return anonAccount || isGovmAccount;
    });
    const isAddressEditable = computed((): boolean => {
      return [Permission.CHANGE_ADDRESS].some((per) =>
        permissions.includes(per)
      );
    });
    const isAdminContactViewable = computed((): boolean => {
      return [Permission.VIEW_ADMIN_CONTACT].some((per) =>
        permissions.includes(per)
      );
    });
    const isAccountStatusActive = computed((): boolean => {
      return currentOrganization.statusCode === AccountStatus.ACTIVE;
    });
    const setAccountDetails = () => {
      accountDetails.value = {
        ...accountDetails.value,
        name: currentOrganization?.name || "",
        branchName: currentOrganization?.branchName || "",
        businessType: currentOrganization.businessType || "",
        businessSize: currentOrganization?.businessSize || "",
      };
    };
    const setup = async () => {
      setAccountDetails();
      await syncAddress();
      if (!anonAccount) {
        originalAddress.value = currentOrgAddress;
        if (Object.keys(currentOrgAddress).length === 0) {
          isCompleteAccountInfo.value = false;
          errorMessage.value = isAddressEditable.value
            ? "Your account info is incomplete. Please enter your address in order to proceed."
            : "This accounts profile is incomplete. You will not be able to proceed until an account administrator entered the missing information for this account.";
          ctx.refs.editAccountForm?.validate();
          ctx.refs.mailingAddress?.triggerValidate();
        }
      } else {
        baseAddress.value = null;
      }
    };
    const updateAndSaveAccountDetails = (accountDetails) => {
      accountDetails.value = accountDetails;
      updateDetails();
    };
    const updateAndSaveAccessTypeDetails = async (accessType: string) => {
      await updateOrganizationAccessType(accessType);
      viewOnlyMode({ component: "accessType", mode: true });
    };
    const resetAddress = () => {
      baseAddress.value = originalAddress.value;
      viewOnlyMode("address");
    };
    const viewOnlyMode = async (details) => {
      const { component, mode } = details;
      if (component === "address") {
        isAddressViewOnly.value = mode;
      }
      if (component === "account") {
        isAccountInfoViewOnly.value = mode;
      }
      if (component === "accessType") {
        if (!mode) {
          await getOrgPayments();
        }
        isAccessTypeViewOnly.value = mode;
      }
    };
    const beforeRouteLeave = async (to, from, next) => {
      if (!isAddressEditable.value || isCompleteAccountInfo.value) {
        next();
      } else {
        console.log("account info incomplete.blocking navigation");
      }
    };
    const updateAddress = (address: Address) => {
      addressChanged.value = true;
      setCurrentOrganizationAddress(address);
    };
    const showSuspendAccountDialog = async (status) => {
      if (status === AccountStatus.ACTIVE) {
        dialogTitle.value = "Suspend Account";
        dialogText.value = ctx.root.$t("suspendAccountText").toString();
      } else {
        dialogTitle.value = "Unsuspend Account";
        dialogText.value = ctx.root.$t("unsuspendAccountText").toString();
      }
      ctx.refs.suspendAccountDialog.open();
    };
    const confirmSuspendAccount = async (): Promise<void> => {
      isSuspensionReasonFormValid.value =
        ctx.refs.suspensionReasonForm?.validate();
      if (isSuspensionReasonFormValid.value) {
        await suspendOrganization(selectedSuspensionReasonCode.value);
        ctx.refs.suspendAccountDialog.close();
        if (currentOrganization.statusCode === AccountStatus.SUSPENDED) {
          suspensionCompleteDialogText.value = `The account ${currentOrganization.name} has been suspended.`;
          ctx.refs.suspensionCompleteDialog.open();
        }
      }
    };
    const closeSuspendAccountDialog = () => {
      ctx.refs.suspendAccountDialog.close();
    };
    const closeSuspensionCompleteDialog = () => {
      ctx.refs.suspensionCompleteDialog.close();
    };
    const getAccountFromSession = (): AccountSettings => {
      return JSON.parse(
        ConfigHelper.getFromSession(SessionStorageKeys.CurrentAccount || "{}")
      );
    };
    const updateDetails = async () => {
      errorMessage.value = "";
      const {
        branchName,
        businessSize,
        businessType,
        name,
        isBusinessAccount,
      } = accountDetails.value;
      let createRequestBody: CreateRequestBody = {};
      if (
        baseAddress.value &&
        addressChanged.value &&
        JSON.stringify(originalAddress.value) !==
          JSON.stringify(currentOrgAddress)
      ) {
        createRequestBody.mailingAddress = { ...baseAddress.value };
      }
      if (name !== currentOrganization.name) {
        createRequestBody.name = name;
      }
      if (branchName !== currentOrganization.branchName) {
        createRequestBody.branchName = branchName;
      }
      if (typeof isBusinessAccount !== undefined) {
        createRequestBody.isBusinessAccount = isBusinessAccount;
      }
      if (isBusinessAccount && accountDetails.value) {
        if (currentOrganization.businessSize !== businessSize) {
          createRequestBody.businessSize = businessSize;
        }
        if (currentOrganization.businessType !== businessType) {
          createRequestBody.businessType = businessType;
        }
      }
      try {
        await updateOrg(createRequestBody);
        ctx.root.$store.commit("updateHeader");
        addressChanged.value = false;
        if (baseAddress.value) {
          isCompleteAccountInfo.value = true;
        }
        viewOnlyMode({ component: "address", mode: true });
        viewOnlyMode({ component: "account", mode: true });
      } catch (err) {
        switch (err.response.status) {
          case 409:
            errorMessage.value =
              "An account with this name already exists. Try a different account name.";
            break;
          case 400:
            errorMessage.value = "Invalid account name";
            break;
          default:
            errorMessage.value =
              "An error occurred while attempting to create your account.";
        }
      }
    };
    const checkBaseAddressValidity = (isValid) => {
      isBaseAddressValid.value = !!isValid;
    };
    const getStatusColor = (status) => {
      switch (status) {
        case AccountStatus.NSF_SUSPENDED:
        case AccountStatus.SUSPENDED:
          return "error";
        case AccountStatus.ACTIVE:
          return "green";
        default:
          return "primary";
      }
    };
    const getDialogStatusButtonColor = (status) => {
      switch (status) {
        case AccountStatus.NSF_SUSPENDED:
        case AccountStatus.SUSPENDED:
          return "green";
        case AccountStatus.ACTIVE:
          return "error";
        default:
          return "primary";
      }
    };
    const getStatusText = (status) => {
      switch (status) {
        case AccountStatus.NSF_SUSPENDED:
          return "NSF SUSPENDED";
        case AccountStatus.SUSPENDED:
          return "SUSPENDED";
        default:
          return status;
      }
    };
    onMounted(async () => {
      const accountSettings = getAccountFromSession();
      await syncOrganization(accountSettings.id);
      setAccountChangedHandler(setup);
      await setup();
    });
    return {
      dialogTitle,
      dialogText,
      selectedSuspensionReasonCode,
      suspensionCompleteDialogText,
      isSuspensionReasonFormValid,
      addressChanged,
      originalAddress,
      errorMessage,
      isBaseAddressValid,
      isCompleteAccountInfo,
      accountDetails,
      isAddressViewOnly,
      isAccountInfoViewOnly,
      isAccessTypeViewOnly,
      $refs,
      suspensionSelectRules,
      isStaff,
      isSuspendButtonVisible,
      editAccountUrl,
      canChangeAccessType,
      baseAddress,
      nameChangeNotAllowed,
      isAddressEditable,
      isAdminContactViewable,
      isAccountStatusActive,
      setAccountDetails,
      setup,
      updateAndSaveAccountDetails,
      updateAndSaveAccessTypeDetails,
      resetAddress,
      viewOnlyMode,
      beforeRouteLeave,
      updateAddress,
      showSuspendAccountDialog,
      confirmSuspendAccount,
      closeSuspendAccountDialog,
      closeSuspensionCompleteDialog,
      getAccountFromSession,
      updateDetails,
      checkBaseAddressValidity,
      getStatusColor,
      getDialogStatusButtonColor,
      getStatusText,
    };
  },
});
