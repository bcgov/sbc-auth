import {
  defineComponent,
  computed,
  toRefs,
  ref,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Mixins, Prop, Vue } from "vue-property-decorator";
import { mapMutations, mapState } from "vuex";
import { Account } from "@/util/constants";
import CommonUtils from "@/util/common-util";
import { PADInfo } from "@/models/Organization";
import TermsOfUseDialog from "@/components/auth/common/TermsOfUseDialog.vue";
import { mask } from "vue-the-mask";
export default defineComponent({
  directives: {
    mask,
  },
  components: {
    TermsOfUseDialog,
  },
  props: {
    padInformation: {
      default: () => ({} as PADInfo),
      type: Object as PropType<any>,
    },
    isChangeView: { default: false, type: Boolean },
    isAcknowledgeNeeded: { default: true, type: Boolean },
    isTOSNeeded: { default: true, type: Boolean },
    isInitialTOSAccepted: { default: false, type: Boolean },
    isInitialAcknowledged: { default: false, type: Boolean },
    clearOnEdit: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const currentOrgPADInfo = computed(
      () => ctx.root.$store.state.org.currentOrgPADInfo
    );
    const currentOrganizationType = computed(
      () => ctx.root.$store.state.org.currentOrganizationType
    );
    const {
      padInformation,
      isChangeView,
      isAcknowledgeNeeded,
      isTOSNeeded,
      isInitialTOSAccepted,
      isInitialAcknowledged,
      clearOnEdit,
    } = toRefs(props);
    const currentOrgPADInfo = ref<PADInfo>(undefined);
    const currentOrganizationType = ref<string>(undefined);
    const setCurrentOrganizationPADInfo =
      ref<(padInfo: PADInfo) => void>(undefined);
    const transitNumber = ref<string>("");
    const institutionNumber = ref<string>("");
    const accountNumber = ref<string>("");
    const isTOSAccepted = ref<boolean>(false);
    const isAcknowledged = ref<boolean>(false);
    const isTouched = ref<boolean>(false);
    const isStartedEditing = ref<boolean>(false);
    const bankInfoDialog = ref<boolean>(false);
    const $refs = ref<{
      preAuthDebitForm: HTMLFormElement;
    }>(undefined);
    const transitNumberRules = ref([
      (v) => !!v || "Transit Number is required",
      (v) => v.length >= 4 || "Transit Number should be minimum of 4 digits",
    ]);
    const institutionNumberRules = ref([
      (v) => !!v || "Institution Number is required",
      (v) => v.length === 3 || "Institution Number should be 3 digits",
    ]);
    const accountNumberRules = ref([
      (v) => !!v || "Account Number is required",
      (v) =>
        (v.length >= 7 && v.length <= 12) ||
        "Account Number should be between 7 to 12 digits",
    ]);
    const accountMask = ref(CommonUtils.accountMask());
    const isTermsOfServiceAccepted = computed(() => {
      if (isInitialTOSAccepted.value && !isStartedEditing.value) {
        return true;
      }
      return Object.keys(padInformation.value).length
        ? padInformation.value.isTOSAccepted
        : currentOrgPADInfo.value?.isTOSAccepted;
    });
    const padInfoSubtitle = computed(() => {
      return showPremiumPADInfo.value
        ? "Services will continue to be billed to the linked BC Online account until the mandatory (3) day confirmation period has ended."
        : "This account will not be able to perform any transactions until the mandatory (3) day confirmation period has ended.";
    });
    const acknowledgementLabel = computed(() => {
      return showPremiumPADInfo.value
        ? "I understand that services will continue to be billed to the linked BC Online account until the mandatory (3) day confirmation period has ended."
        : "I understand that this account will not be able to perform any transactions until the mandatory (3) day confirmation period for pre-authorized debit has ended.";
    });
    const showPremiumPADInfo = computed(() => {
      return (
        isChangeView.value || currentOrganizationType.value === Account.PREMIUM
      );
    });
    const emitPreAuthDebitInfo = async () => {
      if (!isStartedEditing.value) {
        await formClear();
      }
      const padInfo: PADInfo = {
        bankTransitNumber: transitNumber.value,
        bankInstitutionNumber: institutionNumber.value,
        bankAccountNumber: accountNumber.value,
        isTOSAccepted: isTOSAccepted.value,
        isAcknowledged: isAcknowledged.value,
      };
      isPreAuthDebitFormValid();
      setCurrentOrganizationPADInfo.value(padInfo);
      isTouched.value = true;
      isPadInfoTouched();
      return padInfo;
    };
    const formClear = () => {
      if (clearOnEdit.value && !isStartedEditing.value) {
        const padInfo: PADInfo = Object.keys(padInformation.value).length
          ? padInformation.value
          : currentOrgPADInfo.value;
        transitNumber.value =
          padInfo?.bankTransitNumber !== transitNumber.value
            ? transitNumber.value
            : "";
        institutionNumber.value =
          padInfo?.bankInstitutionNumber !== institutionNumber.value
            ? institutionNumber.value
            : "";
        accountNumber.value = /X/.test(accountNumber.value)
          ? ""
          : accountNumber.value;
        isTOSAccepted.value = false;
        isStartedEditing.value = true;
      }
    };
    const isPreAuthDebitFormValid = () => {
      const acknowledge = isAcknowledgeNeeded.value
        ? isAcknowledged.value
        : true;
      const tosAccepted = isTOSNeeded.value ? isTOSAccepted.value : true;
      return (
        (ctx.refs.preAuthDebitForm?.validate() && tosAccepted && acknowledge) ||
        false
      );
    };
    const isPadInfoTouched = () => {
      return isTouched.value;
    };
    const isTermsAccepted = (isAccepted) => {
      isTOSAccepted.value = isAccepted;
      isTouched.value = true;
      emitPreAuthDebitInfo();
    };
    onMounted(() => {
      const padInfo: PADInfo = Object.keys(padInformation.value).length
        ? padInformation.value
        : currentOrgPADInfo.value;
      transitNumber.value = padInfo?.bankTransitNumber || "";
      institutionNumber.value = padInfo?.bankInstitutionNumber || "";
      accountNumber.value = padInfo?.bankAccountNumber || "";
      isTOSAccepted.value =
        isInitialTOSAccepted.value || padInfo?.isTOSAccepted || false;
      setCurrentOrganizationPADInfo.value(padInfo);
      ctx.root.$nextTick(() => {
        if (isTOSAccepted.value) {
          isPreAuthDebitFormValid();
        }
      });
    });
    return {
      currentOrgPADInfo,
      currentOrganizationType,
      currentOrgPADInfo,
      currentOrganizationType,
      setCurrentOrganizationPADInfo,
      transitNumber,
      institutionNumber,
      accountNumber,
      isTOSAccepted,
      isAcknowledged,
      isTouched,
      isStartedEditing,
      bankInfoDialog,
      $refs,
      transitNumberRules,
      institutionNumberRules,
      accountNumberRules,
      accountMask,
      isTermsOfServiceAccepted,
      padInfoSubtitle,
      acknowledgementLabel,
      showPremiumPADInfo,
      emitPreAuthDebitInfo,
      formClear,
      isPreAuthDebitFormValid,
      isPadInfoTouched,
      isTermsAccepted,
    };
  },
});
