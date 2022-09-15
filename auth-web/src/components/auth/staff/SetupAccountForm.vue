import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { AccessType, Pages } from "@/util/constants";
import {
  AccountType,
  ProductCode,
  Products,
  ProductsRequestBody,
} from "@/models/Staff";
import { Component, Vue } from "vue-property-decorator";
import {
  CreateRequestBody,
  MembershipType,
  Organization,
} from "@/models/Organization";
import { mapActions, mapState } from "vuex";
import { CreateRequestBody as InvitationRequestBody } from "@/models/Invitation";
import ModalDialog from "@/components/auth/common/ModalDialog.vue";
import OrgModule from "@/store/modules/org";
import StaffModule from "@/store/modules/staff";
import { getModule } from "vuex-module-decorators";
export default defineComponent({
  components: {
    ModalDialog,
  },
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const products = computed(() => ctx.root.$store.state.staff.products);
    const accountTypes = computed(
      () => ctx.root.$store.state.staff.accountTypes
    );
    const createOrgByStaff = () =>
      ctx.root.$store.dispatch("org/createOrgByStaff");
    const addProductsToOrg = () =>
      ctx.root.$store.dispatch("org/addProductsToOrg");
    const createInvitation = () =>
      ctx.root.$store.dispatch("org/createInvitation");
    const getProducts = () => ctx.root.$store.dispatch("staff/getProducts");
    const getAccountTypes = () =>
      ctx.root.$store.dispatch("staff/getAccountTypes");
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const staffStore = ref(getModule(StaffModule, ctx.root.$store));
    const accountName = ref<string>("");
    const accountType = ref<string>("");
    const errorMessage = ref<string>("");
    const saving = ref(false);
    const loader = ref(false);
    const selectedProducts = ref<ProductCode[]>([]);
    const email = ref("");
    const emailConfirm = ref("");
    const dialogTitle = ref("");
    const dialogText = ref("");
    const createOrgByStaff =
      ref<(requestBody: CreateRequestBody) => Promise<Organization>>(undefined);
    const addProductsToOrg =
      ref<(productsRequestBody: ProductsRequestBody) => Promise<Products>>(
        undefined
      );
    const getProducts = ref<() => Promise<ProductCode[]>>(undefined);
    const getAccountTypes = ref<() => Promise<AccountType[]>>(undefined);
    const createInvitation = ref<(Invitation) => Promise<void>>(undefined);
    const products = ref<ProductCode[]>(undefined);
    const accountTypes = ref<AccountType[]>(undefined);
    const $refs = ref<{
      directorSearchForm: HTMLFormElement;
      errorDialog: ModalDialog;
    }>(undefined);
    const accountNameRules = ref([(v) => !!v || "An account name is required"]);
    const emailRules = ref([
      (v) => !!v || "An email address is required",
      (v) => /.+@.+\..+/.test(v) || "Invalid Email Address",
    ]);
    const emailMatchError = () => {
      return email.value === emailConfirm.value
        ? null
        : "Email Address does not match";
    };
    const isFormValid = (): boolean => {
      return (
        !!accountName.value &&
        selectedProducts.value.length &&
        !emailMatchError() &&
        ctx.refs.directorSearchForm.validate()
      );
    };
    const save = async () => {
      loader.value = saving.value;
      if (isFormValid()) {
        const createRequestBody: CreateRequestBody = {
          name: accountName.value,
          typeCode: accountType.value,
          accessType: AccessType.ANONYMOUS,
        };
        const productsSelected: Products[] = selectedProducts.value.map(
          (prod) => {
            return {
              productCode: prod.code,
              productRoles: ["search"],
            };
          }
        );
        const addProductsRequestBody: ProductsRequestBody = {
          subscriptions: productsSelected,
        };
        try {
          saving.value = true;
          const organization = await createOrgByStaff.value(createRequestBody);
          await addProductsToOrg.value(addProductsRequestBody);
          await createInvitation.value({
            recipientEmail: email.value,
            sentDate: new Date(),
            membership: [
              { membershipType: MembershipType.Admin, orgId: organization.id },
            ],
          });
          saving.value = false;
          loader.value = saving.value;
          ctx.root.$router.push({
            path: `/staff-setup-account-success/${AccessType.ANONYMOUS.toLowerCase()}/${
              accountName.value
            }`,
          });
        } catch (err) {
          saving.value = false;
          switch (err.response.status) {
            case 409:
              errorMessage.value =
                "An account with this name already exists. Try a different account name.";
              break;
            case 400:
              if (err.response.data.code === "MAX_NUMBER_OF_ORGS_LIMIT") {
                errorMessage.value = "Maximum number of accounts reached";
              } else {
                errorMessage.value = "Invalid account name";
              }
              break;
            default:
              errorMessage.value =
                "Something went wrong while attempting to create this account. Please try again later.";
          }
          showEntityNotFoundModal(errorMessage.value);
          loader.value = saving.value;
        }
      }
    };
    const cancel = () => {
      ctx.root.$router.push({ path: Pages.STAFF_DASHBOARD });
    };
    const showEntityNotFoundModal = (msg?) => {
      dialogTitle.value = "An error has occured";
      dialogText.value =
        msg ||
        "Something went wrong while attempting to create this account. Please try again later.";
      ctx.refs.errorDialog.open();
    };
    const close = () => {
      ctx.refs.errorDialog.close();
    };
    onMounted(async () => {
      await getProducts.value();
      await getAccountTypes.value();
      if (accountTypes.value && accountTypes.value.length) {
        const defaultAcc = accountTypes.value.filter(
          (account) => account.default
        );
        accountType.value =
          defaultAcc && defaultAcc.length && defaultAcc[0].code
            ? defaultAcc[0].code
            : accountType.value;
      }
    });
    return {
      currentOrganization,
      products,
      accountTypes,
      createOrgByStaff,
      addProductsToOrg,
      createInvitation,
      getProducts,
      getAccountTypes,
      orgStore,
      staffStore,
      accountName,
      accountType,
      errorMessage,
      saving,
      loader,
      selectedProducts,
      email,
      emailConfirm,
      dialogTitle,
      dialogText,
      createOrgByStaff,
      addProductsToOrg,
      getProducts,
      getAccountTypes,
      createInvitation,
      products,
      accountTypes,
      $refs,
      accountNameRules,
      emailRules,
      emailMatchError,
      isFormValid,
      save,
      cancel,
      showEntityNotFoundModal,
      close,
    };
  },
});
