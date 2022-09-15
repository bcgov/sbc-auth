import { defineComponent, ref, watch, onMounted } from "@vue/composition-api";
import { Component, Mixins, Watch } from "vue-property-decorator";
import { Task, TaskFilterParams, TaskList } from "@/models/Task";
import {
  TaskRelationshipStatus,
  TaskRelationshipType,
  TaskStatus,
} from "@/util/constants";
import CommonUtils from "@/util/common-util";
import { DataOptions } from "vuetify";
import PaginationMixin from "@/components/auth/mixins/PaginationMixin.vue";
import { namespace } from "vuex-class";
const TaskModule = namespace("task");
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const staffTasks = ref<Task[]>([]);
    const taskFilter = ref<TaskFilterParams>(undefined);
    const totalStaffTasks = ref(0);
    const columnSort = ref(CommonUtils.customSort);
    const tableDataOptions = ref<Partial<DataOptions>>({});
    const isTableLoading = ref<boolean>(false);
    const TaskRelationshipTypeEnum = ref(TaskRelationshipType);
    const headerAccounts = ref([
      {
        text: "Date Submittted",
        align: "left",
        sortable: false,
        value: "dateSubmitted",
        width: "150",
      },
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
        value: "type",
      },
      {
        text: "Status",
        align: "left",
        sortable: false,
        value: "status",
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
    const getStaffTasks = async (val, oldVal) => {
      await searchStaffTasks(val?.page, val?.itemsPerPage);
    };
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const searchStaffTasks = async (
      page: number = 1,
      pageLimit: number = numberOfItems
    ) => {
      try {
        taskFilter.value = {
          relationshipStatus: TaskRelationshipStatus.PENDING_STAFF_REVIEW,
          pageNumber: page,
          pageLimit: pageLimit,
          statuses: [TaskStatus.OPEN, TaskStatus.HOLD],
        };
        const staffTasksResp = await fetchTasks(taskFilter.value);
        staffTasks.value = staffTasksResp.tasks;
        totalStaffTasks.value = staffTasksResp?.total || 0;
      } catch (error) {
        isTableLoading.value = false;
        console.error(error);
      }
    };
    const review = (item) => {
      cachePageInfo(tableDataOptions.value);
      ctx.root.$router.push(`/review-account/${item.id}`);
    };
    watch(tableDataOptions, getStaffTasks, { deep: true });
    onMounted(() => {
      tableDataOptions.value = DEFAULT_DATA_OPTIONS;
      if (hasCachedPageInfo) {
        tableDataOptions.value = getAndPruneCachedPageInfo();
      }
    });
    return {
      staffTasks,
      taskFilter,
      totalStaffTasks,
      columnSort,
      tableDataOptions,
      isTableLoading,
      TaskRelationshipTypeEnum,
      headerAccounts,
      formatDate,
      getStaffTasks,
      getIndexedTag,
      searchStaffTasks,
      review,
    };
  },
});
