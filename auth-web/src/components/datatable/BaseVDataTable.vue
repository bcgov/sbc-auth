<template>
  <v-data-table
    id="virtual-scroll-table"
    class="base-table"
    :disable-sort="true"
    :fixed-header="height ? true : false"
    :footer-props="{ itemsPerPageOptions: [5, 10, 15, 20] }"
    :items-per-page="5"
    :headers="headers"
    :items="sortedItemsLimited"
    hide-default-header
    :height="height ? height : ''"
    :loading="filtering || loading"
    :mobile-breakpoint="0"
    :options.sync="tableDataOptions"
    :server-items-length="totalItems"
    :hide-default-footer="pageHide ? true : false"
    ref="regTable"
    v-on:@scroll="onScroll"
  >
    <!-- Headers (two rows) -->
    <template v-slot:header>
      <thead class="base-table__header">
        <!-- First row has titles. -->
        <slot name="header-title-slot" :headers="headers">
          <tr :style="{ 'background-color': headerBg }">
            <th
              v-for="header, i in headers"
              :key="header.col + i"
              :class="[header.class, 'base-table__header__title']"
              :style="header.minWidth ? { 'min-width': header.minWidth, 'max-width': header.minWidth } : ''"
            >
              <slot :name="'header-title-slot-' + header.col" :header="header">
                <span v-html="header.value" />
              </slot>
            </th>
          </tr>
        </slot>
        <!-- Second row has filters. -->
        <slot name="header-filter-slot" :headers="headers">
          <tr :style="{ 'background-color': headerBg }">
            <th
              v-for="header in headers"
              :key="header.col"
              :class="[header.class, 'base-table__header__filter pb-5']"
            >
            <slot :name="'header-filter-slot-' + header.col" :header="header"></slot>
            <header-filter
              :filtering="filtering"
              :filters="filters"
              :header="header"
              :setFiltering="setFiltering"
              :sortedItems="setItems"
              :updateFilter="updateFilter"
              :headers="headers"
              :setSortedItems="setSortedItems"
            ></header-filter>
            </th>
          </tr>
        </slot>
      </thead>
    </template>

    <!-- Items -->
    <template v-slot:item="{ item, index }">
      <tr class="base-table__item-row" :key="item[itemKey]">
        <td
          v-for="header in headers" :key="'item-' + header.col"
          :class="[header.itemClass, 'base-table__item-cell']"
        >
          <slot :header="header" :item="item" :index="index" :name="'item-slot-' + header.col">
            <span v-if="header.itemFn" v-html="header.itemFn(item)" />
            <span v-else>{{ item[header.col] }}</span>
          </slot>
        </td>
      </tr>
    </template>
    <template v-if="start > 0" v-slot:[`body.prepend`]>
      <tr><td :colspan="headers.length" :style="'padding-top:'+startHeight+'px'"></td></tr>
    </template>
    <template v-if="start + perPage < sortedItems.length" v-slot:[`body.append`]>
      <tr><td :colspan="headers.length" :style="'padding-top:'+endHeight+'px'"></td></tr>
    </template>

    <!-- Loading -->
    <template v-slot:loading>
      <div class="py-8 base-table__text" v-html="loadingText" />
    </template>

    <!-- No data -->
    <template v-slot:no-data>
      <div class="py-8 base-table__text" v-html="noDataText" />
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { PropType, computed, defineComponent, getCurrentInstance, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { BaseTableHeaderI } from './interfaces'
import { DEFAULT_DATA_OPTIONS } from './resources'
import { DataOptions } from 'vuetify'
import HeaderFilter from './components/HeaderFilter.vue'
import _ from 'lodash'

// FUTURE: remove this in vue 3 upgrade (typing will be inferred properly)
interface BaseTableStateI {
  filtering: boolean,
  headers: BaseTableHeaderI[],
  sortedItems: object[],
  visibleItems: object[],
  tableDataOptions: DataOptions
}

export default defineComponent({
  components: { HeaderFilter },
  name: 'BaseVDataTable',
  emits: ['update-table-options'],
  props: {
    clearFiltersTrigger: { default: 1 },
    headerBg: { default: 'white' },
    height: { type: String },
    itemKey: { type: String },
    loading: { default: false },
    loadingText: { default: 'Loading...' },
    noDataText: { default: 'No results found.' },
    setItems: { default: [] as object[] },
    setHeaders: { default: [] as BaseTableHeaderI[] },
    setTableDataOptions: { default: () => _.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions },
    totalItems: { type: Number },
    pageHide: { default: false },
    updateFilter: { type: Function as PropType<(filterField?: string, value?: any) => void>, required: false },
    filters: { default: { isActive: false, filterPayload: {} }, required: false },
    customPagination: { default: false }
  },
  setup (props, { emit }) {
    // reactive vars
    const state = (reactive({
      filtering: false,
      headers: _.cloneDeep(props.setHeaders),
      sortedItems: [...props.setItems],
      visibleItems: [],
      tableDataOptions: props.setTableDataOptions
    }) as unknown) as BaseTableStateI

    const start = ref(0)
    const rowHeight = ref(75)
    const perPage = 10
    const timeout = ref(null)
    const vm = getCurrentInstance().proxy
    const regTable = ref(null)

    const onScroll = (e) => {
      timeout && clearTimeout(timeout)
      timeout.value = setTimeout(() => {
        const scrollTop = e.target.scrollTop
        const scrollBottom = scrollTop + e.target.clientHeight
        const rowsInView = Math.ceil(e.target.clientHeight / rowHeight.value)
        let startRow = Math.floor(scrollTop / rowHeight.value)
        const endRow = startRow + rowsInView

        // Handle scrolling up
        if (startRow < start.value) {
          start.value = startRow
        }

        // Handle scrolling down
        if (endRow > start.value + perPage) {
          start.value = endRow - perPage
        }

        // Update the scrollTop value to match the new start row
        vm.$nextTick(() => {
          e.target.scrollTop = scrollTop
        })
      }, 20)
    }

    onMounted(() => {
      const tableWrapper = document.querySelector('.v-data-table__wrapper')
      if (tableWrapper) tableWrapper.addEventListener('scroll', onScroll)
    })

    const sortedItemsLimited = computed(() => {
      const tableWrapper = document.querySelector('.v-data-table__wrapper')
      if (tableWrapper) {
        const rows = tableWrapper.getElementsByClassName('base-table__item-row')
        if (rows.length > 0) rowHeight.value = Array.from(rows).reduce((acc, row) => acc + row.clientHeight, 0) / rows.length
      }
      return state.sortedItems.slice(start.value, perPage + start.value)
    })

    const startHeight = computed(() => {
      return start.value * rowHeight.value - 80
    })

    const endHeight = computed(() => {
      return rowHeight.value * (state.sortedItems.length - start.value)
    })

    const filter = _.debounce(async (header: BaseTableHeaderI) => {
      // rely on custom filterApiFn to alter result set if given (meant for server side filtering)
      if (header.customFilter.filterApiFn) {
        state.filtering = true
        await header.customFilter.filterApiFn(header.customFilter.value)
        state.filtering = false
      }
    }, 500)

    const setFiltering = (filter: boolean) => {
      state.filtering = filter
    }

    const setSortedItems = (items: object[]) => {
      state.sortedItems = [...items]
    }

    watch(() => props.setItems, (val: object[]) => { state.sortedItems = [...val] })
    watch(() => props.setHeaders, (val: BaseTableHeaderI[]) => {
      // maintain filters
      const filters = {}
      state.headers.forEach((header) => {
        if (header.hasFilter) filters[header.col] = header.customFilter.value
      })
      val.forEach((header) => {
        if (Object.keys(filters).includes(header.col)) header.customFilter.value = filters[header.col]
      })
      state.headers = val
    })
    watch(() => props.clearFiltersTrigger, () => {
      state.headers.forEach((header) => {
        if (header.hasFilter) header.customFilter.value = ''
      })
      state.sortedItems = props.setItems
    })

    watch(() => state.tableDataOptions, (val: DataOptions) => { emit('update-table-options', val) })

    return {
      filter,
      setFiltering,
      ...toRefs(state),
      setSortedItems,
      onScroll,
      sortedItemsLimited,
      startHeight,
      endHeight,
      start,
      perPage,
      regTable
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
.base-table {

  &__header {

    &__filter {
      padding-top: 10px;

      &__select,
      &__textbox {
        font-size: 0.825rem !important;

        .v-input__control .v-input__slot .v-input__append-inner .v-input__icon.v-input__icon--clear .v-icon {
          color: $app-blue;
        }
      }
    }

    &__title {
      color: $gray9 !important;
      font-size: 0.875rem;
    }

  }

  &__item-cell {
    border: 0px;
    font-size: 0.875rem;
    padding: 8px 0 8px 16px;
    vertical-align: top;
  }

  &__text {
    border: 0px;
    position: sticky;
    left: 0;
    flex-grow: 0;
    flex-shrink: 0;
  }

  ::v-deep .v-data-footer {
    min-width: 100%;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar {
    width: .625rem;
    height: 0.50rem;
    overflow-x: hidden;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-track {
    overflow: auto;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-thumb {
    border-radius: 5px;
    background-color: lightgray;
  }

  ::v-deep .v-label,
  ::v-deep .v-label--active {
    color: $gray7 !important;
    font-size: .825rem;
    transform: None !important;
  }

  ::v-deep .v-label--active {
    color: $gray7;
    font-size: .825rem;
  }

  ::v-deep .v-input__slot {
    font-weight: normal;
    height: 42px !important;
    min-height: 42px !important;

    .v-select__slot label {
      top: 12px;
    }

    .v-text-field__slot input,
    .v-text-field__slot input::placeholder {
      color: $gray7;
      font-size: 0.825rem !important;
    }
  }

  ::v-deep .v-input__icon--clear .theme--light.v-icon {
    color: $app-blue;
  }

  ::v-deep .v-text-field--enclosed.v-input--dense:not(.v-text-field--solo) .v-input__append-inner {
    margin-top: 10px;
  }

  ::v-deep .v-list-item .v-list-item--link .theme--light:hover {
    background-color: $gray1;
  }
}
</style>
