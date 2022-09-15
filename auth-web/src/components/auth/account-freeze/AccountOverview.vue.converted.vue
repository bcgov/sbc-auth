import {
  defineComponent,
  computed,
  ref,
  onMounted,
} from "@vue/composition-api";
import { Component, Mixins, Prop } from "vue-property-decorator";
import { mapActions, mapMutations, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { FailedInvoice } from "@/models/invoice";
import { Organization } from "@/models/Organization";
import Steppable from "@/components/auth/common/stepper/Steppable.vue";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const calculateFailedInvoices = () =>
      ctx.root.$store.dispatch("org/calculateFailedInvoices");
    const currentOrganization = ref<Organization>(undefined);
    const calculateFailedInvoices = ref<() => FailedInvoice>(undefined);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const nsfFee = ref<number>(0);
    const nsfCount = ref<number>(0);
    const totalTransactionAmount = ref<number>(0);
    const totalAmountToPay = ref<number>(0);
    const totalPaidAmount = ref<number>(0);
    const suspendedDate = computed(() => {
      return currentOrganization.value?.suspendedOn
        ? formatDate.value(new Date(currentOrganization.value.suspendedOn))
        : "";
    });
    const goNext = () => {
      stepForward();
    };
    const downloadTransactionPDF = () => {};
    onMounted(async () => {
      const failedInvoices: FailedInvoice =
        await calculateFailedInvoices.value();
      nsfCount.value = failedInvoices?.nsfCount || 0;
      totalTransactionAmount.value =
        failedInvoices?.totalTransactionAmount || 0;
      nsfFee.value = failedInvoices?.nsfFee || 0;
      totalAmountToPay.value = failedInvoices?.totalAmountToPay || 0;
    });
    return {
      currentOrganization,
      calculateFailedInvoices,
      currentOrganization,
      calculateFailedInvoices,
      formatDate,
      nsfFee,
      nsfCount,
      totalTransactionAmount,
      totalAmountToPay,
      totalPaidAmount,
      suspendedDate,
      goNext,
      downloadTransactionPDF,
    };
  },
});
