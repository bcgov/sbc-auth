<template>
  <v-data-table
    class="base-table"
    :disable-sort="true"
    :fixed-header="height ? true : false"
    :footer-props="{ itemsPerPageOptions: [5, 10, 15, 20] }"
    :headers="headers"
    hide-default-header
    :height="height ? height : ''"
    :items="sortedItems"
    :loading="filtering || loading"
    :mobile-breakpoint="0"
    :options.sync="tableDataOptions"
    :server-items-length="totalItems"
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
              <slot :name="'header-filter-slot-' + header.col" :header="header">
                <v-select
                  v-if="header.hasFilter && header.customFilter.type === 'select'"
                  :class="['base-table__header__filter__select']"
                  :clearable="header.customFilter.clearable"
                  dense
                  filled
                  hide-details
                  item-text="text"
                  item-value="value"
                  :items="header.customFilter.items"
                  :label="!header.customFilter.value ? header.customFilter.label || '' : ''"
                  :open-on-clear="true"
                  v-model="header.customFilter.value"
                  @reset="filter(header)"
                  @input="filter(header)"
                />
                <v-text-field
                  v-else-if="header.hasFilter && header.customFilter.type === 'text'"
                  :class="['base-table__header__filter__textbox', header.customFilter.value ? 'active' : '']"
                  :clearable="header.customFilter.clearable"
                  dense
                  filled
                  hide-details
                  :placeholder="!header.customFilter.value ? header.customFilter.label || '' : ''"
                  v-model="header.customFilter.value"
                  @reset="filter(header)"
                  @input="filter(header)"
                />
              </slot>
            </th>
          </tr>
        </slot>
      </thead>
    </template>

    <!-- Items -->
    <template v-slot:item="{ item }">
      <tr class="base-table__item-row" :key="item[itemKey]">
        <td
          v-for="header in headers" :key="'item-' + header.col"
          :class="[header.itemClass, 'base-table__item-cell']"
        >
          <slot :header="header" :item="item" :name="'item-slot-' + header.col">
            <span v-if="header.itemFn" v-html="header.itemFn(item)" />
            <span v-else>{{ item[header.col] }}</span>
          </slot>
        </td>
      </tr>
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
import { defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import { BaseTableHeaderI } from './interfaces'
import { DEFAULT_DATA_OPTIONS } from './resources'
import { DataOptions } from 'vuetify'
import _ from 'lodash'

// FUTURE: remove this in vue 3 upgrade (typing will be inferred properly)
interface BaseTableStateI {
  filtering: boolean,
  headers: BaseTableHeaderI[],
  sortedItems: object[],
  tableDataOptions: DataOptions
}

export default defineComponent({
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
    totalItems: { type: Number }
  },
  setup (props, { emit }) {
    // reactive vars
    const state = (reactive({
      filtering: false,
      headers: _.cloneDeep(props.setHeaders),
      sortedItems: [...props.setItems],
      tableDataOptions: props.setTableDataOptions
    }) as unknown) as BaseTableStateI

    const filter = _.debounce(async (header: BaseTableHeaderI) => {
      // rely on custom filterApiFn to alter result set if given (meant for server side filtering)
      if (header.customFilter.filterApiFn) {
        state.filtering = true
        await header.customFilter.filterApiFn(header.customFilter.value)
        state.filtering = false
      }
    }, 500)

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
    })
    watch(() => props.setTableDataOptions, (val: DataOptions) => { state.tableDataOptions = val })
    watch(() => state.tableDataOptions, (val: DataOptions) => { emit('update-table-options', val) })

    return {
      filter,
      ...toRefs(state)
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

  ::v-deep .v-label {
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
