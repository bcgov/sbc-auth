import { defineComponent, ref, watch, onMounted } from "@vue/composition-api";
import { Component, Mixins, Prop, Watch } from "vue-property-decorator";
import { Task, TaskFilterParams, TaskList } from "@/models/Task";
import { TaskRelationshipStatus, TaskStatus } from "@/util/constants";
import CommonUtils from "@/util/common-util";
import { DataOptions } from "vuetify";
import PaginationMixin from "@/components/auth/mixins/PaginationMixin.vue";
import { namespace } from "vuex-class";
const TaskModule = namespace("task");
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const rejectedTasks = ref<Task[]>([]);
    const taskFilter = ref<TaskFilterParams>(undefined);
    const totalRejectedTasks = ref(0);
    const columnSort = ref(CommonUtils.customSort);
    const tableDataOptions = ref<Partial<DataOptions>>({});
    const isTableLoading = ref<boolean>(false);
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
        text: "Rejected By",
        align: "left",
        sortable: false,
        value: "modifiedBy",
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
          relationshipStatus: TaskRelationshipStatus.REJECTED,
          pageNumber: page,
          pageLimit: pageLimit,
          statuses: [TaskStatus.COMPLETED],
        };
        const rejectedTasksResp = await fetchTasks(taskFilter.value);
        rejectedTasks.value = rejectedTasksResp.tasks;
        totalRejectedTasks.value = rejectedTasksResp?.total || 0;
      } catch (error) {
        isTableLoading.value = false;
        console.error(error);
      }
    };
    const view = (item) => {
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
      rejectedTasks,
      taskFilter,
      totalRejectedTasks,
      columnSort,
      tableDataOptions,
      isTableLoading,
      headerAccounts,
      formatDate,
      getStaffTasks,
      getIndexedTag,
      searchStaffTasks,
      view,
    };
  },
});
