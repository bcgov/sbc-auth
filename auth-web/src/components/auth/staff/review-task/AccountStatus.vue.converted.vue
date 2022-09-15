import {
  defineComponent,
  toRefs,
  ref,
  computed,
  PropType,
} from "@vue/composition-api";
import { Component, Prop, Vue } from "vue-property-decorator";
import { TaskRelationshipStatus, TaskStatus } from "@/util/constants";
import CommonUtils from "@/util/common-util";
import { Task } from "@/models/Task";
import moment from "moment";
export default defineComponent({
  props: {
    tabNumber: { default: null, type: Number },
    isPendingReviewPage: { default: false, type: Boolean },
    title: { default: "Account Status", type: String },
    taskDetails: { default: {}, type: Object as PropType<Task> },
  },
  setup(props, ctx) {
    const { tabNumber, isPendingReviewPage, title, taskDetails } =
      toRefs(props);
    const TaskRelationshipStatusEnum = ref(TaskRelationshipStatus);
    const formatNumberToTwoPlaces = ref(CommonUtils.formatNumberToTwoPlaces);
    const statusLabel = computed((): string => {
      switch (taskDetails.value.relationshipStatus) {
        case TaskRelationshipStatus.ACTIVE:
          return "Approved";
        case TaskRelationshipStatus.REJECTED:
          return "Rejected";
        case TaskRelationshipStatus.PENDING_STAFF_REVIEW:
          return isAccountOnHold.value ? "On Hold" : "Pending";
        default:
          return "";
      }
    });
    const isAccountOnHold = computed((): boolean => {
      return taskDetails.value.status === TaskStatus.HOLD;
    });
    const accountOnHoldRemarks = computed((): string => {
      return taskDetails.value?.remarks;
    });
    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`;
    };
    const formatDate = (date: Date): string => {
      return moment(date).format("MMM DD, YYYY");
    };
    return {
      TaskRelationshipStatusEnum,
      formatNumberToTwoPlaces,
      statusLabel,
      isAccountOnHold,
      accountOnHoldRemarks,
      getIndexedTag,
      formatDate,
    };
  },
});
