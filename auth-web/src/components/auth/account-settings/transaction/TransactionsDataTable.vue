import {
  defineComponent,
  computed,
  toRefs,
  ref,
  watch,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop, Vue, Watch } from "vue-property-decorator";
import {
  TransactionFilter,
  TransactionFilterParams,
  TransactionTableList,
  TransactionTableRow,
} from "@/models/transaction";
import { mapActions, mapState } from "vuex";
import CommonUtils from "@/util/common-util";
import { Organization } from "@/models/Organization";
import { TransactionStatus } from "@/util/constants";
export default defineComponent({
  props: {
    transactionFilters: {
      default: () => ({} as TransactionFilter),
      type: Object as PropType<TransactionFilter>,
    },
  },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const getTransactionList = () =>
      ctx.root.$store.dispatch("org/getTransactionList");
    const { transactionFilters } = toRefs(props);
    const currentOrganization = ref<Organization>(undefined);
    const getTransactionList =
      ref<(filterParams: TransactionFilterParams) => TransactionTableList>(
        undefined
      );
    const ITEMS_PER_PAGE = ref(5);
    const PAGINATION_COUNTER_STEP = ref(4);
    const transactionList = ref<TransactionTableRow[]>([]);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const totalTransactionsCount = ref(0);
    const isDataLoading = ref(false);
    const tableDataOptions = ref<any>({});
    const headerTranscations = ref([
      {
        text: "Transaction",
        align: "left",
        sortable: false,
        value: "transactionNames",
      },
      {
        text: "Folio Number",
        align: "left",
        sortable: false,
        value: "folioNumber",
      },
      {
        text: "Initiated by",
        align: "left",
        sortable: false,
        value: "initiatedBy",
        width: "170",
      },
      {
        text: "Date (Pacific Time)",
        align: "left",
        value: "transactionDate",
        sortable: false,
        width: "110",
      },
      {
        text: "Total Amount",
        align: "right",
        value: "totalAmount",
        sortable: false,
      },
      {
        text: "Status",
        align: "left",
        value: "status",
        sortable: false,
        width: "110",
      },
    ]);
    const transactionStatus = ref([
      {
        status: TransactionStatus.COMPLETED.toUpperCase(),
        description: "Funds received",
      },
      {
        status: TransactionStatus.PENDING.toUpperCase(),
        description: "Transaction is pending",
      },
      {
        status: TransactionStatus.CANCELLED.toUpperCase(),
        description: "Transaction is cancelled",
      },
    ]);
    const getPaginationOptions = computed(() => {
      return [...Array(PAGINATION_COUNTER_STEP.value)].map(
        (value, index) => ITEMS_PER_PAGE.value * (index + 1)
      );
    });
    const loadTransactionList = async (
      pageNumber?: number,
      itemsPerPage?: number
    ) => {
      isDataLoading.value = true;
      const filterParams: TransactionFilterParams = {
        filterPayload: transactionFilters.value,
        pageNumber: pageNumber,
        pageLimit: itemsPerPage,
      };
      const resp = await getTransactionList.value(filterParams);
      transactionList.value = resp?.transactionsList || [];
      totalTransactionsCount.value = resp?.total || 0;
      emitTotalCount();
      isDataLoading.value = false;
    };
    const getTransactions = async (val, oldVal) => {
      const pageNumber = val.page || 1;
      const itemsPerPage = val.itemsPerPage;
      await loadTransactionList(pageNumber, itemsPerPage);
    };
    const emitTotalCount = () => {
      return totalTransactionsCount.value;
    };
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const getStatusClass = (item) => {
      switch (item.status) {
        case TransactionStatus.COMPLETED:
          return "status-paid";
        case TransactionStatus.PENDING:
          return "status-pending";
        case TransactionStatus.CANCELLED:
          return "status-deleted";
        default:
          return "";
      }
    };
    const customSortActive = (items, index, isDescending) => {
      const isDesc = isDescending.length > 0 && isDescending[0];
      items.sort((a, b) => {
        return isDesc
          ? a[index[0]] < b[index[0]]
            ? -1
            : 1
          : b[index[0]] < a[index[0]]
          ? -1
          : 1;
      });
      return items;
    };
    const formatInitiatedBy = (name) => {
      return name === "None None" ? "-" : name;
    };
    const formatStatus = (status) => {
      const statusMapToPending = [
        "Settlement Scheduled",
        "PAD Invoice Approved",
      ];
      return statusMapToPending.includes(status) ? "Pending" : status;
    };
    const getStatusColor = (status) => {
      switch (status?.toUpperCase()) {
        case TransactionStatus.COMPLETED.toUpperCase():
          return "success";
        case TransactionStatus.CANCELLED.toUpperCase():
          return "error";
        default:
          return "";
      }
    };
    watch(tableDataOptions, getTransactions, { deep: true });
    return {
      currentOrganization,
      getTransactionList,
      currentOrganization,
      getTransactionList,
      ITEMS_PER_PAGE,
      PAGINATION_COUNTER_STEP,
      transactionList,
      formatDate,
      totalTransactionsCount,
      isDataLoading,
      tableDataOptions,
      headerTranscations,
      transactionStatus,
      getPaginationOptions,
      loadTransactionList,
      getTransactions,
      emitTotalCount,
      getIndexedTag,
      getStatusClass,
      customSortActive,
      formatInitiatedBy,
      formatStatus,
      getStatusColor,
    };
  },
});
