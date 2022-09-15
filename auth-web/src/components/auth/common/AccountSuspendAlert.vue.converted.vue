import {
  defineComponent,
  ref,
  computed,
  onMounted,
} from "@vue/composition-api";
import { Component, Vue } from "vue-property-decorator";
import { Member, Organization } from "@/models/Organization";
import { AccountStatus } from "@/util/constants";
import { Code } from "@/models/Code";
import CommonUtils from "@/util/common-util";
import { FailedInvoice } from "@/models/invoice";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const CodesModule = namespace("codes");
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const totalTransactionAmount = ref(0);
    const totalAmountToPay = ref(0);
    const totalPaidAmount = ref(0);
    const suspendedDate = computed(() => {
      return currentOrganization?.suspendedOn
        ? formatDate.value(new Date(currentOrganization.suspendedOn))
        : "";
    });
    const isSuspendedForNSF = computed((): boolean => {
      return currentOrganization?.statusCode === AccountStatus.NSF_SUSPENDED;
    });
    const suspendedBy = computed((): string => {
      return currentOrganization?.decisionMadeBy;
    });
    const suspendedReason = (): string => {
      return suspensionReasonCodes?.find(
        (suspensionReasonCode) =>
          suspensionReasonCode?.code ===
          currentOrganization?.suspensionReasonCode
      )?.desc;
    };
    onMounted(async () => {
      if (isSuspendedForNSF.value) {
        const failedInvoices: FailedInvoice = await calculateFailedInvoices();
        totalTransactionAmount.value =
          failedInvoices.totalTransactionAmount || 0;
        totalAmountToPay.value = failedInvoices.totalAmountToPay || 0;
      }
    });
    return {
      formatDate,
      totalTransactionAmount,
      totalAmountToPay,
      totalPaidAmount,
      suspendedDate,
      isSuspendedForNSF,
      suspendedBy,
      suspendedReason,
    };
  },
});
