import {
  defineComponent,
  computed,
  toRefs,
  ref,
  watch,
  onMounted,
} from "@vue/composition-api";
import { Account, Pages } from "@/util/constants";
import { Component, Mixins, Prop, Vue, Watch } from "vue-property-decorator";
import { Member, MembershipType, Organization } from "@/models/Organization";
import {
  StatementFilterParams,
  StatementListItem,
  StatementListResponse,
} from "@/models/statement";
import { mapActions, mapState } from "vuex";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import CommonUtils from "@/util/common-util";
import StatementsSettings from "@/components/auth/account-settings/statement/StatementsSettings.vue";
import moment from "moment";
export default defineComponent({
  components: {
    StatementsSettings,
  },
  props: { orgId: { default: "", type: String } },
  setup(props, ctx) {
    const currentOrganization = computed(
      () => ctx.root.$store.state.org.currentOrganization
    );
    const currentMembership = computed(
      () => ctx.root.$store.state.org.currentMembership
    );
    const getStatementsList = () =>
      ctx.root.$store.dispatch("org/getStatementsList");
    const getStatement = () => ctx.root.$store.dispatch("org/getStatement");
    const { orgId } = toRefs(props);
    const currentMembership = ref<Member>(undefined);
    const currentOrganization = ref<Organization>(undefined);
    const getStatementsList =
      ref<(filterParams: StatementFilterParams) => StatementListResponse>(
        undefined
      );
    const getStatement = ref<(statementParams: any) => any>(undefined);
    const ITEMS_PER_PAGE = ref(5);
    const PAGINATION_COUNTER_STEP = ref(4);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const totalStatementsCount = ref<number>(0);
    const tableDataOptions = ref<any>({});
    const isDataLoading = ref<boolean>(false);
    const statementsList = ref<StatementListItem[]>([]);
    const isLoading = ref<boolean>(false);
    const $refs = ref<{
      statementSettingsModal: StatementsSettings;
    }>(undefined);
    const headerStatements = ref([
      {
        text: "Date",
        align: "left",
        sortable: false,
        value: "dateRange",
      },
      {
        text: "Frequency",
        align: "left",
        sortable: false,
        value: "frequency",
      },
      {
        text: "Downloads",
        align: "right",
        sortable: false,
        value: "action",
      },
    ]);
    const getPaginationOptions = computed(() => {
      return [...Array(PAGINATION_COUNTER_STEP.value)].map(
        (value, index) => ITEMS_PER_PAGE.value * (index + 1)
      );
    });
    const isStatementsAllowed = computed((): boolean => {
      return (
        currentOrganization.value?.orgType === Account.PREMIUM &&
        [MembershipType.Admin, MembershipType.Coordinator].includes(
          currentMembership.value.membershipTypeCode
        )
      );
    });
    const initialize = async () => {
      if (!isStatementsAllowed.value) {
        ctx.root.$router.push(
          `/${Pages.MAIN}/${currentOrganization.value.id}/settings/account-info`
        );
      } else {
        await loadStatementsList();
      }
    };
    const formatDateRange = (date1, date2) => {
      let displayDate = "";
      let dateObj1 = getMomentDateObj(date1);
      let dateObj2 = getMomentDateObj(date2);
      let year = dateObj1.year() === dateObj2.year() ? dateObj1.year() : "";
      let month =
        dateObj1.month() === dateObj2.month() ? dateObj1.format("MMMM") : "";
      if (date1 === date2) {
        return dateObj1.format("MMMM DD, YYYY");
      } else if (year && !month) {
        return `${dateObj1.format("MMMM DD")} - ${dateObj2.format(
          "MMMM DD"
        )}, ${year}`;
      } else if (year && month) {
        return `${month} ${dateObj1.date()} - ${dateObj2.date()}, ${year}`;
      } else {
        return `${dateObj1.format("MMMM DD, YYYY")} - ${dateObj2.format(
          "MMMM DD, YYYY"
        )}`;
      }
    };
    const getMomentDateObj = (dateStr) => {
      return moment(dateStr, "YYYY-MM-DD");
    };
    const getTransactions = async (val, oldVal) => {
      const pageNumber = val.page || 1;
      const itemsPerPage = val.itemsPerPage;
      await loadStatementsList(pageNumber, itemsPerPage);
    };
    const loadStatementsList = async (
      pageNumber?: number,
      itemsPerPage?: number
    ) => {
      isDataLoading.value = true;
      const filterParams: StatementFilterParams = {
        pageNumber: pageNumber,
        pageLimit: itemsPerPage,
      };
      const resp = await getStatementsList.value(filterParams);
      statementsList.value = resp?.items || [];
      totalStatementsCount.value = resp?.total || 0;
      isDataLoading.value = false;
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
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const downloadStatement = async (item, type) => {
      isLoading.value = true;
      try {
        const downloadType = type === "CSV" ? "text/csv" : "application/pdf";
        const response = await getStatement.value({
          statementId: item.id,
          type: downloadType,
        });
        const contentDispArr =
          response?.headers["content-disposition"].split("=");
        const fileName =
          contentDispArr.length && contentDispArr[1]
            ? contentDispArr[1]
            : `bcregistry-statement-${type.toLowerCase()}`;
        CommonUtils.fileDownload(response.data, fileName, downloadType);
        isLoading.value = false;
      } catch (error) {
        isLoading.value = false;
      }
    };
    const openSettingsModal = () => {
      ctx.refs.statementSettingsModal.openSettings();
    };
    watch(tableDataOptions, getTransactions, { deep: true });
    onMounted(async () => {
      setAccountChangedHandler(initialize);
      initialize();
    });
    return {
      currentOrganization,
      currentMembership,
      getStatementsList,
      getStatement,
      currentMembership,
      currentOrganization,
      getStatementsList,
      getStatement,
      ITEMS_PER_PAGE,
      PAGINATION_COUNTER_STEP,
      formatDate,
      totalStatementsCount,
      tableDataOptions,
      isDataLoading,
      statementsList,
      isLoading,
      $refs,
      headerStatements,
      getPaginationOptions,
      isStatementsAllowed,
      initialize,
      formatDateRange,
      getMomentDateObj,
      getTransactions,
      loadStatementsList,
      customSortActive,
      getIndexedTag,
      downloadStatement,
      openSettingsModal,
    };
  },
});
