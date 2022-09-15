import {
  defineComponent,
  toRefs,
  ref,
  computed,
  watch,
  onMounted,
} from "@vue/composition-api";
import { Account, Pages } from "@/util/constants";
import { ActivityLog, ActivityLogFilterParams } from "@/models/activityLog";
import { Component, Mixins, Prop, Vue, Watch } from "vue-property-decorator";
import { Member, MembershipType, Organization } from "@/models/Organization";
import AccountChangeMixin from "@/components/auth/mixins/AccountChangeMixin.vue";
import CommonUtils from "@/util/common-util";
import { namespace } from "vuex-class";
const ActivityLogModule = namespace("activity");
const OrgModule = namespace("org");
export default defineComponent({
  props: { orgId: { default: "", type: Number } },
  setup(props, ctx) {
    const { orgId } = toRefs(props);
    const ITEMS_PER_PAGE = ref(5);
    const PAGINATION_COUNTER_STEP = ref(4);
    const formatDate = ref(CommonUtils.formatDisplayDate);
    const totalActivityCount = ref<number>(0);
    const tableDataOptions = ref<any>({});
    const isDataLoading = ref<boolean>(false);
    const activityList = ref<ActivityLog[]>([]);
    const isLoading = ref<boolean>(false);
    const activityHeader = ref([
      {
        text: "Date",
        align: "left",
        sortable: false,
        value: "created",
        class: "bold-header",
      },
      {
        text: "Initiated by",
        align: "left",
        sortable: false,
        value: "actor",
        class: "bold-header",
      },
      {
        text: "Subject",
        align: "left",
        sortable: false,
        value: "action",
        class: "bold-header",
      },
    ]);
    const getPaginationOptions = computed(() => {
      return [...Array(PAGINATION_COUNTER_STEP.value)].map(
        (value, index) => ITEMS_PER_PAGE.value * (index + 1)
      );
    });
    const initialize = async () => {
      await loadActivityList();
    };
    const getActivityLogs = async (val) => {
      const pageNumber = val?.page || 1;
      const itemsPerPage = val?.itemsPerPage;
      await loadActivityList(pageNumber, itemsPerPage);
    };
    const loadActivityList = async (
      pageNumber?: number,
      itemsPerPage?: number
    ) => {
      isDataLoading.value = true;
      const filterParams: ActivityLogFilterParams = {
        pageNumber: pageNumber,
        pageLimit: itemsPerPage,
        orgId: currentOrganization.id,
      };
      try {
        const resp: any = await getActivityLog(filterParams);
        activityList.value = resp?.activityLogs || [];
        totalActivityCount.value = resp?.total || 0;
        isDataLoading.value = false;
      } catch {
        activityList.value = [];
        totalActivityCount.value = 0;
        isDataLoading.value = false;
      }
    };
    watch(tableDataOptions, getActivityLogs, { deep: true });
    onMounted(async () => {
      setAccountChangedHandler(initialize);
      initialize();
    });
    return {
      ITEMS_PER_PAGE,
      PAGINATION_COUNTER_STEP,
      formatDate,
      totalActivityCount,
      tableDataOptions,
      isDataLoading,
      activityList,
      isLoading,
      activityHeader,
      getPaginationOptions,
      initialize,
      getActivityLogs,
      loadActivityList,
    };
  },
});
