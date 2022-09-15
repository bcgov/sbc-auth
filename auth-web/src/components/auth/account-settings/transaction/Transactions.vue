import {
  defineComponent,
  toRefs,
  ref,
  computed,
  onMounted,
} from "@vue/composition-api";
import { Account, Pages, SearchFilterCodes } from "@/util/constants";
import { Component, Mixins, Prop, Vue, Watch } from "vue-property-decorator";
import {
  Member,
  MembershipType,
  OrgPaymentDetails,
  Organization,
} from "@/models/Organization";
import {
  TransactionFilter,
  TransactionFilterParams,
  TransactionTableList,
} from "@/models/transaction";
import { mapActions, mapState } from "vuex";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import CommonUtils from "@/util/common-util";
import SearchFilterInput from "@/components/auth/common/SearchFilterInput.vue";
import { SearchFilterParam } from "@/models/searchfilter";
import TransactionsDataTable from "@/components/auth/account-settings/transaction/TransactionsDataTable.vue";
import moment from "moment";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
export default defineComponent({
  components: {
    TransactionsDataTable,
    SearchFilterInput,
  },
  props: { orgId: { default: "", type: String } },
  setup(props, ctx) {
    const { orgId } = toRefs(props);
    const updateTransactionTableCounter = ref<number>(0);
    const totalTransactionsCount = ref<number>(0);
    const isLoading = ref<boolean>(false);
    const searchFilter = ref<SearchFilterParam[]>([]);
    const transactionFilterProp = ref<TransactionFilter>(
      {} as TransactionFilter
    );
    const isTransactionFetchDone = ref<boolean>(false);
    const credit = ref<any>(0);
    const isTransactionsAllowed = computed((): boolean => {
      return (
        currentOrganization?.orgType === Account.PREMIUM &&
        [MembershipType.Admin, MembershipType.Coordinator].includes(
          currentMembership.membershipTypeCode
        )
      );
    });
    const getPaymentDetails = async () => {
      const { accountId, credit } = currentOrgPaymentDetails;
      if (!accountId || Number(accountId) !== currentOrganization?.id) {
        const paymentDetails: OrgPaymentDetails = await getOrgPayments(
          currentOrganization?.id
        );
        credit.value =
          paymentDetails.credit && paymentDetails.credit !== null
            ? paymentDetails.credit
            : 0;
      } else {
        credit.value = credit && credit !== null ? credit : 0;
      }
    };
    const initializeFilters = () => {
      searchFilter.value = [
        {
          id: SearchFilterCodes.DATERANGE,
          placeholder: "Date Range",
          labelKey: "Date",
          appliedFilterValue: "",
          filterInput: "",
        },
        {
          id: SearchFilterCodes.USERNAME,
          placeholder: "Initiated by",
          labelKey: "Initiated by",
          appliedFilterValue: "",
          filterInput: "",
        },
        {
          id: SearchFilterCodes.FOLIONUMBER,
          placeholder: "Folio Number",
          labelKey: "Folio Number",
          appliedFilterValue: "",
          filterInput: "",
        },
      ];
      isTransactionFetchDone.value = false;
    };
    const setAppliedFilterValue = (filters: SearchFilterParam[]) => {
      filters.forEach((filter) => {
        switch (filter.id) {
          case SearchFilterCodes.DATERANGE:
            transactionFilterProp.value.dateFilter =
              filter.appliedFilterValue || {};
            break;
          case SearchFilterCodes.FOLIONUMBER:
            transactionFilterProp.value.folioNumber = filter.appliedFilterValue;
            break;
          case SearchFilterCodes.USERNAME:
            transactionFilterProp.value.createdBy = filter.appliedFilterValue;
            break;
        }
      });
      isTransactionFetchDone.value = false;
      updateTransactionTableCounter.value++;
    };
    const initFilter = () => {
      if (isTransactionsAllowed.value) {
        initializeFilters();
        getPaymentDetails();
        updateTransactionTableCounter.value++;
      } else {
        ctx.root.$router.push(
          `/${Pages.MAIN}/${currentOrganization.id}/settings/account-info`
        );
      }
    };
    const setTotalTransactionCount = (value) => {
      totalTransactionsCount.value = value;
      isTransactionFetchDone.value = true;
    };
    const exportCSV = async () => {
      isLoading.value = true;
      const filterParams: TransactionFilter = transactionFilterProp.value;
      const downloadData = await getTransactionReport(filterParams);
      CommonUtils.fileDownload(
        downloadData,
        `bcregistry-transactions-${moment().format("MM-DD-YYYY")}.csv`,
        "text/csv"
      );
      isLoading.value = false;
    };
    onMounted(async () => {
      setAccountChangedHandler(initFilter);
      initFilter();
    });
    return {
      updateTransactionTableCounter,
      totalTransactionsCount,
      isLoading,
      searchFilter,
      transactionFilterProp,
      isTransactionFetchDone,
      credit,
      isTransactionsAllowed,
      getPaymentDetails,
      initializeFilters,
      setAppliedFilterValue,
      initFilter,
      setTotalTransactionCount,
      exportCSV,
    };
  },
});
