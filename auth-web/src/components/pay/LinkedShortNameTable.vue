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
    :setTableDataOptions="tableDataOptions"
    :title="title"
    :totalItems="state.totalResults"
    :pageHide="true"
    :filters="state.filters"
    :updateFilter="updateFilter"
    :useObserver="true"
    :observerCallback="infiniteScrollCallback"
    @update-table-options="tableDataOptions = $event"
  >
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
    <template #item-slot-actions="{ item, index }">
      <div
          :id="`action-menu-${index}`"
          class="mx-auto"
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
            v-model="actionDropdown[index]"
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
                <v-icon>{{ actionDropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
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
import { Ref, computed, defineComponent, onMounted, reactive, ref } from '@vue/composition-api'
import { BaseVDataTable } from '..'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { DataOptions } from 'vuetify'
import PaymentService from '@/services/payment.services'
import { LinkedShortNameFilterParams } from '@/models/pay/shortname'
import _ from 'lodash'

export default defineComponent({
  name: 'LinkedShortNameTable',
  components: { BaseVDataTable },
  setup (props, { emit }) {
    const actionDropdown: Ref<boolean[]> = ref([])
    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)
    const title = computed(() => {
      return `Linked Bank Short Names (${state.totalResults})`
    })

    const headers = [
      {
        col: 'shortName',
        customFilter: {
          clearable: true,
          label: 'Bank Short Name',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Bank Short Name'
      },
      {
        col: 'accountName',
        customFilter: {
          clearable: true,
          label: 'Account Name',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Account Name'
      },
      {
        col: 'accountBranch',
        customFilter: {
          clearable: true,
          label: 'Branch Name',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Branch Name'
      },
      {
        col: 'accountId',
        customFilter: {
          clearable: true,
          label: 'Account Number',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Account Number'
      },
      {
        col: 'actions',
        hasFilter: false,
        minWidth: '164px',
        value: 'Actions',
        width: '164px'
      }
    ]

    const state = reactive({
      results: [
        {
          accountName: 'RCPV',
          shortName: 'RCPV',
          accountBranch: 'Saanich',
          accountId: '3199',
          id: 1
        }
      ],
      totalResults: 1,
      filters: {
        isActive: false,
        pageNumber: 1,
        pageLimit: 20,
        filterPayload: {
          accountName: '',
          shortName: '',
          accountBranch: '',
          accountId: ''
        } 
      } as LinkedShortNameFilterParams,
      loading: false
    })

    onMounted(async () => {
      headers.forEach((header) => {
        if (header.hasFilter) {
          (header.customFilter as any).filterApiFn = (val: any) => loadTableData(header.col, val || '')
        }
      })
      await loadTableData()
    })

    // This is also called inside of the HeaderFilter component inside of the BaseVDataTable component
    async function loadTableData (filterField?: string, value?: any, appendToResults = false) {
      state.loading = true
      if (filterField) {
        state.filters.pageNumber = 1
        state.filters.filterPayload[filterField] = value
      }
      let filtersActive = false
      for (const key in state.filters.filterPayload) {
        if (key === 'dateFilter') {
          if (state.filters.filterPayload[key].endDate) filtersActive = true
        } else if (state.filters.filterPayload[key]) filtersActive = true
        if (filtersActive) break
      }
      state.filters.isActive = filtersActive

      try {
        const response = await PaymentService.getEFTShortNames(state.filters, 'LINKED')
        if (response?.data) {
          // We use appendToResults for infinite scroll, so we keep the existing results.
          state.results = appendToResults ? state.results.concat(response.data.items) : response.data.items
          state.totalResults = response.data.total
          emit('shortname-state-total', response.data.stateTotal)
        } else {
          throw new Error('No response from getEFTShortNames')
        }
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTShortNames list.', error)
      }
      state.loading = false
    }

    const clearFiltersTrigger = ref(0)
    async function clearFilters () {
      clearFiltersTrigger.value++
      state.filters.filterPayload = {}
      state.filters.isActive = false
      await loadTableData()
    }

    function updateFilter (filterField?: string, value?: any) {
      if (filterField) {
        if (value) {
          state.filters.filterPayload[filterField] = value
          state.filters.isActive = true
        } else {
          delete state.filters.filterPayload[filterField]
        }
      }
      if (Object.keys(state.filters.filterPayload).length === 0) {
        state.filters.isActive = false
      } else {
        state.filters.isActive = true
      }
    }

    async function infiniteScrollCallback() {
      state.filters.pageNumber++
      await loadTableData(null, null, true)
    }

    return {
      actionDropdown,
      clearFilters,
      clearFiltersTrigger,
      infiniteScrollCallback,
      headers,
      tableDataOptions,
      state,
      title,
      updateFilter
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

#linked-bank-short-names {
  border: 1px solid #e9ecef
}

// For the dropdown text color. TODO: Refactor 
::v-deep .theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  font-weight: normal;
  .v-icon.v-icon {
    color: $app-blue;
  }
}

.open-action-btn {
  border-top-right-radius: 0px;
  border-bottom-right-radius: 0px;
  min-width: 4.9rem
}

::v-deep {
  .v-btn + .v-btn {
      margin-left: 0.5rem;
  }

  .base-table__header > tr:first-child > th  {
    padding: 0 0 0 0 !important;
  }
  .base-table__header__filter {
    padding-left: 16px;
    padding-right: 4px;
  }
  .base-table__item-row {
    color: #495057;
    font-weight: bold;
  }
  .base-table__item-cell {
    padding: 16px 0 16px 16px;
    vertical-align: middle;
  }
}
</style>
