import { defineComponent, toRefs, ref, computed } from "@vue/composition-api";
import { Account, PaymentTypes } from "@/util/constants";
import { Component, Emit, Mixins, Prop } from "vue-property-decorator";
import ConfirmCancelButton from "@/components/auth/common/ConfirmCancelButton.vue";
import { Organization } from "@/models/Organization";
import PaymentMethods from "@/components/auth/common/PaymentMethods.vue";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
export default defineComponent({
  components: {
    ConfirmCancelButton,
    PaymentMethods,
  },
  props: { readOnly: { default: false, type: Boolean } },
  setup(props, ctx) {
    const { readOnly } = toRefs(props);
    const selectedPaymentMethod = ref<string>("");
    const isPADValid = ref<boolean>(false);
    const pageSubTitle = computed(() => {
      return "Select the payment method for this account.";
    });
    const isEnableCreateBtn = computed(() => {
      return selectedPaymentMethod.value === PaymentTypes.PAD
        ? selectedPaymentMethod.value && isPADValid.value
        : !!selectedPaymentMethod.value;
    });
    const goBack = () => {
      stepBack();
    };
    const setSelectedPayment = (payment) => {
      selectedPaymentMethod.value = payment;
      setCurrentOrganizationPaymentType(selectedPaymentMethod.value);
    };
    const setPADValid = (isValid) => {
      isPADValid.value = isValid;
    };
    const save = () => {
      setCurrentOrganizationPaymentType(selectedPaymentMethod.value);
      createAccount();
    };
    const createAccount = () => {};
    return {
      selectedPaymentMethod,
      isPADValid,
      pageSubTitle,
      isEnableCreateBtn,
      goBack,
      setSelectedPayment,
      setPADValid,
      save,
      createAccount,
    };
  },
});
