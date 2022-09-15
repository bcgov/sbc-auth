import { defineComponent, ref, watch, onMounted } from "@vue/composition-api";
import {
  AccessType,
  Account,
  AccountStatus,
  SessionStorageKeys,
} from "@/util/constants";
import { Component, Mixins, Watch } from "vue-property-decorator";
import {
  Member,
  OrgFilterParams,
  OrgList,
  Organization,
} from "@/models/Organization";
import { Code } from "@/models/Code";
import CommonUtils from "@/util/common-util";
import ConfigHelper from "@/util/config-helper";
import { DataOptions } from "vuetify";
import PaginationMixin from "@/components/auth/mixins/PaginationMixin.vue";
import { UserSettings } from "sbc-common-components/src/models/userSettings";
import { namespace } from "vuex-class";
const OrgModule = namespace("org");
const StaffModule = namespace("staff");
const CodesModule = namespace("codes");
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const headerAccounts = ref([
      {
        text: "Name",
        align: "left",
        sortable: false,
        value: "name",
      },
      {
        text: "Type",
        align: "left",
        sortable: false,
        value: "orgType",
      },
      {
        text: "Suspended by",
        align: "left",
        sortable: false,
        value: "decisionMadeBy",
      },
      {
        text: "Date Suspended",
        align: "left",
        sortable: false,
        value: "suspendedOn",
      },
      {
        text: "Reason",
        align: "left",
        sortable: false,
        value: "statusCode",
      },
      {
        text: "Actions",
        align: "left",
        value: "action",
        sortable: false,
        width: "105",
      },
    ]);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const totalAccountsCount = ref(0);
    const tableDataOptions = ref<Partial<DataOptions>>({});
    const orgFilter = ref<OrgFilterParams>(undefined);
    const isTableLoading = ref<boolean>(false);
    const suspendedOrgs = ref<Organization[]>([]);
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const getAccounts = async (val, oldVal) => {
      await getOrgs(val?.page, val?.itemsPerPage);
    };
    const getOrgs = async (
      page: number = 1,
      pageLimit: number = numberOfItems
    ) => {
      const appliedFilterValue =
        ConfigHelper.getFromSession(SessionStorageKeys.OrgSearchFilter) || "";
      try {
        orgFilter.value = {
          statuses: [AccountStatus.NSF_SUSPENDED, AccountStatus.SUSPENDED],
          page: page,
          limit: pageLimit,
        };
        const activeAccountsResp: any = await searchOrgs(orgFilter.value);
        suspendedOrgs.value = activeAccountsResp?.orgs;
        totalAccountsCount.value = activeAccountsResp?.total || 0;
      } catch (error) {
        isTableLoading.value = false;
        console.error(error);
      }
    };
    const view = async (org: Organization) => {
      cachePageInfo(tableDataOptions.value);
      let orgId: number = org.id;
      await syncOrganization(orgId);
      await addOrgSettings(org);
      await syncMembership(orgId);
      ctx.root.$router.push(`/account/${orgId}/settings`);
    };
    const formatType = (org: Organization): string => {
      let orgTypeDisplay = org.orgType === Account.BASIC ? "Basic" : "Premium";
      if (org.accessType === AccessType.ANONYMOUS) {
        return "Director Search";
      }
      if (org.accessType === AccessType.EXTRA_PROVINCIAL) {
        return orgTypeDisplay + " (out-of-province)";
      }
      return orgTypeDisplay;
    };
    const getStatusText = (org: Organization) => {
      if (org.statusCode === AccountStatus.NSF_SUSPENDED) {
        return "NSF";
      } else if (org.statusCode === AccountStatus.SUSPENDED) {
        return getSuspensionReasonCode(org);
      } else {
        return org.statusCode;
      }
    };
    const getSuspensionReasonCode = (org: Organization): string => {
      return suspensionReasonCodes?.find(
        (suspensionReasonCode) =>
          suspensionReasonCode?.code === org?.suspensionReasonCode
      )?.desc;
    };
    watch(tableDataOptions, getAccounts, { deep: true });
    onMounted(async () => {
      tableDataOptions.value = DEFAULT_DATA_OPTIONS;
      if (hasCachedPageInfo) {
        tableDataOptions.value = getAndPruneCachedPageInfo();
      }
      suspendedOrgs.value = suspendedStaffOrgs;
      totalAccountsCount.value = suspendedReviewCount;
    });
    return {
      headerAccounts,
      formatDate,
      totalAccountsCount,
      tableDataOptions,
      orgFilter,
      isTableLoading,
      suspendedOrgs,
      getIndexedTag,
      getAccounts,
      getOrgs,
      view,
      formatType,
      getStatusText,
      getSuspensionReasonCode,
    };
  },
});
