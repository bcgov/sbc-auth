import { defineComponent, ref, computed } from "@vue/composition-api";
import Component from "vue-class-component";
import ConfigHelper from "@/util/config-helper";
import { DataOptions } from "vuetify";
import { SessionStorageKeys } from "@/util/constants";
import Vue from "vue";
export default defineComponent({
  props: {},
  setup(_props, ctx) {
    const DEFAULT_ITEMS_PER_PAGE = ref(5);
    const PAGINATION_COUNTER_STEP = ref(4);
    const DEFAULT_DATA_OPTIONS = ref<DataOptions>({
      page: 1,
      itemsPerPage: numberOfItems.value,
      sortBy: [],
      sortDesc: [],
      groupBy: [],
      groupDesc: [],
      multiSort: false,
      mustSort: false,
    });
    const numberOfItems = computed(() => {
      return (
        getNumberOfItemsFromSessionStorage() || DEFAULT_ITEMS_PER_PAGE.value
      );
    });
    const hasCachedPageInfo = computed((): boolean => {
      const paginationOptions = JSON.parse(
        ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) ||
          "{}"
      );
      return Object.keys(paginationOptions).length !== 0;
    });
    const getPaginationOptions = computed(() => {
      return [...Array(PAGINATION_COUNTER_STEP.value)].map(
        (value, index) => DEFAULT_ITEMS_PER_PAGE.value * (index + 1)
      );
    });
    const getNumberOfItemsFromSessionStorage = (): number | undefined => {
      let items = +ConfigHelper.getFromSession(
        SessionStorageKeys.PaginationNumberOfItems
      );
      return !isNaN(items) ? items : undefined;
    };
    const saveItemsPerPage = (val) => {
      ConfigHelper.addToSession(
        SessionStorageKeys.PaginationNumberOfItems,
        val
      );
    };
    const cachePageInfo = (tableDataOptions: Partial<DataOptions>) => {
      ConfigHelper.addToSession(
        SessionStorageKeys.PaginationOptions,
        JSON.stringify(tableDataOptions)
      );
    };
    const getAndPruneCachedPageInfo = (): Partial<DataOptions> | undefined => {
      const paginationOptions = JSON.parse(
        ConfigHelper.getFromSession(SessionStorageKeys.PaginationOptions) ||
          "{}"
      );
      if (Object.keys(paginationOptions).length !== 0) {
        ConfigHelper.removeFromSession(SessionStorageKeys.PaginationOptions);
        return paginationOptions;
      } else {
        return undefined;
      }
    };
    return {
      DEFAULT_ITEMS_PER_PAGE,
      PAGINATION_COUNTER_STEP,
      DEFAULT_DATA_OPTIONS,
      numberOfItems,
      hasCachedPageInfo,
      getPaginationOptions,
      getNumberOfItemsFromSessionStorage,
      saveItemsPerPage,
      cachePageInfo,
      getAndPruneCachedPageInfo,
    };
  },
});
