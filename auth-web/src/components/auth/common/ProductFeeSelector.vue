import {
  defineComponent,
  toRefs,
  ref,
  watch,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { AccountFee, OrgProductFeeCode } from "@/models/Organization";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
export default defineComponent({
  props: {
    orgProductFeeCodes: {
      default: undefined,
      type: Object as PropType<OrgProductFeeCode>,
    },
    canSelect: { default: false, type: Boolean },
    productCode: { default: "", type: Object as PropType<any> },
    selectedApplyFilingFees: {
      default: undefined,
      type: Object as PropType<any>,
    },
  },
  setup(props, ctx) {
    const {
      orgProductFeeCodes,
      canSelect,
      productCode,
      selectedApplyFilingFees,
    } = toRefs(props);
    const applyFilingFees = ref("false");
    const serviceFeeCode = ref("");
    const index = ref(1);
    const applyFilingFeesValues = ref([
      {
        text: "Yes",
        value: "true",
      },
      {
        text: "No",
        value: "false",
      },
    ]);
    const $refs = ref<{
      productFeeForm: HTMLFormElement;
    }>(undefined);
    const applyFilingFeesRules = ref([
      (v) => !!v || "A statutory fee is required",
    ]);
    const serviceFeeCodeRules = ref([
      (v) => !!v || "A service fee is required",
    ]);
    const updateFilingFees = (val, oldVal) => {
      if (
        val?.existingApplyFilingFees?.toString() !==
        oldVal?.existingApplyFilingFees?.toString()
      ) {
        applyFilingFees.value = val?.existingApplyFilingFees?.toString() || "";
      }
      if (
        val?.existingserviceFeeCode?.toString() !==
        oldVal?.existingserviceFeeCode?.toString()
      ) {
        serviceFeeCode.value = val?.existingserviceFeeCode || "";
      }
    };
    const validateNow = () => {
      const isFormValid = ctx.refs.productFeeForm?.validate();
      ctx.emit("emit-product-fee-change", isFormValid);
    };
    const displayProductFee = (feeAmount: number): string => {
      return `$ ${feeAmount.toFixed(2)} Service fee`;
    };
    const selectChange = () => {
      const accountFee: AccountFee = {
        product: productCode.value,
        applyFilingFees: applyFilingFees.value === "true",
        serviceFeeCode: serviceFeeCode.value,
      };
      return accountFee;
    };
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    watch(selectedApplyFilingFees, updateFilingFees, { deep: true });
    onMounted(() => {
      applyFilingFees.value =
        selectedApplyFilingFees.value?.existingApplyFilingFees?.toString() ||
        applyFilingFees.value;
      serviceFeeCode.value =
        selectedApplyFilingFees.value?.existingserviceFeeCode ||
        serviceFeeCode.value;
    });
    return {
      applyFilingFees,
      serviceFeeCode,
      index,
      applyFilingFeesValues,
      $refs,
      applyFilingFeesRules,
      serviceFeeCodeRules,
      updateFilingFees,
      validateNow,
      displayProductFee,
      selectChange,
      getIndexedTag,
    };
  },
});
