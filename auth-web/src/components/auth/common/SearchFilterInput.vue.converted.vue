import {
  defineComponent,
  toRefs,
  computed,
  PropType,
} from "@vue/composition-api";
import { Component, Emit, Prop } from "vue-property-decorator";
import CommonUtils from "@/util/common-util";
import DateRangeFilter from "@/components/auth/common/DateRangeFilter.vue";
import { SearchFilterCodes } from "@/util/constants";
import { SearchFilterParam } from "@/models/searchfilter";
import Vue from "vue";
export default defineComponent({
  components: {
    DateRangeFilter,
  },
  props: {
    filteredRecordsCount: { default: 0, type: Number },
    filterParams: {
      default: [] as SearchFilterParam[],
      type: Array as Proptype<SearchFilterParam[]>,
    },
    isDataFetchCompleted: { default: true, type: Boolean },
  },
  setup(props, ctx) {
    const { filteredRecordsCount, filterParams, isDataFetchCompleted } =
      toRefs(props);
    const isApplyFilterEnabled = computed(() => {
      return filterParams.value.some((filter) => !!filter.filterInput);
    });
    const showFilteredChips = computed(() => {
      return filterParams.value.some((filter) => !!filter.appliedFilterValue);
    });
    const colCount = computed(() => {
      return filterParams.value.length * 2 + 4;
    });
    const applyFilter = () => {
      filterParams.value.forEach((filter) => {
        if (filter.filterInput) {
          filter.appliedFilterValue = filter.filterInput;
        }
        filter.filterInput = "";
      });
      filterTexts();
    };
    const filterTexts = () => {
      return filterParams.value;
    };
    const clearAppliedFilter = (filter) => {
      filter.appliedFilterValue = "";
      filterTexts();
    };
    const clearAllFilters = () => {
      filterParams.value.forEach((filter) => {
        filter.appliedFilterValue = "";
      });
      filterTexts();
    };
    const applyDateFilter = (dateRangeObj, filter) => {
      filter.appliedFilterValue = dateRangeObj;
      filterTexts();
    };
    const isDateRange = (filter) => {
      return filter.id === SearchFilterCodes.DATERANGE;
    };
    const getDateFilterLabel = (appliedFilterValue) => {
      return appliedFilterValue?.startDate === appliedFilterValue?.endDate
        ? CommonUtils.formatDisplayDate(appliedFilterValue?.startDate)
        : `${CommonUtils.formatDisplayDate(
            appliedFilterValue?.startDate
          )} - ${CommonUtils.formatDisplayDate(appliedFilterValue?.endDate)}`;
    };
    return {
      isApplyFilterEnabled,
      showFilteredChips,
      colCount,
      applyFilter,
      filterTexts,
      clearAppliedFilter,
      clearAllFilters,
      applyDateFilter,
      isDateRange,
      getDateFilterLabel,
    };
  },
});
