import {
  defineComponent,
  toRefs,
  ref,
  computed,
  watch,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { OrgProductFeeCode } from "@/models/Organization";
import ProductFeeSelector from "@/components/auth/common/ProductFeeSelector.vue";
export default defineComponent({
  components: {
    ProductFeeSelector,
  },
  props: {
    orgProduct: { default: undefined, type: Object as PropType<any> },
    orgProductFeeCodes: {
      default: undefined,
      type: Array as Proptype<OrgProductFeeCode[]>,
    },
    isProductActionLoading: { default: false, type: Boolean },
    isProductActionCompleted: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const {
      orgProduct,
      orgProductFeeCodes,
      isProductActionLoading,
      isProductActionCompleted,
    } = toRefs(props);
    const viewOnlyMode = ref(true);
    const selectedFee = ref<any>({});
    const applyFilling = computed(() => {
      return orgProduct.value?.applyFilingFees === true ? "Yes" : "No";
    });
    const getProductFee = computed(() => {
      const fee: any = productFee();
      return fee && fee.amount ? `$ ${fee && fee?.amount.toFixed(2)}` : "";
    });
    const existingFeeCodes = computed(() => {
      const existingApplyFilingFees = selectedFee.value?.applyFilingFees
        ? selectedFee.value?.applyFilingFees
        : orgProduct.value?.applyFilingFees;
      const fee: any = productFee();
      const selectedFeeCode = fee && fee.code;
      const existingserviceFeeCode = selectedFee.value?.serviceFeeCode
        ? selectedFee.value?.serviceFeeCode
        : selectedFeeCode;
      return { existingApplyFilingFees, existingserviceFeeCode };
    });
    const onProductActionCompleted = (val, oldVal) => {
      if (val && val !== oldVal) {
        updateViewOnlyMode(true);
      }
    };
    const updateViewOnlyMode = (mode = true) => {
      viewOnlyMode.value = mode;
      if (mode === false) {
        selectedFee.value = {};
      }
    };
    const productFee = () => {
      if (orgProductFeeCodes.value.length > 0) {
        const fees = orgProductFeeCodes.value.filter(
          (fee) => fee.code === orgProduct.value.serviceFeeCode
        );
        return fees && fees[0];
      }
      return {};
    };
    const updatedProductFee = (data) => {
      selectedFee.value = data;
      return selectedFee.value;
    };
    const saveProductFee = () => {
      return selectedFee.value;
    };
    watch(isProductActionCompleted, onProductActionCompleted);
    return {
      viewOnlyMode,
      selectedFee,
      applyFilling,
      getProductFee,
      existingFeeCodes,
      onProductActionCompleted,
      updateViewOnlyMode,
      productFee,
      updatedProductFee,
      saveProductFee,
    };
  },
});
