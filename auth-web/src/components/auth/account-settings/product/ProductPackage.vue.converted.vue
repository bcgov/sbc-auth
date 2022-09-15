import {
  defineComponent,
  ref,
  computed,
  onMounted,
} from "@vue/composition-api";
import { AccessType, Account, Role, productStatus } from "@/util/constants";
import {
  AccountFee,
  OrgProduct,
  OrgProductCode,
  OrgProductFeeCode,
  OrgProductsRequestBody,
  Organization,
} from "@/models/Organization";
import { Component, Mixins, Vue } from "vue-property-decorator";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import { KCUserProfile } from "sbc-common-components/src/models/KCUserProfile";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import Product from "@/components/auth/common/Product.vue";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const userModule = namespace("user");
export default defineComponent({
  components: {
    Product,
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const isBtnSaved = ref(false);
    const disableSaveBtn = ref(false);
    const isLoading = ref<boolean>(false);
    const isProductActionLoading = ref<boolean>(false);
    const dialogTitle = ref("");
    const dialogText = ref("");
    const dialogIcon = ref("");
    const submitRequestValidationError = ref("");
    const expandedProductCode = ref<string>("");
    const AccountEnum = ref(Account);
    const orgProductsFees = ref<any>("");
    const orgProductFeeCodes = ref<any>("");
    const isProductActionCompleted = ref<boolean>(false);
    const $refs = ref<{
      confirmDialog: ModalDialog;
    }>(undefined);
    const canManageAccounts = computed(() => {
      return (
        currentUser?.roles?.includes(Role.StaffManageAccounts) &&
        isVariableFeeAccount()
      );
    });
    const setSelectedProduct = async (productDetails) => {
      const productCode = productDetails.code;
      const forceRemove = productDetails.forceRemove;
      if (productCode) {
        addToCurrentSelectedProducts({ productCode: productCode, forceRemove });
      }
    };
    const setup = async () => {
      isLoading.value = true;
      resetCurrentSelectedProducts();
      await loadProduct();
      if (canManageAccounts.value) {
        orgProductsFees.value = await syncCurrentAccountFees(
          currentOrganization.id
        );
        orgProductFeeCodes.value = await fetchOrgProductFeeCodes();
      }
      isLoading.value = false;
    };
    const toggleProductDetails = (productCode: string) => {
      expandedProductCode.value = productCode;
    };
    const loadProduct = async () => {
      try {
        await getOrgProducts(currentOrganization.id);
      } catch (err) {
        console.log("Error while loading products ", err);
      }
    };
    const orgProductDetails = (product) => {
      const { code: productCode, subscriptionStatus } = product;
      let productData;
      if (orgProductsFees.value && orgProductsFees.value.length > 0) {
        const orgProd = orgProductsFees.value.filter(
          (orgProduct) => orgProduct.product === productCode
        );
        productData = orgProd && orgProd[0];
      }
      if (!productData && subscriptionStatus !== productStatus.NOT_SUBSCRIBED) {
        productData = {
          product: productCode,
          applyFilingFees: true,
          serviceFeeCode: "TRF01",
        };
      }
      return productData || {};
    };
    const isVariableFeeAccount = () => {
      const accessType: any = currentOrganization.accessType;
      return [AccessType.GOVM, AccessType.GOVN].includes(accessType) || false;
    };
    const closeError = () => {
      ctx.refs.confirmDialog.close();
    };
    const submitProductRequest = async () => {
      try {
        if (currentSelectedProducts.length === 0) {
          submitRequestValidationError.value =
            "Select at least one product or service to submit request";
        } else {
          submitRequestValidationError.value = "";
          const productsSelected: OrgProductCode[] =
            currentSelectedProducts.map((code: any) => {
              return { productCode: code };
            });
          const addProductsRequestBody: OrgProductsRequestBody = {
            subscriptions: productsSelected,
          };
          await addOrgProducts(addProductsRequestBody);
          await setup();
          dialogTitle.value = "Access Requested";
          dialogText.value =
            "Request has been submitted. Account will immediately have access to the requested product and service unless staff review is required.";
          dialogIcon.value = "mdi-check";
          ctx.refs.confirmDialog.open();
        }
      } catch (ex) {
        dialogTitle.value = "Product Request Failed";
        dialogText.value = "";
        dialogIcon.value = "mdi-alert-circle-outline";
        ctx.refs.confirmDialog.open();
        console.log("Error while trying to submit product request");
      }
    };
    const saveProductFee = async (accountFees) => {
      const accountFee = { accoundId: currentOrganization.id, accountFees };
      isProductActionLoading.value = true;
      isProductActionCompleted.value = false;
      try {
        await updateAccountFees(accountFee);
        orgProductsFees.value = await syncCurrentAccountFees(
          currentOrganization.id
        );
      } catch (err) {
        console.log("Error while updating product fee ", err);
      } finally {
        isProductActionLoading.value = false;
        isProductActionCompleted.value = true;
      }
    };
    onMounted(async () => {
      setAccountChangedHandler(setup);
      await setup();
    });
    return {
      isBtnSaved,
      disableSaveBtn,
      isLoading,
      isProductActionLoading,
      dialogTitle,
      dialogText,
      dialogIcon,
      submitRequestValidationError,
      expandedProductCode,
      AccountEnum,
      orgProductsFees,
      orgProductFeeCodes,
      isProductActionCompleted,
      $refs,
      canManageAccounts,
      setSelectedProduct,
      setup,
      toggleProductDetails,
      loadProduct,
      orgProductDetails,
      isVariableFeeAccount,
      closeError,
      submitProductRequest,
      saveProductFee,
    };
  },
});
