import { defineComponent, toRefs, ref, computed } from "@vue/composition-api";
import { Account, LoginSource } from "@/util/constants";
import { BcolAccountDetails, BcolProfile } from "@/models/bcol";
import { Component, Mixins, Prop, Vue, Watch } from "vue-property-decorator";
import {
  CreateRequestBody,
  Member,
  OrgBusinessType,
  Organization,
} from "@/models/Organization";
import { mapActions, mapMutations, mapState } from "vuex";
import AccountBusinessType from "@/components/auth/common/AccountBusinessType.vue";
import { Address } from "@/models/address";
import BaseAddressForm from "@/components/auth/common/BaseAddressForm.vue";
import BcolLogin from "@/components/auth/create-account/BcolLogin.vue";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import LinkedBCOLBanner from "@/components/auth/common/LinkedBCOLBanner.vue";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { User } from "@/models/user";
import { addressSchema } from "@/schemas";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const UserModule = namespace("user");
export default defineComponent({
  components: {
    AccountBusinessType,
    BcolLogin,
    BaseAddressForm,
    ConfirmCancelButton,
    LinkedBCOLBanner,
  },
  props: {
    cancelUrl: { type: String },
    readOnly: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { cancelUrl, readOnly } = toRefs(props);
    const username = ref("");
    const password = ref("");
    const errorMessage = ref<string>("");
    const bcolDuplicateNameErrorMessage = ref("");
    const saving = ref(false);
    const isBaseAddressValid = ref<boolean>(true);
    const orgNameReadOnly = ref(true);
    const DUPL_ERROR_MESSAGE = ref(
      "An account with this name already exists. Try a different account name."
    );
    const baseAddressSchema = ref<{}>(addressSchema);
    const orgNameRules = ref([(v) => !!v || "An account name is required"]);
    const orgBusinessTypeLocal = ref<OrgBusinessType>({});
    const isOrgBusinessTypeValid = ref(false);
    const $refs = ref<{
      createAccountInfoForm: HTMLFormElement;
    }>(undefined);
    const teamNameRules = ref([(v) => !!v || "An account name is required"]);
    const isExtraProvUser = computed(() => {
      return (
        ctx.root.$store.getters["auth/currentLoginSource"] === LoginSource.BCEID
      );
    });
    const grantAccessText = computed(() => {
      const username = isExtraProvUser.value
        ? ""
        : `, ${currentUser?.fullName},`;
      const accountName = readOnly.value
        ? currentOrganization.bcolAccountName
        : currentOrganization?.bcolAccountDetails?.orgName;
      return `I ${username} confirm that I am authorized to grant access to the account ${accountName}`;
    });
    const grantAccess = computed({
      get() {
        return readOnly.value ? true : currentOrganization?.grantAccess;
      },
      set(grantAccess: boolean) {
        setGrantAccess(grantAccess);
      },
    });
    const address = computed(() => {
      return currentOrgAddress;
    });
    const linked = computed(() => {
      return !!currentOrganization?.bcolAccountDetails;
    });
    const isFormValid = (): boolean => {
      return (
        !!isOrgBusinessTypeValid.value &&
        !errorMessage.value &&
        !!isBaseAddressValid.value
      );
    };
    const unlinkAccount = () => {
      resetBcolDetails();
    };
    const updateAddress = (address: Address) => {
      setCurrentOrganizationAddress(address);
    };
    const updateOrgNameAndClearErrors = () => {
      bcolDuplicateNameErrorMessage.value = "";
      errorMessage.value = "";
    };
    const save = async () => {
      goNext();
    };
    const onLink = async (details: {
      bcolProfile: BcolProfile;
      bcolAccountDetails: BcolAccountDetails;
    }) => {
      const orgName = details.bcolAccountDetails.orgName;
      orgBusinessTypeLocal.value.name = orgName;
      var org: Organization = {
        id: currentOrganization.id,
        name: details.bcolAccountDetails.orgName,
        accessType: currentOrganization.accessType,
        bcolProfile: details.bcolProfile,
        bcolAccountDetails: details.bcolAccountDetails,
        grantAccess: false,
        orgType: Account.PREMIUM,
        bcolAccountName: details.bcolAccountDetails.orgName,
      };
      setCurrentOrganization(org);
      setCurrentOrganizationAddress(details.bcolAccountDetails.address);
      await validateAccountNameUnique();
    };
    const validateAccountNameUnique = async () => {
      const available = await isOrgNameAvailable({
        name: orgBusinessTypeLocal.value.name,
        branchName: orgBusinessTypeLocal.value.branchName,
      });
      if (!available) {
        bcolDuplicateNameErrorMessage.value =
          AccountCreatePremium.DUPL_ERROR_MESSAGE;
        orgNameReadOnly.value = false;
        return false;
      } else {
        orgNameReadOnly.value = true;
        return true;
      }
    };
    const cancel = () => {
      if (stepBack) {
        stepBack();
      } else {
        ctx.root.$router.push({ path: "/home" });
      }
    };
    const goBack = () => {
      stepBack();
    };
    const goNext = async () => {
      const isValidName = readOnly.value
        ? true
        : await validateAccountNameUnique();
      if (isValidName) {
        stepForward();
      } else {
        errorMessage.value = AccountCreatePremium.DUPL_ERROR_MESSAGE;
      }
    };
    const redirectToNext = (organization?: Organization) => {
      ctx.root.$router.push({ path: `/account/${organization.id}/` });
    };
    const checkBaseAddressValidity = (isValid) => {
      isBaseAddressValid.value = !!isValid;
    };
    const updateOrgBusinessType = (orgBusinessType: OrgBusinessType) => {
      orgBusinessTypeLocal.value = orgBusinessType;
      setCurrentOrganizationBusinessType(orgBusinessTypeLocal.value);
    };
    const checkOrgBusinessTypeValid = (isValid) => {
      isOrgBusinessTypeValid.value = !!isValid;
    };
    return {
      username,
      password,
      errorMessage,
      bcolDuplicateNameErrorMessage,
      saving,
      isBaseAddressValid,
      orgNameReadOnly,
      DUPL_ERROR_MESSAGE,
      baseAddressSchema,
      orgNameRules,
      orgBusinessTypeLocal,
      isOrgBusinessTypeValid,
      $refs,
      teamNameRules,
      isExtraProvUser,
      grantAccessText,
      grantAccess,
      address,
      linked,
      isFormValid,
      unlinkAccount,
      updateAddress,
      updateOrgNameAndClearErrors,
      save,
      onLink,
      validateAccountNameUnique,
      cancel,
      goBack,
      goNext,
      redirectToNext,
      checkBaseAddressValidity,
      updateOrgBusinessType,
      checkOrgBusinessTypeValid,
    };
  },
});
