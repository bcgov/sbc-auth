import {
  defineComponent,
  toRefs,
  ref,
  computed,
  onMounted,
} from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { OrgProduct, Organization } from "@/models/Organization";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import NextPageMixin from "@/components/auth/mixins/NextPageMixin.vue";
import Product from "@/components/auth/common/Product.vue";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const userModule = namespace("user");
export default defineComponent({
  components: {
    ConfirmCancelButton,
    Product,
  },
  props: {
    isStepperView: { default: false, type: Boolean },
    noBackButton: { default: false, type: Boolean },
    readOnly: { default: false, type: Boolean },
    orgId: { default: undefined, type: Number },
  },
  setup(props, ctx) {
    const { isStepperView, noBackButton, readOnly, orgId } = toRefs(props);
    const isLoading = ref<boolean>(false);
    const expandedProductCode = ref<string>("");
    const $refs = ref<{
      form: HTMLFormElement;
    }>(undefined);
    const isFormValid = computed(() => {
      return currentSelectedProducts && currentSelectedProducts.length > 0;
    });
    const setup = async () => {
      isLoading.value = true;
      if (readOnly.value) {
        await getOrgProducts(orgId.value);
        setSubscribedProducts();
      } else {
        await getProductList();
      }
      isLoading.value = false;
    };
    const setSelectedProduct = (productDetails) => {
      const productCode = productDetails.code;
      const forceRemove = productDetails.forceRemove;
      if (productCode) {
        addToCurrentSelectedProducts({ productCode: productCode, forceRemove });
      }
    };
    const toggleProductDetails = (productCode) => {
      expandedProductCode.value = productCode;
    };
    const goBack = () => {
      stepBack();
    };
    const next = () => {
      setResetAccountTypeOnSetupAccount(true);
      stepForward();
    };
    const cancel = () => {
      ctx.root.$router.push("/");
    };
    onMounted(async () => {
      await setup();
    });
    return {
      isLoading,
      expandedProductCode,
      $refs,
      isFormValid,
      setup,
      setSelectedProduct,
      toggleProductDetails,
      goBack,
      next,
      cancel,
    };
  },
});
