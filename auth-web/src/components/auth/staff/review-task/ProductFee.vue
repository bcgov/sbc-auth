import { defineComponent, toRefs, ref, onMounted } from "@vue/composition-api";
import {
  AccountFee,
  AccountFeeDTO,
  OrgProduct,
  OrgProductFeeCode,
} from "@/models/Organization";
import { Component, Prop, Vue } from "vue-property-decorator";
import { namespace } from "vuex-class";
import { productStatus } from "@/util/constants";
const orgModule = namespace("org");
export default defineComponent({
  props: {
    tabNumber: { default: null, type: Number },
    title: { default: "Product Fee", type: String },
    canSelect: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { tabNumber, title, canSelect } = toRefs(props);
    const accountFeesDTO = ref<AccountFeeDTO[]>([]);
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
    const validateNow = () => {
      const isFormValid = ctx.refs.productFeeForm?.validate();
      ctx.emit("emit-product-fee-change", isFormValid);
    };
    const displayProductName = (productCode: string): string => {
      return orgProducts?.find((orgProduct) => orgProduct.code === productCode)
        ?.description;
    };
    const displayProductFee = (feeAmount: number): string => {
      return `$ ${feeAmount.toFixed(2)} Service fee`;
    };
    const selectChange = (): void => {
      const accountFees: AccountFee[] = [];
      accountFeesDTO.value.forEach((accountFeeDTO: AccountFeeDTO) => {
        const accountFee: AccountFee = {
          product: accountFeeDTO.product,
          applyFilingFees: accountFeeDTO.applyFilingFees === "true",
          serviceFeeCode: accountFeeDTO.serviceFeeCode,
        };
        accountFees.push(accountFee);
      });
      setCurrentAccountFees(accountFees);
    };
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    onMounted(() => {
      if (!accountFees.length) {
        orgProducts.forEach((orgProduct: OrgProduct) => {
          if (orgProduct.subscriptionStatus === productStatus.ACTIVE) {
            const accountFeeDTO: AccountFeeDTO = {
              product: orgProduct.code,
            };
            accountFeesDTO.value.push(accountFeeDTO);
          }
        });
      } else {
        accountFeesDTO.value = JSON.parse(JSON.stringify(accountFees));
        accountFeesDTO.value.map((accountFee: AccountFeeDTO) => {
          accountFee.applyFilingFees = accountFee.applyFilingFees.toString();
        });
      }
    });
    return {
      accountFeesDTO,
      applyFilingFeesValues,
      $refs,
      applyFilingFeesRules,
      serviceFeeCodeRules,
      validateNow,
      displayProductName,
      displayProductFee,
      selectChange,
      getIndexedTag,
    };
  },
});
