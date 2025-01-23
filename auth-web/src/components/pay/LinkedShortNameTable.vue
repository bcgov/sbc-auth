<template>
  <div>
    <BaseVDataTable
      id="linked-bank-short-names"
      :clearFiltersTrigger="clearFiltersTrigger"
      itemKey="id"
      :loading="loading"
      loadingText="Loading Linked Bank Short Names..."
      noDataText="No records to show."
      :setItems="results"
      :setHeaders="headers"
      :setTableDataOptions="options"
      :hasTitleSlot="true"
      :totalItems="totalResults"
      :pageHide="true"
      :filters="filters"
      :updateFilter="updateFilter"
      :useObserver="true"
      :observerCallback="infiniteScrollCallback"
      @update-table-options="tableDataOptions = $event"
    >
      <template #header-title>
        <h2 class="ml-4 py-6">
          EFT Enabled Accounts
          <span class="font-weight-regular">
            ({{ totalResults }})
          </span>
        </h2>
      </template>
      <template #header-filter-slot-actions>
        <v-btn
          v-if="filters.isActive"
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
      <template #item-slot-shortNameType="{ item }">
        <span>{{ getShortNameTypeDescription(item.shortNameType) }}</span>
      </template>
      <template #item-slot-accountName="{ item }">
        <span>{{ item.accountName }}</span>
        <v-chip
          v-if="item.cfsAccountStatus === CfsAccountStatus.FREEZE"
          small
          label
          color="error"
          class="item-chip"
        >
          {{ SuspensionReason.NSF_SUSPENDED }}
        </v-chip>
      </template>
      <template #item-slot-amountOwing="{ item }">
        <span>{{ formatAmount(item.amountOwing) }}</span>
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
            @click="viewDetails(index)"
          >
            View Detail
          </v-btn>
        </div>
      </template>
    </BaseVDataTable>
  </div>
</template>
<script lang="ts">
import {
  AccountStatus,
  CfsAccountStatus,
  SessionStorageKeys,
  ShortNameStatus,
  SuspensionReason
} from '@/util/constants'
import { defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { BaseVDataTable } from '..'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { LinkedShortNameState } from '@/models/pay/short-name'
import ShortNameUtils from '@/util/short-name-utils'
import _ from 'lodash'
import { useShortNameTable } from '@/composables/short-name-table-factory'

/* Transactions table has pagination, this has infinite scroll.
 * Affiliations table grabs all of the results at once, this grabs it one page at a time (through infinite scroll).
 */
export default defineComponent({
  name: 'LinkedShortNameTable',
  components: { BaseVDataTable },
  props: {
    currentTab: { default: 0 }
  },
  setup (props, { emit, root }) {
    const state = reactive<LinkedShortNameState>({
      results: [],
      totalResults: 1,
      filters: {
        isActive: false,
        pageNumber: 1,
        pageLimit: 20,
        filterPayload: defaultFilterPayload()
      },
      loading: false,
      actionDropdown: [],
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS),
      clearFiltersTrigger: 0
    })

    const { infiniteScrollCallback, loadTableData, updateFilter } = useShortNameTable(state, emit)
    const createHeader = (col, label, type, value, filterValue = '', hasFilter = true, minWidth = '125px',
      width = '125px', filterItems = []) => ({
      col,
      customFilter: {
        filterApiFn: hasFilter ? (val: any) => loadTableData(col, val || '') : null,
        clearable: true,
        items: filterItems.length > 0 ? filterItems : undefined,
        label,
        type,
        value: filterValue
      },
      hasFilter,
      minWidth,
      width,
      value
    })

    const {
      shortName = '',
      shortNameType = '',
      accountName = '',
      accountBranch = '',
      accountId = '',
      amountOwing = '',
      statementId = ''
    } = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.LinkedShortNamesFilter) || '{}')

    const headers = [
      createHeader(
        'shortName',
        'Bank Short Name',
        'text',
        'Short Name',
        shortName,
        true,
        '180px'
      ),
      createHeader(
        'shortNameType',
        'Type',
        'select',
        'Type',
        shortNameType,
        true,
        '200px',
        '200px',
        ShortNameUtils.ShortNameTypeItems
      ),
      createHeader(
        'accountName',
        'Account Name',
        'text',
        'Account Name',
        accountName,
        true,
        '280px'
      ),
      createHeader('accountBranch',
        'Branch Name',
        'text',
        'Branch Name',
        accountBranch,
        true,
        '175px'
      ),
      createHeader(
        'accountId',
        'Account Number',
        'text',
        'Account Number',
        accountId,
        true,
        '180px'
      ),
      createHeader(
        'amountOwing',
        'Total Amount Owing',
        'text',
        'Total Amount Owing',
        amountOwing,
        true,
        '200px'
      ),
      createHeader(
        'statementId',
        'Latest Statement Number',
        'text',
        'Latest Statement Number',
        statementId,
        true,
        '235px'
      ),
      {
        col: 'actions',
        hasFilter: false,
        minWidth: '164px',
        value: 'Actions',
        width: '130px',
        class: 'fixed-action-column',
        itemClass: 'fixed-action-column'
      }
    ]

    async function clearFilters (): Promise<void> {
      state.clearFiltersTrigger++
      state.filters.filterPayload = defaultFilterPayload()
      state.filters.isActive = false
      await loadTableData()
    }

    function defaultFilterPayload () {
      return {
        accountName: '',
        shortName: '',
        shortNameType: '',
        accountBranch: '',
        accountId: '',
        state: ShortNameStatus.LINKED
      }
    }

    function formatAmount (amount: number) {
      return amount !== undefined ? CommonUtils.formatAmount(amount) : ''
    }

    function viewDetails (index) {
      root.$router?.push({
        name: 'shortnamedetails',
        params: {
          'shortNameId': state.results[index].id?.toString()
        }
      })
    }

    async function loadData () {
      try {
        state.filters.filterPayload = JSON.parse(
          ConfigHelper.getFromSession(SessionStorageKeys.LinkedShortNamesFilter)) || state.filters.filterPayload
      } catch {
        // Silent catch
      }
      await loadTableData()
    }

    watch(() => props.currentTab, () => {
      loadData()
    })

    onMounted(async () => {
      await loadData()
    })

    watch(() => state.filters, (filters: any) => {
      ConfigHelper.addToSession(SessionStorageKeys.LinkedShortNamesFilter, JSON.stringify(filters.filterPayload))
    }, { deep: true })

    return {
      ...toRefs(state),
      clearFilters,
      infiniteScrollCallback,
      headers,
      state,
      updateFilter,
      viewDetails,
      formatAmount,
      CfsAccountStatus,
      AccountStatus,
      SuspensionReason,
      getShortNameTypeDescription: ShortNameUtils.getShortNameTypeDescription
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';

.v-btn {
  border-radius: 4px !important;
  height: 40px !important;
  padding: 0 24px 0 24px !important;
  top: -5px;
}

#linked-bank-short-names {
  border: 1px solid #e9ecef;
  font-weight: bold;
}
.item-chip {
  margin-left: 1em;
}
</style>
