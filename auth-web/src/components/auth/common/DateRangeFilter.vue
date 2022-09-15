import {
  defineComponent,
  toRefs,
  ref,
  computed,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop } from "vue-property-decorator";
import CommonUtils from "@/util/common-util";
import { DateFilterCodes } from "@/util/constants";
import Vue from "vue";
import moment from "moment";
export const DATEFILTER_CODES = DateFilterCodes;
export default defineComponent({
  props: {
    dateFilterProp: { default: () => {}, type: Object as PropType<any> },
  },
  setup(props, ctx) {
    const { dateFilterProp } = toRefs(props);
    const dateRangeSelected = ref<any>([]);
    const dateFilterRanges = ref([
      {
        label: "Today",
        code: DATEFILTER_CODES.TODAY,
      },
      {
        label: "Yesterday",
        code: DATEFILTER_CODES.YESTERDAY,
      },
      {
        label: "Last Week",
        code: DATEFILTER_CODES.LASTWEEK,
      },
      {
        label: "Last Month",
        code: DATEFILTER_CODES.LASTMONTH,
      },
      {
        label: "Custom Range",
        code: DATEFILTER_CODES.CUSTOMRANGE,
      },
    ]);
    const dateFilterSelectedIndex = ref<number>(null);
    const dateFilterSelected = ref<any>({});
    const showDateFilter = ref<boolean>(false);
    const pickerDate = ref<string>("");
    const isApplyFilterBtnValid = computed(() => {
      if (
        dateRangeSelected.value?.length === 2 &&
        dateRangeSelected.value[0] > dateRangeSelected.value[1]
      ) {
        dateRangeSelected.value = [
          dateRangeSelected.value[1],
          dateRangeSelected.value[0],
        ];
      }
      return (
        dateRangeSelected.value[0] &&
        dateRangeSelected.value[1] &&
        dateRangeSelected.value[0] <= dateRangeSelected.value[1]
      );
    });
    const showDateRangeSelected = computed(() => {
      let dateText = "";
      if (
        dateFilterSelected.value?.code === DATEFILTER_CODES.TODAY ||
        dateFilterSelected.value?.code === DATEFILTER_CODES.YESTERDAY
      ) {
        dateText = `<strong>${
          dateFilterSelected.value?.label
        }:</strong> ${CommonUtils.formatDisplayDate(
          dateRangeSelected.value[0],
          "MM-DD-YYYY"
        )}`;
      } else {
        dateText = `<strong>${dateFilterSelected.value?.label}:</strong> 
      ${CommonUtils.formatDisplayDate(
        dateRangeSelected.value[0],
        "MM-DD-YYYY"
      )} 
        - ${CommonUtils.formatDisplayDate(
          dateRangeSelected.value[1],
          "MM-DD-YYYY"
        )}`;
      }
      return dateFilterSelected.value?.code
        ? dateText
        : "<strong>No dates selected</strong>";
    });
    const openDateFilter = () => {
      initDatePicker();
      showDateFilter.value = true;
    };
    const initDatePicker = () => {
      if (!dateFilterProp.value) {
        dateFilterSelectedIndex.value = null;
        dateRangeSelected.value = [];
      }
      dateFilterSelected.value = dateFilterSelectedIndex.value
        ? dateFilterRanges.value[dateFilterSelectedIndex.value]
        : {};
    };
    const formatDatePickerDate = (dateObj) => {
      return dateObj.format("YYYY-MM-DD");
    };
    const formatDateFilter = (dateStr) => {
      if (!dateStr) return null;
      const [year, month, day] = dateStr.split("-");
      return `${year}-${month}-${day}`;
    };
    const dateFilterChange = (val) => {
      if (val > -1) {
        dateFilterSelected.value = dateFilterRanges.value[val];
        switch (dateFilterSelected.value?.code) {
          case DATEFILTER_CODES.TODAY:
            const today = formatDatePickerDate(moment());
            dateRangeSelected.value = [today, today];
            pickerDate.value = today.slice(0, -3);
            break;
          case DATEFILTER_CODES.YESTERDAY:
            const yesterday = formatDatePickerDate(
              moment().subtract(1, "days")
            );
            dateRangeSelected.value = [yesterday, yesterday];
            pickerDate.value = yesterday.slice(0, -3);
            break;
          case DATEFILTER_CODES.LASTWEEK:
            const weekStart = formatDatePickerDate(
              moment().subtract(1, "weeks").startOf("isoWeek")
            );
            const weekEnd = formatDatePickerDate(
              moment().subtract(1, "weeks").endOf("isoWeek")
            );
            dateRangeSelected.value = [weekStart, weekEnd];
            pickerDate.value = weekStart.slice(0, -3);
            break;
          case DATEFILTER_CODES.LASTMONTH:
            const monthStart = formatDatePickerDate(
              moment().subtract(1, "months").startOf("month")
            );
            const monthEnd = formatDatePickerDate(
              moment().subtract(1, "months").endOf("month")
            );
            dateRangeSelected.value = [monthStart, monthEnd];
            pickerDate.value = monthStart.slice(0, -3);
            break;
          case DATEFILTER_CODES.CUSTOMRANGE:
            pickerDate.value = "";
        }
      }
    };
    const dateClick = (date) => {
      pickerDate.value = "";
      dateFilterSelectedIndex.value = 4;
      dateFilterSelected.value =
        dateFilterRanges.value[dateFilterSelectedIndex.value];
    };
    const applyDateFilter = () => {
      emitDateFilter();
      showDateFilter.value = false;
    };
    const emitDateFilter = () => {
      return {
        startDate: formatDateFilter(dateRangeSelected.value[0]),
        endDate: formatDateFilter(dateRangeSelected.value[1]),
      };
    };
    return {
      dateRangeSelected,
      dateFilterRanges,
      dateFilterSelectedIndex,
      dateFilterSelected,
      showDateFilter,
      pickerDate,
      isApplyFilterBtnValid,
      showDateRangeSelected,
      openDateFilter,
      initDatePicker,
      formatDatePickerDate,
      formatDateFilter,
      dateFilterChange,
      dateClick,
      applyDateFilter,
      emitDateFilter,
    };
  },
});
