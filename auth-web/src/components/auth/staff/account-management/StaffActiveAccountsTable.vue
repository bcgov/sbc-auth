import {
  defineComponent,
  ref,
  computed,
  watch,
  onMounted,
} from "@vue/composition-api";
import {
  AccessType,
  Account,
  AccountStatus,
  SessionStorageKeys,
} from "@/util/constants";
import { Component, Mixins, Watch } from "vue-property-decorator";
import {
  Member,
  OrgAccountTypes,
  OrgFilterParams,
  OrgList,
  OrgMap,
  Organization,
} from "@/models/Organization";
import CommonUtils from "@/util/common-util";
import ConfigHelper from "@/util/config-helper";
import { DataOptions } from "vuetify";
import { EnumDictionary } from "@/models/util";
import OrgModule from "@/store/modules/org";
import PaginationMixin from "@/components/auth/mixins/PaginationMixin.vue";
import SearchFilterInput from "@/components/auth/common/SearchFilterInput.vue";
import { UserSettings } from "sbc-common-components/src/models/userSettings";
import debounce from "@/util/debounce";
import { getModule } from "vuex-module-decorators";
import { namespace } from "vuex-class";
const StaffBinding = namespace("staff");
const OrgBinding = namespace("org");
export default defineComponent({
  components: {
    SearchFilterInput,
  },
  props: {},
  setup(_props, ctx) {
    const orgStore = ref(getModule(OrgModule, ctx.root.$store));
    const activeOrgs = ref<Organization[]>([]);
    const headerAccounts = ref([
      {
        text: "Account Name",
        value: "name",
      },
      {
        text: "Branch Name",
        value: "branchName",
      },
      {
        text: "Account Number",
        value: "id",
      },
      {
        text: "Approved By",
        value: "decisionMadeBy",
      },
      {
        value: "orgType",
      },
      {
        text: "Actions",
        value: "action",
      },
    ]);
    const accountTypeMap = ref<EnumDictionary<OrgAccountTypes, OrgMap>>({
      [OrgAccountTypes.ALL]: {},
      [OrgAccountTypes.BASIC]: {
        accessType: [AccessType.REGULAR, AccessType.REGULAR_BCEID],
        orgType: Account.BASIC,
      },
      [OrgAccountTypes.BASIC_OUT_OF_PROVINCE]: {
        accessType: [AccessType.EXTRA_PROVINCIAL],
        orgType: Account.BASIC,
      },
      [OrgAccountTypes.PREMIUM]: {
        accessType: [AccessType.REGULAR, AccessType.REGULAR_BCEID],
        orgType: Account.PREMIUM,
      },
      [OrgAccountTypes.PREMIUM_OUT_OF_PROVINCE]: {
        accessType: [AccessType.EXTRA_PROVINCIAL],
        orgType: Account.PREMIUM,
      },
      [OrgAccountTypes.GOVM]: {
        accessType: [AccessType.GOVM],
      },
      [OrgAccountTypes.GOVN]: {
        accessType: [AccessType.GOVN],
      },
      [OrgAccountTypes.DIRECTOR_SEARCH]: {
        accessType: [AccessType.ANONYMOUS],
      },
    });
    const accountTypes = ref(Array.from(Object.keys(accountTypeMap.value)));
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const totalAccountsCount = ref(0);
    const tableDataOptions = ref<Partial<DataOptions>>({});
    const isTableLoading = ref(false);
    const searchParamsExist = ref(false);
    const dropdown = ref<Array<boolean>>([]);
    const searchParams = ref<OrgFilterParams>({
      name: "",
      branchName: "",
      id: "",
      decisionMadeBy: "",
      orgType: OrgAccountTypes.ALL,
      statuses: [AccountStatus.ACTIVE],
    });
    const debouncedOrgSearch = ref(
      debounce(
        async (
          context: StaffActiveAccountsTable,
          page = 1,
          pageLimit = context.numberOfItems
        ) => {
          try {
            context.isTableLoading = true;
            const completeSearchParams: OrgFilterParams = {
              ...context.searchParams,
              orgType: undefined,
              accessType: undefined,
              ...context.getOrgAndAccessTypeFromAccountType(
                context.searchParams.orgType
              ),
              page: page,
              limit: pageLimit,
            };
            const activeAccountsResp = await context.searchOrgs(
              completeSearchParams
            );
            context.activeOrgs = activeAccountsResp.orgs;
            context.totalAccountsCount = activeAccountsResp?.total || 0;
          } catch (error) {
            console.error(error);
          } finally {
            context.isTableLoading = false;
          }
        }
      )
    );
    const noDataMessage = computed(() => {
      return ctx.root.$t(
        searchParamsExist.value
          ? "searchAccountNoResult"
          : "searchAccountStartMessage"
      );
    });
    const searchChanged = (value: OrgFilterParams) => {
      searchParamsExist.value = doSearchParametersExist(value);
      tableDataOptions.value = { ...getAndPruneCachedPageInfo(), page: 1 };
      setSearchFilterToStorage(JSON.stringify(value));
      debouncedOrgSearch.value(this);
    };
    const tableDataOptionsChange = async (val) => {
      debouncedOrgSearch.value(this, val?.page, val?.itemsPerPage);
    };
    const viewInBusinessRegistryDashboard = async (org: Organization) => {
      await syncBeforeNavigate(org);
      ctx.root.$router.push(`/account/business/business?accountid=${org.id}`);
    };
    const view = async (org: Organization) => {
      await syncBeforeNavigate(org);
      ctx.root.$router.push(`/account/${org.id}/settings`);
    };
    const clearSearchParams = () => {
      searchParams.value = {
        name: "",
        branchName: "",
        id: "",
        decisionMadeBy: "",
        orgType: OrgAccountTypes.ALL,
        accessType: [],
        statuses: [AccountStatus.ACTIVE],
      };
    };
    const syncBeforeNavigate = async (org: Organization) => {
      cachePageInfo(tableDataOptions.value);
      await syncOrganization(org.id);
      await addOrgSettings(org);
      await syncMembership(org.id);
    };
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const getOrgAndAccessTypeFromAccountType = (
      accountType: string
    ): object => {
      return accountTypeMap.value[accountType];
    };
    const getAccountTypeFromOrgAndAccessType = (org: Organization): any => {
      const entries = Object.entries(accountTypeMap.value);
      const byAccessTypeAndOrgType = entries.find(
        ([key, value]) =>
          value?.accessType?.includes(org.accessType) &&
          value?.orgType === org.orgType
      );
      if (byAccessTypeAndOrgType) {
        return byAccessTypeAndOrgType[0];
      }
      const byAccessType = entries.find(([key, value]) =>
        value?.accessType?.includes(org.accessType)
      );
      if (byAccessType) {
        return byAccessType[0];
      }
      const byOrgType = entries.find(
        ([key, value]) => value?.orgType === org.orgType
      );
      if (byOrgType) {
        return byOrgType[0];
      }
      return "";
    };
    const setSearchFilterToStorage = (val: string): void => {
      ConfigHelper.addToSession(SessionStorageKeys.OrgSearchFilter, val);
    };
    const doSearchParametersExist = (searchParams: OrgFilterParams) => {
      return (
        searchParams.name.length > 0 ||
        searchParams.branchName.length > 0 ||
        searchParams.id.length > 0 ||
        searchParams.decisionMadeBy.length > 0 ||
        (searchParams.orgType.length > 0 &&
          searchParams.orgType !== OrgAccountTypes.ALL)
      );
    };
    watch(searchParams, searchChanged, { deep: true });
    watch(tableDataOptions, tableDataOptionsChange, { deep: true });
    onMounted(() => {
      tableDataOptions.value = DEFAULT_DATA_OPTIONS;
      const orgSearchFilter =
        ConfigHelper.getFromSession(SessionStorageKeys.OrgSearchFilter) || "";
      try {
        searchParams.value = JSON.parse(orgSearchFilter);
      } catch {}
      if (hasCachedPageInfo) {
        tableDataOptions.value = getAndPruneCachedPageInfo();
      }
    });
    return {
      orgStore,
      activeOrgs,
      headerAccounts,
      accountTypeMap,
      accountTypes,
      formatDate,
      totalAccountsCount,
      tableDataOptions,
      isTableLoading,
      searchParamsExist,
      dropdown,
      searchParams,
      debouncedOrgSearch,
      noDataMessage,
      searchChanged,
      tableDataOptionsChange,
      viewInBusinessRegistryDashboard,
      view,
      clearSearchParams,
      syncBeforeNavigate,
      getIndexedTag,
      getOrgAndAccessTypeFromAccountType,
      getAccountTypeFromOrgAndAccessType,
      setSearchFilterToStorage,
      doSearchParametersExist,
    };
  },
});
