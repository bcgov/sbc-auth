import {
  defineComponent,
  toRefs,
  ref,
  watch,
  onMounted,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop, Watch } from "vue-property-decorator";
import Vue from "vue";
export default defineComponent({
  props: {
    onlineBankingData: { type: Object as PropType<any> },
    showPayWithOnlyCC: { default: false, type: Boolean },
  },
  setup(props, ctx) {
    const { onlineBankingData, showPayWithOnlyCC } = toRefs(props);
    const payWithCreditCard = ref<boolean>(false);
    const totalBalanceDue = ref(0);
    const cfsAccountId = ref<string>("");
    const payeeName = ref<string>("");
    const overCredit = ref<boolean>(false);
    const creditBalance = ref(0);
    const partialCredit = ref<boolean>(false);
    const credit = ref(0);
    const updateonlineBankingData = async (val, oldVal) => {
      setData();
    };
    const setData = () => {
      totalBalanceDue.value = onlineBankingData.value?.totalBalanceDue || 0;
      payeeName.value = onlineBankingData.value?.payeeName;
      cfsAccountId.value = onlineBankingData.value?.cfsAccountId || "";
      overCredit.value = onlineBankingData.value?.overCredit || false;
      partialCredit.value = onlineBankingData.value?.partialCredit || false;
      creditBalance.value = onlineBankingData.value?.creditBalance || 0;
      credit.value = onlineBankingData.value?.credit || 0;
    };
    watch(onlineBankingData, updateonlineBankingData, { deep: true });
    onMounted(() => {
      setData();
    });
    return {
      payWithCreditCard,
      totalBalanceDue,
      cfsAccountId,
      payeeName,
      overCredit,
      creditBalance,
      partialCredit,
      credit,
      updateonlineBankingData,
      setData,
    };
  },
});
