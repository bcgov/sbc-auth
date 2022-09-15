import {
  defineComponent,
  toRefs,
  ref,
  computed,
  watch,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Mixins, Prop, Watch } from "vue-property-decorator";
import AccountBusinessType from "@/components/auth/common/AccountBusinessType.vue";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import { Code } from "@/models/Code";
import { OrgBusinessType } from "@/models/Organization";
import { namespace } from "vuex-class";
const CodesModule = namespace("codes");
export default defineComponent({
  components: {
    AccountBusinessType,
  },
  props: {
    accountDetails: {
      default: null,
      type: Object as PropType<OrgBusinessType>,
    },
    viewOnlyMode: { default: true, type: Boolean },
    isBusinessAccount: { default: false, type: Boolean },
    nameChangeNotAllowed: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const {
      accountDetails,
      viewOnlyMode,
      isBusinessAccount,
      nameChangeNotAllowed,
    } = toRefs(props);
    const orgName = ref("");
    const branchName = ref("");
    const accountTypeBusiness = ref(false);
    const isOrgBusinessTypeValid = ref(false);
    const isLoading = ref(false);
    const orgBusinessType = ref<OrgBusinessType>({
      businessType: "",
      businessSize: "",
    });
    const $refs = ref<{
      editAccountForm: HTMLFormElement;
    }>(undefined);
    const getBusinessTypeLabel = computed(() => {
      return getCodeLabel(
        businessTypeCodes,
        orgBusinessType.value.businessType
      );
    });
    const getBusinessSizeLabel = computed(() => {
      return getCodeLabel(
        businessSizeCodes,
        orgBusinessType.value.businessSize
      );
    });
    const onAccountDetailsChange = () => {
      updateAccountDetails();
    };
    const onAccountTypeChange = (businessType) => {
      accountTypeBusiness.value = businessType;
    };
    const updateAccountDetails = () => {
      orgName.value = accountDetails.value?.name;
      branchName.value = accountDetails.value?.branchName;
      orgBusinessType.value.businessType = accountDetails.value?.businessType;
      orgBusinessType.value.businessSize = accountDetails.value?.businessSize;
      accountTypeBusiness.value = isBusinessAccount.value;
    };
    const getCodeLabel = (codeList, code) => {
      const codeArray = codeList.filter((type) => type.code === code);
      return (codeArray && codeArray[0] && codeArray[0]?.desc) || "";
    };
    const cancelEdit = () => {
      updateAccountDetails();
      return {
        component: "account",
        mode: true,
      };
    };
    const updateOrgBusinessType = (orgBusinessType: OrgBusinessType) => {
      orgBusinessType.value = orgBusinessType;
    };
    const updateDetails = () => {
      if (isOrgBusinessTypeValid.value) {
        return orgBusinessType.value;
      }
    };
    const checkOrgBusinessTypeValid = (isValid) => {
      isOrgBusinessTypeValid.value = !!isValid;
    };
    watch(accountDetails, onAccountDetailsChange, { deep: true });
    watch(isBusinessAccount, onAccountTypeChange);
    onMounted(async () => {
      isLoading.value = true;
      await getBusinessTypeCodes();
      await getBusinessSizeCodes();
      updateAccountDetails();
      isLoading.value = false;
    });
    return {
      orgName,
      branchName,
      accountTypeBusiness,
      isOrgBusinessTypeValid,
      isLoading,
      orgBusinessType,
      $refs,
      getBusinessTypeLabel,
      getBusinessSizeLabel,
      onAccountDetailsChange,
      onAccountTypeChange,
      updateAccountDetails,
      getCodeLabel,
      cancelEdit,
      updateOrgBusinessType,
      updateDetails,
      checkOrgBusinessTypeValid,
    };
  },
});
