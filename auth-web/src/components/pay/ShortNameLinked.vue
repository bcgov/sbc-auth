<template>
  <BaseVDataTable
    id="linked-bank-short-names"
    class="transaction-list"
    :clearFiltersTrigger="clearFiltersTrigger"
    itemKey="id"
    :loading="false"
    loadingText="Loading Linked Bank Short Names..."
    noDataText="No records to show."
    :setItems="tableState.results"
    :setHeaders="headers"
    :setTableDataOptions="tableDataOptions"
    :title="tableTitle"
    :totalItems="tableState.totalResults"
    pageHide="true"
    :filters="tableState.filters"
    :updateFilter="updateFilter"
    @update-table-options="tableDataOptions = $event"
  >
    <template #header-filter-slot-actions>
      <v-btn
        v-if="tableState.filters.isActive"
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
  </BaseVDataTable>
</template>
<script lang="ts">
import { Ref, computed, defineComponent, onMounted, reactive, ref } from '@vue/composition-api'
import { BaseVDataTable } from '..'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { DataOptions } from 'vuetify'
import PaymentService from '@/services/payment.services'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameLinked',
  components: { BaseVDataTable },
  setup (props, { emit }) {
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

    const extended = ref(true)

    const tableTitle = computed(() => {
      return `Linked Bank Short Names (${tableState.totalResults})`
    })
    
    const tableState = reactive({
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
        filterPayload: {
          accountName: '',
          shortName: '',
          accountBranch: '',
          accountId: ''
        }
      },
      loading: false
    })

    const clearFiltersTrigger = ref(0)

    const loadLinkedShortnameList = async (filterField?: string, value?: any) => {
      tableState.loading = true
      if (filterField) {
        tableState.filters.pageNumber = 1
        tableState.filters.filterPayload[filterField] = value
      }
      let filtersActive = false
      for (const key in tableState.filters.filterPayload) {
        if (key === 'dateFilter') {
          if (tableState.filters.filterPayload[key].endDate) filtersActive = true
        } else if (tableState.filters.filterPayload[key]) filtersActive = true
        if (filtersActive) break
      }
      tableState.filters.isActive = filtersActive

      try {
        const response = await PaymentService.getEFTShortNames(tableState.filters, 'LINKED')
        if (response?.data) {
          tableState.results = response.data.items || []
          tableState.totalResults = response.data.total
          emit('shortname-state-total', response.data.stateTotal)
        } else throw new Error('No response from getEFTShortNames')
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to getEFTShortNames list.', error)
      }
      tableState.loading = false
    }

    // TODO genericize
    const clearAllFilters = async () => {
      tableState.filters.filterPayload = {} as any
      tableState.filters.isActive = false
      await loadLinkedShortnameList()
    }

    // TODO genericize
    const clearFilters = () => {
      clearFiltersTrigger.value++
      // clear affiliation state filters and trigger search
      clearAllFilters()
    }

    // TODO make this generic.
    const updateFilter = (filterField?: string, value?: any) => {
      if (filterField) {
        if (value) {
          tableState.filters.filterPayload[filterField] = value
          tableState.filters.isActive = true
        } else {
          delete tableState.filters.filterPayload[filterField]
        }
      }
      if (Object.keys(tableState.filters.filterPayload).length === 0) {
        tableState.filters.isActive = false
      } else {
        tableState.filters.isActive = true
      }
    }

    headers.forEach((header) => {
      if (header.hasFilter) {
        (header.customFilter as any).filterApiFn = (val: any) => loadLinkedShortnameList(header.col, val || '')
      }
    })

    onMounted(async () => {
      await loadLinkedShortnameList()
    })

    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)

    return {
      clearFilters,
      clearFiltersTrigger,
      headers,
      extended,
      tableDataOptions,
      tableState,
      tableTitle,
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

::v-deep {
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
