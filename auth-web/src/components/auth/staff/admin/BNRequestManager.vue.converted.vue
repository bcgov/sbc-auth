import { defineComponent, toRefs, ref, watch } from "@vue/composition-api";
import { Component, Prop, Watch } from "vue-property-decorator";
import { RequestTracker, ResubmitBNRequest } from "@/models/request-tracker";
import ResubmitRequestDialog from "@/components/auth/staff/admin/ResubmitRequestDialog.vue";
import Vue from "vue";
import { namespace } from "vuex-class";
const BusinessModule = namespace("business");
export default defineComponent({
  components: {
    ResubmitRequestDialog,
  },
  props: { businessIdentifier: { default: undefined, type: String } },
  setup(props, ctx) {
    const { businessIdentifier } = toRefs(props);
    const headers = ref([
      {
        text: "Request Type",
        align: "start",
        value: "requestType",
        sortable: false,
        show: true,
      },
      { text: "Processed", value: "isProcessed", sortable: false, show: true },
      { text: "Admin Request", value: "isAdmin", sortable: false, show: true },
      {
        text: "Actions",
        align: "end",
        value: "action",
        sortable: false,
        show: true,
      },
    ]);
    const bnRequests = ref<RequestTracker[]>([]);
    const requestDetails = ref<RequestTracker>(null);
    const resubmitRequestDialog = ref(false);
    const businessIdentifierChange = async () => {
      bnRequests.value = await getBNRequests(businessIdentifier.value);
    };
    const showResubmitRequestDialog = async (
      item: RequestTracker
    ): Promise<void> => {
      requestDetails.value = await getRequestTracker(item.id);
      resubmitRequestDialog.value = true;
    };
    const hideResubmitRequestDialog = async (): Promise<void> => {
      resubmitRequestDialog.value = false;
      requestDetails.value = null;
    };
    const resubmitRequest = async (xmlData): Promise<void> => {
      const queued = await resubmitBNRequest({
        businessIdentifier: businessIdentifier.value,
        requestType: requestDetails.value.requestType,
        request: xmlData,
      });
      if (queued) {
        resubmitRequestDialog.value = false;
        requestDetails.value = null;
        await businessIdentifierChange();
      }
    };
    watch(businessIdentifier, businessIdentifierChange, {
      deep: true,
      immediate: true,
    });
    return {
      headers,
      bnRequests,
      requestDetails,
      resubmitRequestDialog,
      businessIdentifierChange,
      showResubmitRequestDialog,
      hideResubmitRequestDialog,
      resubmitRequest,
    };
  },
});
