import {
  defineComponent,
  toRefs,
  ref,
  computed,
  onMounted,
} from "@vue/composition-api";
import { Account, LDFlags } from "@/util/constants";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { OrgBusinessType, Organization } from "@/models/Organization";
import { Code } from "@/models/Code";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import OrgNameAutoComplete from "@/views/auth/OrgNameAutoComplete.vue";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const CodesModule = namespace("codes");
export default defineComponent({
  components: {
    OrgNameAutoComplete,
  },
  props: {
    govmAccount: { default: false, type: Boolean },
    errorMessage: { default: null, type: String },
    saving: { default: false, type: Boolean },
    bcolDuplicateNameErrorMessage: { default: null, type: String },
    premiumLinkedAccount: { default: false, type: Boolean },
    orgNameReadOnly: { default: false, type: Boolean },
    isEditAccount: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const {
      govmAccount,
      errorMessage,
      saving,
      bcolDuplicateNameErrorMessage,
      premiumLinkedAccount,
      orgNameReadOnly,
      isEditAccount,
    } = toRefs(props);
    const autoCompleteIsActive = ref<boolean>(false);
    const autoCompleteSearchValue = ref<string>("");
    const isLoading = ref(false);
    const $refs = ref<{
      accountInformationForm: HTMLFormElement;
      name: HTMLFormElement;
      businessType: HTMLFormElement;
      businessSize: HTMLFormElement;
      isBusinessAccount: HTMLFormElement;
    }>(undefined);
    const isBusinessAccount = ref(false);
    const name = ref("");
    const businessType = ref("");
    const businessSize = ref("");
    const branchName = ref("");
    const orgNameRules = ref([(v) => !!v || "An account name is required"]);
    const orgBusinessTypeRules = ref([
      (v) => !!v || "A business type is required",
    ]);
    const orgBusinessSizeRules = ref([
      (v) => !!v || "A business size is required",
    ]);
    const enableOrgNameAutoComplete = computed((): boolean => {
      return (
        LaunchDarklyService.getFlag(LDFlags.EnableOrgNameAutoComplete) || false
      );
    });
    const getOrgNameLabel = computed((): string => {
      return govmAccount.value
        ? "Ministry Name"
        : isBusinessAccount.value
        ? "Legal Business Name"
        : "Account Name";
    });
    const emitUpdatedOrgBusinessType = () => {
      const orgBusinessType: OrgBusinessType = {
        name: name.value,
        isBusinessAccount: isBusinessAccount.value,
        ...((govmAccount.value || isBusinessAccount.value) && {
          branchName: branchName.value,
        }),
        ...(isBusinessAccount.value && {
          businessType: businessType.value,
          businessSize: businessSize.value,
          branchName: branchName.value,
        }),
      };
      return orgBusinessType;
    };
    const emitValid = () => {
      let isFormValid = false;
      isFormValid =
        !ctx.refs.isBusinessAccount?.hasError && !ctx.refs.name?.hasError;
      if (isBusinessAccount.value && isFormValid) {
        isFormValid =
          isFormValid &&
          !ctx.refs.businessType?.hasError &&
          !ctx.refs.businessSize?.hasError;
      }
      return isFormValid;
    };
    const setAutoCompleteSearchValue = (
      autoCompleteSearchValue: string
    ): void => {
      if (enableOrgNameAutoComplete.value) {
        autoCompleteIsActive.value = false;
        name.value = autoCompleteSearchValue;
      }
      emitUpdatedOrgBusinessType();
    };
    const onOrgNameChange = async () => {
      if (enableOrgNameAutoComplete.value && isBusinessAccount.value) {
        if (name.value) {
          autoCompleteSearchValue.value = name.value;
        }
        autoCompleteIsActive.value = name.value !== "";
      }
      if (premiumLinkedAccount.value && bcolDuplicateNameErrorMessage.value) {
        ctx.emit("update:org-name-clear-errors");
      }
      await onOrgBusinessTypeChange();
    };
    const onOrgBusinessTypeChange = async (clearOrgName: boolean = false) => {
      if (clearOrgName) {
        name.value = "";
      }
      await ctx.root.$nextTick();
      emitUpdatedOrgBusinessType();
      emitValid();
    };
    onMounted(async () => {
      try {
        isLoading.value = true;
        await getBusinessSizeCodes();
        await getBusinessTypeCodes();
        if (currentOrganization.name) {
          name.value = currentOrganization.name;
          isBusinessAccount.value = currentOrganization.isBusinessAccount;
          businessType.value = currentOrganization.businessType;
          businessSize.value = currentOrganization.businessSize;
          branchName.value = currentOrganization.branchName;
        } else {
          isBusinessAccount.value =
            currentOrganization.orgType !== Account.BASIC;
        }
        await onOrgBusinessTypeChange();
      } catch (ex) {
        console.log(`error while loading account business type -  ${ex}`);
      } finally {
        isLoading.value = false;
      }
    });
    return {
      autoCompleteIsActive,
      autoCompleteSearchValue,
      isLoading,
      $refs,
      isBusinessAccount,
      name,
      businessType,
      businessSize,
      branchName,
      orgNameRules,
      orgBusinessTypeRules,
      orgBusinessSizeRules,
      enableOrgNameAutoComplete,
      getOrgNameLabel,
      emitUpdatedOrgBusinessType,
      emitValid,
      setAutoCompleteSearchValue,
      onOrgNameChange,
      onOrgBusinessTypeChange,
    };
  },
});
