import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import {
  AccessType,
  Account,
  LoginSource,
  Pages,
  PaymentTypes,
  Permission,
} from "@/util/constants";
import { Component, Emit, Mixins, Prop, Vue } from "vue-property-decorator";
import {
  CreateRequestBody,
  Member,
  MembershipType,
  OrgPaymentDetails,
  Organization,
  PADInfo,
  PADInfoValidation,
} from "@/models/Organization";
import { mapActions, mapMutations, mapState } from "vuex";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import { Address } from "@/models/address";
import { BcolProfile } from "@/models/bcol";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import PaymentMethods from "@/components/auth/common/PaymentMethods.vue";
export default defineComponent({
  components: {
    PaymentMethods,
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentOrgPaymentType = computed(
      () => ctx.root.$store.state.org.currentOrgPaymentType
    );
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const permissions = computed(() => ctx.root.$store.state.org.permissions);
    const currentOrgAddress = computed(
      () => ctx.root.$store.state.org.currentOrgAddress
    );
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const validatePADInfo = () =>
      ctx.root.$store.dispatch("org/validatePADInfo");
    const getOrgPayments = () => ctx.root.$store.dispatch("org/getOrgPayments");
    const updateOrg = () => ctx.root.$store.dispatch("org/updateOrg");
    const syncAddress = () => ctx.root.$store.dispatch("org/syncAddress");
    const setCurrentOrganizationPaymentType =
      ref<(paymentType: string) => void>(undefined);
    const getOrgPayments = ref<() => any>(undefined);
    const updateOrg =
      ref<(requestBody: CreateRequestBody) => Promise<Organization>>(undefined);
    const currentMembership = ref<Member>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const currentOrgPaymentType = ref<string>(undefined);
    const validatePADInfo = ref<() => Promise<PADInfoValidation>>(undefined);
    const permissions = ref<string[]>(undefined);
    const currentUser = ref<KCUserProfile>(undefined);
    const currentOrgAddress = ref<Address>(undefined);
    const syncAddress = ref<() => Address>(undefined);
    const savedOrganizationType = ref<string>("");
    const selectedPaymentMethod = ref<string>("");
    const padInfo = ref<PADInfo>({} as PADInfo);
    const isBtnSaved = ref(false);
    const disableSaveBtn = ref(false);
    const errorMessage = ref<string>("");
    const errorTitle = ref("Payment Update Failed");
    const bcolInfo = ref<BcolProfile>({} as BcolProfile);
    const errorText = ref("");
    const isLoading = ref<boolean>(false);
    const padValid = ref<boolean>(false);
    const paymentMethodChanged = ref<boolean>(false);
    const isFuturePaymentMethodAvailable = ref<boolean>(false);
    const isTOSandAcknowledgeCompleted = ref<boolean>(false);
    const $refs = ref<{
      errorDialog: ModalDialog;
    }>(undefined);
    const isDisableSaveBtn = computed(() => {
      let disableSaveBtn = false;
      if (isBtnSaved.value) {
        disableSaveBtn = false;
      } else if (
        (selectedPaymentMethod.value === PaymentTypes.PAD && !padValid.value) ||
        !paymentMethodChanged.value ||
        selectedPaymentMethod.value === PaymentTypes.EJV ||
        disableSaveButtonForBCOL()
      ) {
        disableSaveBtn = true;
      }
      return disableSaveBtn;
    });
    const isAcknowledgeNeeded = computed(() => {
      return (
        selectedPaymentMethod.value !== currentOrgPaymentType.value ||
        isFuturePaymentMethodAvailable.value
      );
    });
    const isPaymentViewAllowed = computed((): boolean => {
      return [Permission.VIEW_PAYMENT_METHODS, Permission.MAKE_PAYMENT].some(
        (per) => permissions.value.includes(per)
      );
    });
    const setSelectedPayment = (payment) => {
      errorMessage.value = "";
      selectedPaymentMethod.value = payment.selectedPaymentMethod;
      isBtnSaved.value = (isBtnSaved.value && !payment.isTouched) || false;
      paymentMethodChanged.value = payment.isTouched || false;
    };
    const disableSaveButtonForBCOL = () => {
      return (
        selectedPaymentMethod.value === PaymentTypes.BCOL &&
        (bcolInfo.value?.password === undefined ||
          bcolInfo.value?.password === "")
      );
    };
    const getPADInfo = (padInfo: PADInfo) => {
      padInfo.value = padInfo;
    };
    const isPADValid = (isValid) => {
      padValid.value = isValid;
    };
    const getBcolInfo = (bcolProfile: BcolProfile) => {
      bcolInfo.value = bcolProfile;
    };
    const initialize = async () => {
      errorMessage.value = "";
      bcolInfo.value = {};
      const isNotAnonUser =
        currentUser.value?.loginSource !== LoginSource.BCROS;
      if (isNotAnonUser) {
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
              `/${Pages.MAIN}/${currentOrganization.value.id}/settings/account-info`
            );
            return;
          }
        }
      }
      if (isPaymentViewAllowed.value) {
        savedOrganizationType.value =
          currentOrganization.value?.orgType === Account.PREMIUM &&
          !currentOrganization.value?.bcolAccountId &&
          currentOrganization.value?.accessType !== AccessType.GOVM
            ? Account.UNLINKED_PREMIUM
            : currentOrganization.value.orgType;
        selectedPaymentMethod.value = "";
        const orgPayments: OrgPaymentDetails = await getOrgPayments.value();
        isFuturePaymentMethodAvailable.value =
          !!orgPayments.futurePaymentMethod || false;
        isTOSandAcknowledgeCompleted.value =
          orgPayments.padTosAcceptedBy !== null || false;
        selectedPaymentMethod.value = currentOrgPaymentType.value || "";
        if (
          currentOrganization.value.accessType === AccessType.GOVN &&
          orgPayments.paymentMethod === PaymentTypes.BCOL
        ) {
          savedOrganizationType.value = currentOrganization.value.orgType;
        }
      } else {
        ctx.root.$router.push(
          `/${Pages.MAIN}/${currentOrganization.value.id}/settings/account-info`
        );
      }
    };
    const verifyPAD = async () => {
      const verifyPad: PADInfoValidation = await validatePADInfo.value();
      if (!verifyPad || verifyPad?.isValid) {
        return true;
      } else {
        isLoading.value = false;
        errorText.value = "Bank information validation failed";
        if (verifyPad?.message?.length) {
          let msgList = "";
          verifyPad.message.forEach((msg) => {
            msgList += `<li>${msg}</li>`;
          });
          errorText.value = `<ul style="list-style-type: none;">${msgList}</ul>`;
        }
        ctx.refs.errorDialog.open();
        return false;
      }
    };
    const cancel = () => {
      initialize();
    };
    const save = async () => {
      isBtnSaved.value = false;
      isLoading.value = true;
      let isValid = false;
      let createRequestBody: CreateRequestBody;
      if (selectedPaymentMethod.value === PaymentTypes.PAD) {
        isValid = await verifyPAD();
        createRequestBody = {
          paymentInfo: {
            paymentMethod: PaymentTypes.PAD,
            bankTransitNumber: padInfo.value.bankTransitNumber,
            bankInstitutionNumber: padInfo.value.bankInstitutionNumber,
            bankAccountNumber: padInfo.value.bankAccountNumber,
          },
        };
      } else if (selectedPaymentMethod.value === PaymentTypes.BCOL) {
        isValid = !!(bcolInfo.value.userId && bcolInfo.value.password);
        if (!isValid) {
          errorMessage.value = "Missing User ID and Password for BC Online.";
          isLoading.value = false;
        }
        createRequestBody = {
          paymentInfo: {
            paymentMethod: PaymentTypes.BCOL,
          },
          bcOnlineCredential: bcolInfo.value,
        };
      } else {
        isValid = true;
        createRequestBody = {
          paymentInfo: {
            paymentMethod: selectedPaymentMethod.value,
          },
        };
      }
      if (isValid) {
        try {
          await updateOrg.value(createRequestBody);
          isBtnSaved.value = true;
          isLoading.value = false;
          paymentMethodChanged.value = false;
          initialize();
          setCurrentOrganizationPaymentType.value(selectedPaymentMethod.value);
        } catch (error) {
          console.error(error);
          isLoading.value = false;
          isBtnSaved.value = false;
          paymentMethodChanged.value = false;
          switch (error.response.status) {
            case 409:
              errorMessage.value = error.response.data.message;
              break;
            case 400:
              errorMessage.value = error.response.data.message;
              break;
            default:
              errorMessage.value =
                "An error occurred while attempting to create your account.";
          }
        }
      }
    };
    const closeError = () => {
      ctx.refs.errorDialog.close();
    };
    onMounted(async () => {
      setAccountChangedHandler(await initialize);
      await initialize();
    });
    return {
      currentOrganization,
      currentOrgPaymentType,
      currentMembership,
      permissions,
      currentOrgAddress,
      currentUser,
      validatePADInfo,
      getOrgPayments,
      updateOrg,
      syncAddress,
      setCurrentOrganizationPaymentType,
      getOrgPayments,
      updateOrg,
      currentMembership,
      currentOrganization,
      currentOrgPaymentType,
      validatePADInfo,
      permissions,
      currentUser,
      currentOrgAddress,
      syncAddress,
      savedOrganizationType,
      selectedPaymentMethod,
      padInfo,
      isBtnSaved,
      disableSaveBtn,
      errorMessage,
      errorTitle,
      bcolInfo,
      errorText,
      isLoading,
      padValid,
      paymentMethodChanged,
      isFuturePaymentMethodAvailable,
      isTOSandAcknowledgeCompleted,
      $refs,
      isDisableSaveBtn,
      isAcknowledgeNeeded,
      isPaymentViewAllowed,
      setSelectedPayment,
      disableSaveButtonForBCOL,
      getPADInfo,
      isPADValid,
      getBcolInfo,
      initialize,
      verifyPAD,
      cancel,
      save,
      closeError,
    };
  },
});
