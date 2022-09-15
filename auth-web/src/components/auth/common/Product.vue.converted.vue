import {
  defineComponent,
  toRefs,
  ref,
  computed,
  watch,
  onMounted,
  PropType,
} from "@vue/composition-api";
import {
  AccountFee,
  OrgProduct,
  OrgProductFeeCode,
} from "@/models/Organization";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import { DisplayModeValues, productStatus } from "@/util/constants";
import LaunchDarklyService from "sbc-common-components/src/services/launchdarkly.services";
import ProductFee from "@/components/auth/common/ProductFeeViewEdit.vue";
import ProductTos from "@/components/auth/common/ProductTOS.vue";
const TOS_NEEDED_PRODUCT = ["VS"];
export default defineComponent({
  components: {
    ProductTos,
    ProductFee,
  },
  props: {
    productDetails: {
      default: undefined,
      type: Object as PropType<OrgProduct>,
    },
    orgProduct: { default: undefined, type: Object as PropType<AccountFee> },
    orgProductFeeCodes: {
      default: undefined,
      type: Object as PropType<OrgProductFeeCode>,
    },
    isProductActionLoading: { default: false, type: Boolean },
    isProductActionCompleted: { default: false, type: Boolean },
    userName: { default: "", type: String },
    orgName: { default: "", type: String },
    isSelected: { default: false, type: Boolean },
    isexpandedView: { default: false, type: Boolean },
    isAccountSettingsView: { default: false, type: Boolean },
    isBasicAccount: { default: false, type: Boolean },
    canManageProductFee: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const {
      productDetails,
      orgProduct,
      orgProductFeeCodes,
      isProductActionLoading,
      isProductActionCompleted,
      userName,
      orgName,
      isSelected,
      isexpandedView,
      isAccountSettingsView,
      isBasicAccount,
      canManageProductFee,
    } = toRefs(props);
    const termsAccepted = ref<boolean>(false);
    const productSelected = ref<boolean>(false);
    const viewOnly = ref(DisplayModeValues.VIEW_ONLY);
    const $refs = ref<{
      tosForm: HTMLFormElement;
    }>(undefined);
    const showProductFee = computed(() => {
      return (
        canManageProductFee.value &&
        orgProduct.value &&
        orgProduct.value.product
      );
    });
    const productLabel = computed(() => {
      const { code } = productDetails.value;
      let subTitle = `${code && code.toLowerCase()}CodeSubtitle` || "";
      let details = `${code && code.toLowerCase()}CodeDescription` || "";
      let decisionMadeIcon = null;
      let decisionMadeColorCode = null;
      if (isAccountSettingsView.value) {
        const status = productDetails.value.subscriptionStatus;
        switch (status) {
          case productStatus.ACTIVE: {
            subTitle = `${code && code.toLowerCase()}CodeActiveSubtitle` || "";
            decisionMadeIcon = "mdi-check-circle";
            decisionMadeColorCode = "success";
            break;
          }
          case productStatus.REJECTED: {
            subTitle =
              `${code && code.toLowerCase()}CodeRejectedSubtitle` || "";
            decisionMadeIcon = "mdi-close-circle";
            decisionMadeColorCode = "error";
            break;
          }
          case productStatus.PENDING_STAFF_REVIEW: {
            subTitle = "productPendingSubtitle";
            decisionMadeIcon = "mdi-clock-outline";
            break;
          }
          default: {
            break;
          }
        }
        if (isBasicAccountAndPremiumProduct.value) {
          subTitle =
            `${code && code.toLowerCase()}CodeUnselectableSubtitle` || "";
          decisionMadeIcon = "mdi-minus-box";
        }
      }
      return { subTitle, details, decisionMadeIcon, decisionMadeColorCode };
    });
    const isTOSNeeded = computed(() => {
      return TOS_NEEDED_PRODUCT.includes(productDetails.value.code);
    });
    const isBasicAccountAndPremiumProduct = computed(() => {
      return isBasicAccount.value && productDetails.value.premiumOnly;
    });
    const hasDecisionNotBeenMade = computed(() => {
      if (!isAccountSettingsView.value) {
        return true;
      }
      if (
        ([productStatus.NOT_SUBSCRIBED] as Array<string>).includes(
          productDetails.value.subscriptionStatus
        )
      ) {
        return true;
      }
      termsAccepted.value = true;
      return false;
    });
    const productFooter = computed(() => {
      return {
        id: "tos",
        component: ProductTos,
        props: {
          userName: userName.value,
          orgName: orgName.value,
          isTOSAlreadyAccepted: termsAccepted.value,
        },
        events: { "tos-status-changed": tosChanged },
        ref: "tosForm",
      };
    });
    const onisSelectedChange = (newValue: boolean) => {
      productSelected.value = newValue;
    };
    const expand = () => {
      return isexpandedView.value ? "" : productDetails.value.code;
    };
    const tosChanged = (termsAccepted: boolean) => {
      termsAccepted.value = termsAccepted;
      selecThisProduct(undefined, true);
    };
    const selecThisProduct = (event, emitFromTos: boolean = false) => {
      let forceRemove = false;
      if (isTOSNeeded.value && !termsAccepted.value) {
        if (!emitFromTos) {
          expand();
        }
        productSelected.value = false;
        forceRemove = true;
      }
      return { ...productDetails.value, forceRemove };
    };
    const saveProductFee = (data) => {
      return data;
    };
    const productBadge = (code: string) => {
      return LaunchDarklyService.getFlag(`product-${code}-status`);
    };
    const productPremTooltipText = (code: string) => {
      return LaunchDarklyService.getFlag(`product-${code}-prem-tooltip`);
    };
    watch(isSelected, onisSelectedChange);
    onMounted(() => {
      productSelected.value = isSelected.value;
    });
    return {
      termsAccepted,
      productSelected,
      viewOnly,
      $refs,
      showProductFee,
      productLabel,
      isTOSNeeded,
      isBasicAccountAndPremiumProduct,
      hasDecisionNotBeenMade,
      productFooter,
      onisSelectedChange,
      expand,
      tosChanged,
      selecThisProduct,
      saveProductFee,
      productBadge,
      productPremTooltipText,
    };
  },
});
