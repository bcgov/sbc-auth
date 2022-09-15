import {
  defineComponent,
  toRefs,
  ref,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue } from "vue-property-decorator";
import PayWithCreditCard from "@/components/pay/PayWithCreditCard.vue";
import PayWithOnlineBanking from "@/components/pay/PayWithOnlineBanking.vue";
import PaymentServices from "@/services/payment.services";
export default defineComponent({
  components: {
    PayWithCreditCard,
    PayWithOnlineBanking,
  },
  props: {
    paymentCardData: { type: Object as PropType<any> },
    showPayWithOnlyCC: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { paymentCardData, showPayWithOnlyCC } = toRefs(props);
    const payWithCreditCard = ref<boolean>(false);
    const balanceDue = ref(0);
    const totalBalanceDue = ref(0);
    const cfsAccountId = ref<string>("");
    const payeeName = ref<string>("");
    const onlineBankingData = ref<any>([]);
    const credit = ref<number>(null);
    const doHaveCredit = ref<boolean>(false);
    const overCredit = ref<boolean>(false);
    const partialCredit = ref<boolean>(false);
    const creditBalance = ref(0);
    const paymentId = ref<string>(undefined);
    const totalPaid = ref(0);
    const cancel = () => {
      if (showPayWithOnlyCC.value) {
        emitBtnClick("complete-online-banking");
      } else {
        payWithCreditCard.value = false;
      }
    };
    const emitBtnClick = async (eventName) => {
      if (eventName === "complete-online-banking" && doHaveCredit.value) {
        await PaymentServices.applycredit(paymentId.value);
      }
      ctx.emit(eventName);
    };
    onMounted(() => {
      totalBalanceDue.value = paymentCardData.value?.totalBalanceDue || 0;
      totalPaid.value = paymentCardData.value?.totalPaid || 0;
      balanceDue.value = totalBalanceDue.value - totalPaid.value;
      payeeName.value = paymentCardData.value.payeeName;
      cfsAccountId.value = paymentCardData.value?.cfsAccountId || "";
      payWithCreditCard.value = showPayWithOnlyCC.value;
      credit.value = paymentCardData.value.credit;
      doHaveCredit.value =
        paymentCardData.value.credit !== null &&
        paymentCardData.value.credit !== 0;
      if (doHaveCredit.value) {
        overCredit.value = credit.value >= totalBalanceDue.value;
        partialCredit.value = credit.value < totalBalanceDue.value;
        balanceDue.value = overCredit.value
          ? balanceDue.value
          : balanceDue.value - credit.value;
      }
      creditBalance.value = overCredit.value
        ? credit.value - balanceDue.value
        : 0;
      paymentId.value = paymentCardData.value.paymentId;
      onlineBankingData.value = {
        totalBalanceDue: balanceDue.value,
        payeeName: payeeName.value,
        cfsAccountId: cfsAccountId.value,
        overCredit: overCredit.value,
        partialCredit: partialCredit.value,
        creditBalance: creditBalance.value,
        credit: credit.value,
      };
    });
    return {
      payWithCreditCard,
      balanceDue,
      totalBalanceDue,
      cfsAccountId,
      payeeName,
      onlineBankingData,
      credit,
      doHaveCredit,
      overCredit,
      partialCredit,
      creditBalance,
      paymentId,
      totalPaid,
      cancel,
      emitBtnClick,
    };
  },
});
