import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { CorpType, LDFlags, LoginSource, Pages } from "@/util/constants";
import { MembershipStatus, RemoveBusinessPayload } from "@/models/Organization";
import { mapActions, mapGetters, mapState } from "vuex";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import AddBusinessDialog from "@/components/auth/manage-business/AddBusinessDialog.vue";
import AddNameRequestForm from "@/components/auth/manage-business/AddNameRequestForm.vue";
import { Address } from "@/models/address";
import AffiliatedEntityTable from "@/components/auth/manage-business/AffiliatedEntityTable.vue";
import ConfigHelper from "@/util/config-helper";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import NextPageMixin from "@/components/auth/mixins/NextPageMixin.vue";
import PasscodeResetOptionsModal from "@/components/auth/manage-business/PasscodeResetOptionsModal.vue";
import { appendAccountId } from "sbc-common-components/src/util/common-util";
export default defineComponent({
  components: {
    AddBusinessDialog,
    AddNameRequestForm,
    AffiliatedEntityTable,
    ModalDialog,
    PasscodeResetOptionsModal,
  },
  props: { orgId: { default: "", type: String } },
  setup(props, ctx) {
    const currentOrgAddress = computed(
      () => ctx.root.$store.state.org.currentOrgAddress
    );
    const currentAccountSettings = computed(
      () => ctx.root.$store.state.org.currentAccountSettings
    );
    const userProfile = computed(() => ctx.root.$store.state.user.userProfile);
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const isPremiumAccount = computed(
      () => ctx.root.$store.getters["org/isPremiumAccount"]
    );
    const syncBusinesses = () =>
      ctx.root.$store.dispatch("business/syncBusinesses");
    const removeBusiness = () =>
      ctx.root.$store.dispatch("business/removeBusiness");
    const createNumberedBusiness = () =>
      ctx.root.$store.dispatch("business/createNumberedBusiness");
    const syncAddress = () => ctx.root.$store.dispatch("org/syncAddress");
    const { orgId } = toRefs(props);
    const removeBusinessPayload = ref(null);
    const dialogTitle = ref("");
    const dialogText = ref("");
    const isLoading = ref(-1);
    const resetPasscodeEmail = ref<string>(null);
    const businessIdentifier = ref<string>(null);
    const primaryBtnText = ref("");
    const secondaryBtnText = ref("");
    const primaryBtnHandler = ref<() => void>(undefined);
    const secondaryBtnHandler = ref<() => void>(undefined);
    const lastSyncBusinesses = ref(0);
    const addBusinessDialog = ref(false);
    const addAffiliationDropdown = ref<boolean>(false);
    const isPremiumAccount = ref<boolean>(undefined);
    const syncBusinesses = ref<() => Promise<void>>(undefined);
    const removeBusiness =
      ref<(removeBusinessPayload: RemoveBusinessPayload) => Promise<void>>(
        undefined
      );
    const createNumberedBusiness =
      ref<(accountId: Number) => Promise<void>>(undefined);
    const currentOrgAddress = ref<Address>(undefined);
    const syncAddress = ref<() => Address>(undefined);
    const selectedColumns = ref(["Number", "Type", "Status"]);
    const columns = ref(["Number", "Type", "Status"]);
    const $refs = ref<{
      successDialog: ModalDialog;
      errorDialog: ModalDialog;
      addNRDialog: ModalDialog;
      passcodeResetOptionsModal: PasscodeResetOptionsModal;
      removedBusinessSuccessDialog: ModalDialog;
      removalConfirmDialog: ModalDialog;
    }>(undefined);
    const enableMandatoryAddress = computed((): boolean => {
      return (
        LaunchDarklyService.getFlag(LDFlags.EnableMandatoryAddress) || false
      );
    });
    const setup = async () => {
      if (isLoading.value === 1) {
        return;
      }
      if (Date.now() - lastSyncBusinesses.value < 2000) {
        return;
      }
      isLoading.value = 1;
      ctx.root.$route.query.isNumberedCompanyRequest &&
        (await createNumberedBusiness.value(currentAccountSettings.value.id));
      await syncBusinesses.value();
      lastSyncBusinesses.value = Date.now();
      isLoading.value = 0;
    };
    const goToNameRequest = (): void => {
      window.location.href = appendAccountId(ConfigHelper.getNameRequestUrl());
    };
    const startNumberedCompany = async () => {
      await createNumberedBusiness.value(currentOrganization.id);
      await syncBusinesses.value();
    };
    const showAddSuccessModal = async () => {
      addBusinessDialog.value = false;
      dialogTitle.value = "Business Added";
      dialogText.value = "You have successfully added a business";
      await syncBusinesses.value();
      ctx.refs.successDialog.open();
    };
    const showAddSuccessModalNR = async () => {
      ctx.refs.addNRDialog.close();
      dialogTitle.value = "Name Request Added";
      dialogText.value = "You have successfully added a name request";
      await syncBusinesses.value();
      ctx.refs.successDialog.open();
    };
    const showInvalidCodeModal = (label: string) => {
      addBusinessDialog.value = false;
      dialogTitle.value = `Invalid ${label}`;
      dialogText.value = `Unable to add the business. The provided ${label} is invalid.`;
      ctx.refs.errorDialog.open();
    };
    const showEntityNotFoundModal = () => {
      addBusinessDialog.value = false;
      dialogTitle.value = "Business Not Found";
      dialogText.value = "The specified business was not found.";
      ctx.refs.errorDialog.open();
    };
    const showNRNotFoundModal = () => {
      ctx.refs.addNRDialog.close();
      dialogTitle.value = "Name Request Not Found";
      dialogText.value = "The specified name request was not found.";
      ctx.refs.errorDialog.open();
    };
    const showNRErrorModal = () => {
      ctx.refs.addNRDialog.close();
      dialogTitle.value = "Error Adding Name Request";
      dialogText.value = "";
      ctx.refs.errorDialog.open();
    };
    const showPasscodeClaimedModal = () => {
      const contactNumber = ctx.root.$t("techSupportTollFree").toString();
      addBusinessDialog.value = false;
      dialogTitle.value = "Passcode Already Claimed";
      dialogText.value = `This passcode has already been claimed. If you have questions, please call ${contactNumber}`;
      ctx.refs.errorDialog.open();
    };
    const showUnknownErrorModal = (type: string) => {
      if (type === "business") {
        addBusinessDialog.value = false;
        dialogTitle.value = "Error Adding Existing Business";
        dialogText.value =
          "An error occurred adding your business. Please try again.";
      } else if (type === "nr") {
        ctx.refs.addNRDialog.close();
        dialogTitle.value = "Error Adding Existing Name Request";
        dialogText.value =
          "An error occurred adding your name request. Please try again.";
      }
      ctx.refs.errorDialog.open();
    };
    const showAddBusinessModal = () => {
      addBusinessDialog.value = true;
    };
    const showAddNRModal = () => {
      dialogTitle.value = "Add an Existing Name Request";
      ctx.refs.addNRDialog.open();
    };
    const showConfirmationOptionsModal = (
      removeBusinessPayload: RemoveBusinessPayload
    ) => {
      removeBusinessPayload.value = removeBusinessPayload;
      if (
        removeBusinessPayload.business.corpType.code === CorpType.NAME_REQUEST
      ) {
        populateNRmodalValues();
        ctx.refs.removalConfirmDialog.open();
      } else if (
        removeBusinessPayload.business.corpType.code === CorpType.NEW_BUSINESS
      ) {
        populateIAmodalValues();
        ctx.refs.removalConfirmDialog.open();
      } else if (
        removeBusinessPayload.business.corpType.code ===
        CorpType.NEW_REGISTRATION
      ) {
        populateRegistrationModalValues();
        ctx.refs.removalConfirmDialog.open();
      } else {
        ctx.refs.passcodeResetOptionsModal.open();
      }
    };
    const populateNRmodalValues = () => {
      dialogTitle.value = ctx.root.$t("removeNRConfirmTitle").toString();
      dialogText.value = ctx.root.$t("removeNRConfirmText").toString();
      primaryBtnText.value = "Remove Name Request";
      secondaryBtnText.value = "Keep Name Request";
      primaryBtnHandler.value = confirmRemovalNr;
      secondaryBtnHandler.value = cancelRemoval;
    };
    const populateIAmodalValues = () => {
      dialogTitle.value = ctx.root.$t("removeIAConfirmTitle").toString();
      dialogText.value = ctx.root.$t("removeIAConfirmText").toString();
      primaryBtnText.value = "Delete Incorporation Application";
      secondaryBtnText.value = "Keep Incorporation Application";
      primaryBtnHandler.value = confirmRemovalIA;
      secondaryBtnHandler.value = cancelRemoval;
    };
    const populateRegistrationModalValues = () => {
      dialogTitle.value = ctx.root
        .$t("removeRegistrationConfirmTitle")
        .toString();
      dialogText.value = ctx.root
        .$t("removeRegistrationConfirmText")
        .toString();
      primaryBtnText.value = "Delete Registration";
      secondaryBtnText.value = "Keep Registration";
      primaryBtnHandler.value = confirmRemovalRegistration;
      secondaryBtnHandler.value = cancelRemoval;
    };
    const cancelRemoval = () => {
      ctx.refs.removalConfirmDialog.close();
    };
    const confirmRemovalRegistration = () => {
      ctx.refs.removalConfirmDialog.close();
      remove(
        "",
        false,
        "removeRegistrationSuccessTitle",
        "removeRegistrationSuccessText"
      );
    };
    const confirmRemovalIA = () => {
      ctx.refs.removalConfirmDialog.close();
      remove("", false, "removeIASuccessTitle", "removeIASuccessText");
    };
    const confirmRemovalNr = () => {
      ctx.refs.removalConfirmDialog.close();
      remove("", false, "removeNRSuccessTitle", "removeNRSuccessText");
    };
    const cancelAddBusiness = () => {
      addBusinessDialog.value = false;
    };
    const cancelAddNameRequest = () => {
      ctx.refs.addNRDialog.close();
    };
    const remove = async (
      resetPasscodeEmail: string,
      resetPasscode = true,
      dialogTitleKey = "removeBusiness",
      dialogTextKey = "removedBusinessSuccessText"
    ) => {
      try {
        removeBusinessPayload.value.passcodeResetEmail = resetPasscodeEmail;
        removeBusinessPayload.value.resetPasscode = resetPasscode;
        ctx.refs.passcodeResetOptionsModal.close();
        await removeBusiness.value(removeBusinessPayload.value);
        dialogText.value = ctx.root.$t(dialogTextKey).toString();
        dialogTitle.value = ctx.root.$t(dialogTitleKey).toString();
        await syncBusinesses.value();
        ctx.refs.removedBusinessSuccessDialog.open();
      } catch (ex) {
        console.log("Error during remove organization affiliations event !");
      }
    };
    const removedBusinessSuccessClose = () => {
      ctx.refs.removedBusinessSuccessDialog.close();
    };
    const close = () => {
      ctx.refs.errorDialog.close();
    };
    onMounted(async () => {
      if (currentMembership === undefined) {
        ctx.root.$router.push(`/${Pages.CREATE_ACCOUNT}`);
        return;
      }
      if (currentMembership?.membershipStatus !== MembershipStatus.Active) {
        ctx.root.$router.push(getNextPageUrl());
        return;
      }
      const isNotAnonUser =
        currentUser.value?.loginSource !== LoginSource.BCROS;
      if (isNotAnonUser && enableMandatoryAddress.value) {
        if (
          !currentOrgAddress.value ||
          Object.keys(currentOrgAddress.value).length === 0
        ) {
          await syncAddress.value();
          if (
            !currentOrgAddress.value ||
            Object.keys(currentOrgAddress.value).length === 0
          ) {
            await ctx.root.$router.push(
              `/${Pages.MAIN}/${orgId.value}/settings/account-info`
            );
            return;
          }
        }
      }
      setAccountChangedHandler(setup);
      setup();
    });
    return {
      currentOrgAddress,
      currentAccountSettings,
      userProfile,
      currentUser,
      isPremiumAccount,
      syncBusinesses,
      removeBusiness,
      createNumberedBusiness,
      syncAddress,
      removeBusinessPayload,
      dialogTitle,
      dialogText,
      isLoading,
      resetPasscodeEmail,
      businessIdentifier,
      primaryBtnText,
      secondaryBtnText,
      primaryBtnHandler,
      secondaryBtnHandler,
      lastSyncBusinesses,
      addBusinessDialog,
      addAffiliationDropdown,
      isPremiumAccount,
      syncBusinesses,
      removeBusiness,
      createNumberedBusiness,
      currentOrgAddress,
      syncAddress,
      selectedColumns,
      columns,
      $refs,
      enableMandatoryAddress,
      setup,
      goToNameRequest,
      startNumberedCompany,
      showAddSuccessModal,
      showAddSuccessModalNR,
      showInvalidCodeModal,
      showEntityNotFoundModal,
      showNRNotFoundModal,
      showNRErrorModal,
      showPasscodeClaimedModal,
      showUnknownErrorModal,
      showAddBusinessModal,
      showAddNRModal,
      showConfirmationOptionsModal,
      populateNRmodalValues,
      populateIAmodalValues,
      populateRegistrationModalValues,
      cancelRemoval,
      confirmRemovalRegistration,
      confirmRemovalIA,
      confirmRemovalNr,
      cancelAddBusiness,
      cancelAddNameRequest,
      remove,
      removedBusinessSuccessClose,
      close,
    };
  },
});
