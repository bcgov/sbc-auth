<template>
  <div>
    <v-snackbar
      id="linked-account-snackbar"
      v-model="state.snackbar"
      :timeout="4000"
      transition="fade"
    >
      {{ state.snackbarText }}
    </v-snackbar>
    <BaseVDataTable
      id="linked-bank-short-names"
      :clearFiltersTrigger="state.clearFiltersTrigger"
      itemKey="id"
      :loading="false"
      loadingText="Loading Linked Bank Short Names..."
      noDataText="No records to show."
      :setItems="state.results"
      :setHeaders="headers"
      :setTableDataOptions="state.options"
      :hasTitleSlot="true"
      :totalItems="state.totalResults"
      :pageHide="true"
      :filters="state.filters"
      :updateFilter="updateFilter"
      :useObserver="true"
      :observerCallback="infiniteScrollCallback"
      :highlight-index="state.highlightIndex"
      highlight-class="base-table__item-row-green"
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
      <template #item-slot-accountName="{ item }">
        <span>{{item.accountName}}</span>
        <v-chip
          small
          label
          color="error"
          class="item-chip"
          v-if="item.cfsAccountStatus && item.cfsAccountStatus !== 'ACTIVE'"
        >
          SUSPENDED
        </v-chip>
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
  </div>
</template>
<script lang="ts">
import { SessionStorageKeys, ShortNameStatus } from '@/util/constants'
import { defineComponent, onMounted, reactive, watch } from '@vue/composition-api'
import { BaseVDataTable } from '..'
import ConfigHelper from '@/util/config-helper'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { EFTShortnameResponse } from '@/models/eft-transaction'
import { LinkedShortNameState } from '@/models/pay/short-name'
import _ from 'lodash'
import { useShortNameTable } from '@/composables/short-name-table-factory'

/* Transactions table has pagination, this has infinite scroll.
 * Affiliations table grabs all of the results at once, this grabs it one page at a time (through infinite scroll).
 */
export default defineComponent({
  name: 'LinkedShortNameTable',
  components: { BaseVDataTable },
  props: {
    linkedAccount: { default: {} }
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
      highlightIndex: -1,
      snackbar: false,
      snackbarText: '',
      clearFiltersTrigger: 0
    })

    const { infiniteScrollCallback, loadTableData, updateFilter } = useShortNameTable(state, emit)
    const createHeader = (col, label, type, value, filterValue = '', hasFilter = true, minWidth = '125px') => ({
      col,
      customFilter: {
        filterApiFn: hasFilter ? (val: any) => loadTableData(col, val || '') : null,
        clearable: true,
        label,
        type,
        value: filterValue
      },
      hasFilter,
      minWidth,
      value
    })

    const {
      shortName = '',
      accountName = '',
      accountBranch = '',
      accountId = ''
    } = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.LinkedShortNamesFilter) || '{}')

    const headers = [
      createHeader('shortName', 'Bank Short Name', 'text', 'Bank Short Name', shortName),
      createHeader('accountName', 'Account Name', 'text', 'Account Name', accountName),
      createHeader('accountBranch', 'Branch Name', 'text', 'Branch Name', accountBranch),
      createHeader('accountId', 'Account Number', 'text', 'Account Number', accountId),
      {
        col: 'actions',
        hasFilter: false,
        minWidth: '164px',
        value: 'Actions',
        width: '164px'
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
        accountBranch: '',
        accountId: '',
        state: ShortNameStatus.LINKED
      }
    }

    function viewDetails (index) {
      root.$router?.push({
        name: 'shortnamedetails',
        params: {
          'shortNameId': state.results[index].id?.toString()
        }
      })
    }

    async function onLinkedAccount (account: EFTShortnameResponse) {
      if (account) {
        await loadTableData()
        state.snackbarText = `Bank short name ${account.shortName} was successfully linked.`
        state.highlightIndex = state.results.findIndex((result) => result.id === account.id)
        state.snackbar = true
        setTimeout(() => {
          state.highlightIndex = -1
        }, 4000)
      }
    }

    onMounted(async () => {
      try {
        state.filters.filterPayload = JSON.parse(
          ConfigHelper.getFromSession(SessionStorageKeys.LinkedShortNamesFilter)) || state.filters.filterPayload
      } catch {
        // Silent catch
      }
      await loadTableData()
    })

    watch(() => props.linkedAccount, (account: EFTShortnameResponse) => {
      onLinkedAccount(account)
    })

    watch(() => state.filters, (filters: any) => {
      ConfigHelper.addToSession(SessionStorageKeys.LinkedShortNamesFilter, JSON.stringify(filters.filterPayload))
    }, { deep: true })

    return {
      clearFilters,
      infiniteScrollCallback,
      headers,
      state,
      updateFilter,
      viewDetails
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';

#linked-bank-short-names {
  border: 1px solid #e9ecef;
  font-weight: bold;
}
.item-chip {
  margin-left: 1em;
}
</style>
