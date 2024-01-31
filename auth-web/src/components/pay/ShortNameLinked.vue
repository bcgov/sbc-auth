<template>
  <BaseVDataTable
    id="linked-bank-short-names"
    class="transaction-list"
    :clearFiltersTrigger="clearFiltersTrigger"
    itemKey="id"
    :loading="false"
    loadingText="Loading Transaction Records..."
    noDataText="No Transaction Records"
    :setItems="tableState.results"
    :setHeaders="headers"
    :setTableDataOptions="tableDataOptions"
    title="Linked Bank Short Names"
    :totalItems="tableState.totalResults"
    pageHide="true"
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

import { Ref, defineComponent, onMounted, reactive, ref } from '@vue/composition-api'
import { BaseVDataTable } from '..'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { DataOptions } from 'vuetify'
import PaymentService from '@/services/payment.services'
import _ from 'lodash'
import debounce from '@/util/debounce'

export default defineComponent({
  name: 'ShortNameLinked',
  components: { BaseVDataTable },
  setup () {
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
        col: 'branchName',
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

    const clearFilters = () => {
      console.log('clear')
    }

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

    const loadLinkedShortnameList = debounce(async (filterField?: string, value?: any) => {
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
        const response = await PaymentService.getEFTShortNames('LINKED', tableState.filters)
        if (response?.data) {
          tableState.results = response.data.items || []
          tableState.totalResults = response.data.total
        } else throw new Error('No response from getEFTShortNames')
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error('Failed to get eftShortNames list.', error)
      }
      tableState.loading = false
    }, 200) as (filterField?: string, value?: any, viewAll?: boolean) => Promise<void>

    onMounted(async () => {
      await loadLinkedShortnameList()
    })

    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)

    const clearFiltersTrigger = ref(0)

    return {
      clearFilters,
      clearFiltersTrigger,
      headers,
      extended,
      tableDataOptions,
      tableState
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

#linked-bank-short-names {
  border: 1px solid #e9ecef
}
</style>
