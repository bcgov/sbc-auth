<template>
  <BaseVDataTable
    id="linked-bank-short-names"
    :clearFiltersTrigger="clearFiltersTrigger"
    itemKey="id"
    :loading="false"
    loadingText="Loading Linked Bank Short Names..."
    noDataText="No records to show."
    :setItems="state.results"
    :setHeaders="headers"
    :setTableDataOptions="state.options"
    :title="title"
    :totalItems="state.totalResults"
    :pageHide="true"
    :filters="state.filters"
    :updateFilter="updateFilter"
    :useObserver="true"
    :observerCallback="infiniteScrollCallback"
    @update-table-options="tableDataOptions = $event"
  >
    <template #header-title>
      <h2 class="ml-4 py-6">
        Linked Bank Short Names
        <span class="font-weight-regular">
          ({{ state.totalResults }})
        </span>
      </h2>
    </template>
    <template #header-filter-slot-actions>
      <v-btn
        v-if="state.filters.isActive"
        class="clear-btn mx-auto mt-auto"
        color="primary"
        outlined
        @click="clearFilters()"
      >
        Clear Filters
        <v-icon class="ml-1 mt-1">
          mdi-close
        </v-icon>
      </v-btn>
    </template>
    <template #item-slot-actions="{ index }">
      <div
        :id="`action-menu-${index}`"
        class="new-actions mx-auto"
      >
        <v-btn
          small
          color="primary"
          min-width="5rem"
          min-height="2rem"
          class="open-action-btn"
        >
          View
        </v-btn>
        <span class="more-actions">
          <v-menu
            v-model="state.actionDropdown[index]"
            :attach="`#action-menu-${index}`"
          >
            <template #activator="{ on }">
              <v-btn
                small
                color="primary"
                min-height="2rem"
                class="more-actions-btn"
                v-on="on"
              >
                <v-icon>{{ state.actionDropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
              </v-btn>
            </template>
            <v-list>
              <v-list-item
                class="actions-dropdown_item my-1"
                data-test="remove-linkage-button"
              >
                <v-list-item-subtitle>
                  <v-icon small>mdi-delete</v-icon>
                  <span class="pl-1">Remove Linkage</span>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-menu>
        </span>
      </div>
    </template>
  </BaseVDataTable>
</template>
<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref } from '@vue/composition-api'
import { BaseVDataTable } from '..'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { LinkedShortNameState } from '@/models/pay/short-name'
import { ShortNameStatus } from '@/util/constants'
import _ from 'lodash'
import { useShortNameTable } from '@/composables/short-name-table-factory'

/* Transactions table has pagination, this has infinite scroll.
 * Affiliations table grabs all of the results at once, this grabs it one page at a time (through infinite scroll).
 */
export default defineComponent({
  name: 'LinkedShortNameTable',
  components: { BaseVDataTable },
  setup (props, { emit }) {
    const state = reactive<LinkedShortNameState>({
      results: [],
      totalResults: 1,
      filters: {
        isActive: false,
        pageNumber: 1,
        pageLimit: 20,
        filterPayload: {
          accountName: '',
          shortName: '',
          accountBranch: '',
          accountId: '',
          state: ShortNameStatus.LINKED
        }
      },
      loading: false,
      actionDropdown: [],
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS)
    })

    const { infiniteScrollCallback, loadTableData, updateFilter } = useShortNameTable(state, emit)
    const createHeader = (col, label, type, value, hasFilter = true, minWidth = '125px') => ({
      col,
      customFilter: {
        filterApiFn: hasFilter ? (val: any) => loadTableData(col, val || '') : null,
        clearable: true,
        label,
        type,
        value: ''
      },
      hasFilter,
      minWidth,
      value
    })

    const headers = [
      createHeader('shortName', 'Bank Short Name', 'text', 'Bank Short Name', true, '125px'),
      createHeader('accountName', 'Account Name', 'text', 'Account Name', true, '125px'),
      createHeader('accountBranch', 'Branch Name', 'text', 'Branch Name', true, '125px'),
      createHeader('accountId', 'Account Number', 'text', 'Account Number', true, '125px'),
      {
        col: 'actions',
        hasFilter: false,
        minWidth: '164px',
        value: 'Actions',
        width: '164px'
      }
    ]

    const title = computed<string>(() => {
      return `Linked Bank Short Names (${state.totalResults})`
    })

    onMounted(async () => {
      await loadTableData()
    })

    const clearFiltersTrigger = ref(0)
    async function clearFilters (): Promise<void> {
      clearFiltersTrigger.value++
      state.filters.filterPayload = { state: ShortNameStatus.LINKED }
      state.filters.isActive = false
      await loadTableData()
    }

    return {
      clearFilters,
      clearFiltersTrigger,
      infiniteScrollCallback,
      headers,
      state,
      title,
      updateFilter
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';


#linked-bank-short-names {
  border: 1px solid #e9ecef
}
</style>
