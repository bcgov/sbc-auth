import {
  defineComponent,
  toRefs,
  ref,
  computed,
  onMounted,
  PropType,
} from "@vue/composition-api";
import {
  AccessType,
  Account,
  PaymentTypes,
  SessionStorageKeys,
} from "@/util/constants";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import { Organization, PADInfo } from "@/models/Organization";
import { BcolProfile } from "@/models/bcol";
import ConfigHelper from "@/util/config-helper";
import GLPaymentForm from "@/components/auth/common/GLPaymentForm.vue";
import LinkedBCOLBanner from "@/components/auth/common/LinkedBCOLBanner.vue";
import PADInfoForm from "@/components/auth/common/PADInfoForm.vue";
import { namespace } from "vuex-class";
const PAYMENT_METHODS = {
  [PaymentTypes.CREDIT_CARD]: {
    type: PaymentTypes.CREDIT_CARD,
    icon: "mdi-credit-card-outline",
    title: "Credit Card",
    subtitle: "Pay for transactions individually with your credit card.",
    description: `You don't need to provide any credit card information with your account. Credit card information will be requested when you are ready to complete a transaction.`,
    isSelected: false,
  },
  [PaymentTypes.PAD]: {
    type: PaymentTypes.PAD,
    icon: "mdi-bank-outline",
    title: "Pre-authorized Debit",
    subtitle: "Automatically debit a bank account when payments are due.",
    description: "",
    isSelected: false,
  },
  [PaymentTypes.BCOL]: {
    type: PaymentTypes.BCOL,
    icon: "mdi-link-variant",
    title: "BC Online",
    subtitle: "Use your linked BC Online account for payment.",
    description: "",
    isSelected: false,
  },
  [PaymentTypes.ONLINE_BANKING]: {
    type: PaymentTypes.ONLINE_BANKING,
    icon: "mdi-bank-outline",
    title: "Online Banking",
    subtitle:
      "Pay for products and services through your financial institutions website.",
    description: `
        <p><strong>Online banking is currently limited to the following institutions:</strong></p>
        <p>
          <ul>
            <li>Bank of Montreal</li>
            <li>Central 1 Credit Union</li>
            <li>Coast Capital Savings</li>
            <li>HSBC</li>
            <li>Royal Bank of Canada (RBC)</li>
            <li>Scotiabank</li>
            <li>TD Canada Trust (TD)</li>
          </ul>
        </p>
        <p>
          Instructions to set up your online banking payment solution will be available in the <strong>Payment Methods</strong> section of your account settings once your account has been created.
        </p>
        <p class="mb-0">
          BC Registries and Online Services <strong>must receive payment in full</strong> from your financial institution prior to the release of items purchased through this service. Receipt of an online banking payment generally takes 3-4 days from when you make the payment with your financial institution.
        </p>`,
    isSelected: false,
  },
};
const orgModule = namespace("org");
export default defineComponent({
  components: {
    PADInfoForm,
    LinkedBCOLBanner,
    GLPaymentForm,
  },
  props: {
    currentOrgType: { default: "", type: String },
    currentOrganization: {
      default: undefined,
      type: Object as PropType<Organization>,
    },
    currentSelectedPaymentMethod: { default: "", type: String },
    currentOrgPaymentType: { default: undefined, type: String },
    isChangeView: { default: false, type: Boolean },
    isAcknowledgeNeeded: { default: true, type: Boolean },
    isTouchedUpdate: { default: false, type: Boolean },
    isInitialTOSAccepted: { default: false, type: Boolean },
    isInitialAcknowledged: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const {
      currentOrgType,
      currentOrganization,
      currentSelectedPaymentMethod,
      currentOrgPaymentType,
      isChangeView,
      isAcknowledgeNeeded,
      isTouchedUpdate,
      isInitialTOSAccepted,
      isInitialAcknowledged,
    } = toRefs(props);
    const selectedPaymentMethod = ref<string>("");
    const paymentTypes = ref(PaymentTypes);
    const padInfo = ref<PADInfo>({} as PADInfo);
    const isTouched = ref<boolean>(false);
    const ejvPaymentInformationTitle = ref("General Ledger Information");
    const paymentsPerAccountType = ref(
      ConfigHelper.paymentsAllowedPerAccountType()
    );
    const allowedPaymentMethods = computed(() => {
      const paymentMethods = [];
      if (currentOrgType.value) {
        const paymentTypes = paymentsPerAccountType.value[currentOrgType.value];
        paymentTypes.forEach((paymentType) => {
          if (PAYMENT_METHODS[paymentType]) {
            paymentMethods.push(PAYMENT_METHODS[paymentType]);
          }
        });
      }
      return paymentMethods;
    });
    const forceEditModeBCOL = computed(() => {
      return (
        currentSelectedPaymentMethod.value === PaymentTypes.BCOL &&
        currentOrgPaymentType.value !== undefined &&
        currentOrgPaymentType.value !== PaymentTypes.BCOL
      );
    });
    const isPaymentEJV = computed(() => {
      return currentSelectedPaymentMethod.value === PaymentTypes.EJV;
    });
    const isPadInfoTouched = (isTouched) => {
      isTouched.value = isTouched;
    };
    const isPaymentSelected = (payment) => {
      return selectedPaymentMethod.value === payment.type;
    };
    const paymentMethodSelected = (payment, isTouched = true) => {
      selectedPaymentMethod.value = payment.type;
      isTouched.value = isTouched;
      if (isTouchedUpdate.value) {
        return {
          selectedPaymentMethod: selectedPaymentMethod.value,
          isTouched,
        };
      }
      return selectedPaymentMethod.value;
    };
    const getPADInfo = (padInfo: PADInfo) => {
      padInfo.value = padInfo;
      return padInfo.value;
    };
    const getBcolInfo = (bcolProfile: BcolProfile) => {
      return bcolProfile;
    };
    const isPADValid = (isValid) => {
      if (isValid) {
        paymentMethodSelected({ type: PaymentTypes.PAD }, isTouched.value);
      }
      return isValid;
    };
    onMounted(async () => {
      paymentMethodSelected(
        { type: currentSelectedPaymentMethod.value },
        false
      );
      if (isPaymentEJV.value) {
        await fetchCurrentOrganizationGLInfo(currentOrganization.value?.id);
      }
    });
    return {
      selectedPaymentMethod,
      paymentTypes,
      padInfo,
      isTouched,
      ejvPaymentInformationTitle,
      paymentsPerAccountType,
      allowedPaymentMethods,
      forceEditModeBCOL,
      isPaymentEJV,
      isPadInfoTouched,
      isPaymentSelected,
      paymentMethodSelected,
      getPADInfo,
      getBcolInfo,
      isPADValid,
    };
  },
});
