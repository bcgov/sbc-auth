import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
} from "@vue/composition-api";
import {
  Account,
  LDFlags,
  LoginSource,
  SessionStorageKeys,
} from "@/util/constants";
import { Component, Mixins, Prop, Watch } from "vue-property-decorator";
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
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import OrgModule from "@/store/modules/org";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { addressSchema } from "@/schemas";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    AccountBusinessType,
    BaseAddressForm,
    ConfirmCancelButton,
  },
  props: {
    cancelUrl: { type: String },
    govmAccount: { default: false, type: Boolean },
    readOnly: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentOrgAddress = computed(
      () => ctx.root.$store.state.org.currentOrgAddress
    );
    const currentOrganizationType = computed(
      () => ctx.root.$store.state.org.currentOrganizationType
    );
    const userProfile = computed(() => ctx.root.$store.state.user.userProfile);
    const currentUser = computed(() => ctx.root.$store.state.user.currentUser);
    const syncMembership = () => ctx.root.$store.dispatch("org/syncMembership");
    const syncOrganization = () =>
      ctx.root.$store.dispatch("org/syncOrganization");
    const isOrgNameAvailable = () =>
      ctx.root.$store.dispatch("org/isOrgNameAvailable");
    const { cancelUrl, govmAccount, readOnly } = toRefs(props);
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const errorMessage = ref<string>("");
    const saving = ref(false);
    const isBasicAccount = ref<boolean>(true);
    const syncMembership = ref<(orgId: number) => Promise<Member>>(undefined);
    const syncOrganization =
      ref<(orgId: number) => Promise<Organization>>(undefined);
    const isOrgNameAvailable =
      ref<(requestBody: CreateRequestBody) => Promise<boolean>>(undefined);
    const setCurrentOrganization =
      ref<(organization: Organization) => void>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const isBaseAddressValid = ref(
      !isExtraProvUser.value && !enablePaymentMethodSelectorStep.value
    );
    const currentOrgAddress = ref<Address>(undefined);
    const currentOrganizationType = ref<string>(undefined);
    const setCurrentOrganizationAddress =
      ref<(address: Address) => void>(undefined);
    const orgBusinessTypeLocal = ref<OrgBusinessType>({});
    const baseAddressSchema = ref<{}>(addressSchema);
    const isOrgBusinessTypeValid = ref(false);
    const orgId = ref<number>(null);
    const $refs = ref<{
      createAccountInfoForm: HTMLFormElement;
    }>(undefined);
    const enablePaymentMethodSelectorStep = computed((): boolean => {
      return (
        LaunchDarklyService.getFlag(LDFlags.PaymentTypeAccountCreation) || false
      );
    });
    const address = computed(() => {
      return currentOrgAddress.value;
    });
    const isExtraProvUser = computed(() => {
      return (
        ctx.root.$store.getters["auth/currentLoginSource"] === LoginSource.BCEID
      );
    });
    const isFormValid = (): boolean => {
      return !!isOrgBusinessTypeValid.value && !!isBaseAddressValid.value;
    };
    const updateAddress = (address: Address) => {
      setCurrentOrganizationAddress.value(address);
    };
    const updateOrgBusinessType = (orgBusinessType: OrgBusinessType) => {
      orgBusinessTypeLocal.value = orgBusinessType;
    };
    const checkOrgBusinessTypeValid = (isValid) => {
      isOrgBusinessTypeValid.value = !!isValid;
    };
    const checkBaseAddressValidity = (isValid) => {
      isBaseAddressValid.value = !!isValid;
    };
    const save = async () => {
      if (isFormValid()) {
        const checkNameAVailability =
          orgBusinessTypeLocal.value.name !== currentOrganization.value?.name;
        if (checkNameAVailability && !govmAccount.value) {
          const available = await isOrgNameAvailable.value({
            name: orgBusinessTypeLocal.value.name,
            branchName: orgBusinessTypeLocal.value.branchName,
          });
          if (!available) {
            errorMessage.value =
              "An account with this name already exists. Try a different account name.";
            return;
          }
        }
        const orgType = isBasicAccount.value ? Account.BASIC : Account.PREMIUM;
        let org: Organization = {
          name: orgBusinessTypeLocal.value.name,
          orgType: orgType,
        };
        if (govmAccount.value) {
          org = {
            ...org,
            ...{
              branchName: orgBusinessTypeLocal.value.branchName,
              id: orgId.value,
            },
          };
        }
        if (orgBusinessTypeLocal.value.isBusinessAccount) {
          org = {
            ...org,
            ...{
              branchName: orgBusinessTypeLocal.value.branchName,
              isBusinessAccount: orgBusinessTypeLocal.value.isBusinessAccount,
              businessSize: orgBusinessTypeLocal.value.businessSize,
              businessType: orgBusinessTypeLocal.value.businessType,
            },
          };
        }
        if (!readOnly.value) {
          setCurrentOrganization.value(org);
        }
        stepForward();
      }
    };
    const redirectToNext = (organization?: Organization) => {
      ctx.root.$router.push({ path: `/account/${organization.id}/` });
    };
    const goBack = () => {
      stepBack();
    };
    const goNext = () => {
      stepForward();
    };
    onMounted(async () => {
      if (govmAccount.value) {
        orgId.value = currentOrganization.value.id;
      }
      if (enablePaymentMethodSelectorStep.value) {
        isBasicAccount.value = currentOrganizationType.value === Account.BASIC;
      }
    });
    return {
      currentOrganization,
      currentOrgAddress,
      currentOrganizationType,
      userProfile,
      currentUser,
      syncMembership,
      syncOrganization,
      isOrgNameAvailable,
      orgStore,
      errorMessage,
      saving,
      isBasicAccount,
      syncMembership,
      syncOrganization,
      isOrgNameAvailable,
      setCurrentOrganization,
      currentOrganization,
      isBaseAddressValid,
      currentOrgAddress,
      currentOrganizationType,
      setCurrentOrganizationAddress,
      orgBusinessTypeLocal,
      baseAddressSchema,
      isOrgBusinessTypeValid,
      orgId,
      $refs,
      enablePaymentMethodSelectorStep,
      address,
      isExtraProvUser,
      isFormValid,
      updateAddress,
      updateOrgBusinessType,
      checkOrgBusinessTypeValid,
      checkBaseAddressValidity,
      save,
      redirectToNext,
      goBack,
      goNext,
    };
  },
});
