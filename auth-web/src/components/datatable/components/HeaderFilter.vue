<!-- header filter in a seperate component helps improve performance -->
<template>
  <span>
    <slot
      :name="'header-filter-slot-' + header.col"
      :header="header"
    >
      <v-select
        v-if="header.hasFilter && header.customFilter.type === 'select'"
        v-model="header.customFilter.value"
        :class="['base-table__header__filter__select']"
        :clearable="header.customFilter.clearable"
        dense
        filled
        hide-details
        item-text="text"
        item-value="value"
        :items="header.customFilter.items"
        :label="!header.customFilter.value ? header.customFilter.label || '' : ''"
        @reset="filter(header)"
        @input="filter(header)"
      />
      <v-text-field
        v-else-if="header.hasFilter && header.customFilter.type === 'text'"
        v-model.lazy="header.customFilter.value"
        :class="['base-table__header__filter__textbox', header.customFilter.value ? 'active' : '']"
        :clearable="header.customFilter.clearable"
        dense
        filled
        hide-details
        :placeholder="!header.customFilter.value ? header.customFilter.label || '' : ''"
        @reset="filter(header)"
        @input="filter(header)"
      />
    </slot>
  </span>
</template>

<script lang="ts">
import { BaseSelectFilter, BaseTextFilter } from '../resources/base-filters'
import { PropType, defineComponent, reactive } from '@vue/composition-api'
import { BaseTableHeaderI } from '../interfaces'
import debounce from '@/util/debounce'
import { headerTypes } from '@/resources/table-headers/affiliations-table/headers'

const tempHeader = {
  col: '',
  hasFilter: false,
  value: ''
}

// FUTURE: remove this in vue 3 upgrade (typing will be inferred properly)
interface BaseTableStateI {
sortedItems: object[]
}

export default defineComponent({
  name: 'HeaderFilter',
  props: {
    header: { default: tempHeader as BaseTableHeaderI },
    filtering: { default: false },
    setFiltering: { type: Function as PropType<(filter?: boolean) => void>, required: true },
    sortedItems: { default: [] as object[] },
    filters: { default: { isActive: false, filterPayload: {} }, required: false },
    updateFilter: { type: Function as PropType<(filterField?: string, value?: any) => void>, required: true },
    headers: { default: [] as BaseTableHeaderI[] },
    setSortedItems: { type: Function as PropType<(items: object[], init?: boolean) => void>, required: true }
  },
  setup (props) {
    const state = (reactive({
      sortedItems: [...props.sortedItems]
    }) as unknown) as BaseTableStateI

    const serverSideFilter = debounce(async (header: BaseTableHeaderI) => {
      props.setFiltering(true)
      await header.customFilter.filterApiFn(header.customFilter.value)
      props.setFiltering(false)
    })

    const filter = async (header: BaseTableHeaderI) => {
      if (header.customFilter.filterApiFn) {
        await serverSideFilter(header)
      } else {
        applyFilters(props, state, header)
      }
    }

    function applyFilters (props, state, header) {
      if (props.updateFilter) {
        props.updateFilter(header.col, header.customFilter.value)
      }

      if (!props.filters.isActive) {
        props.setSortedItems(props.sortedItems, true)
        return
      }

      state.sortedItems = props.sortedItems.filter((item, i) => {
        let display = true

        for (let col in props.filters.filterPayload) {
          const headersArray = props.headers
          const index = headersArray.findIndex(item => item.col === col)

          const colValue = props.headers[index].customFilter.items[i].text
          const filterValue = props.filters.filterPayload[col]

          if (headerTypes[col].type === 'select') {
            display = BaseSelectFilter(colValue, filterValue)
          } else {
            display = BaseTextFilter(colValue, filterValue)
          }

          if (!display) {
            return display
          }
        }

        return display
      })

      if (props.setSortedItems) {
        props.setSortedItems(state.sortedItems, true)
      }
    }

    return {
      filter
    }
  }
})
</script>
