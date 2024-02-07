<template>
  <div>
    <ModalDialog
      ref="accountLinkingDialog"
      dialog-class="notify-dialog"
      max-width="640"
      :show-icon="false"
    >
      <template #title>
        <h1 class="text-left">
          Linking {{ state.selectedShortName.shortName }} to an Account
        </h1>
        <v-card-title>
          Search by Account ID or Name to Link:
          <v-btn
            large
            icon
            aria-label="Close Dialog"
            title="Close Dialog"
            :disabled="false"
            style="pointer-events: auto;"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
      </template>
      <template #text>
        <h4>
          Search by Account ID or Name to Link:
        </h4>
        <ShortNameLookup
          :key="state.shortNameLookupKey"
          @business="state.selectedShortName"
        />
      </template>
      <template #actions>
        <v-btn
          large
          color="outlined"
          data-test="dialog-ok-button"
          @click="closeAccountLinkingDialog()"
        >
          Close
        </v-btn>
        <v-btn
          large
          color="primary"
          data-test="dialog-ok-button"
          @click="closeAccountLinkingDialog()"
        >
          Link to an Account and Settle Payment
        </v-btn>
      </template>
    </ModalDialog>
    <DatePicker
      v-show="state.showDatePicker"
      ref="datePicker"
      :reset="state.dateRangeReset"
      class="date-picker"
      :setEndDate="state.endDate"
      :setStartDate="state.startDate"
      @submit="updateDateRange($event)"
    />
    <BaseVDataTable
      id="unlinked-bank-short-names"
      :clearFiltersTrigger="state.clearFiltersTrigger"
      itemKey="id"
      :loading="false"
      loadingText="Loading Unlinked Payments..."
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
      @update-table-options="options = $event"
    >
      <template #header-title>
        <h2 class="ml-4 py-6">
          Unlinked Payments
          <span class="font-weight-regular">
            ({{ state.totalResults }})
          </span>
        </h2>
      </template>
      <template #header-filter-slot-transactionDate>
        <div @click="clickDatePicker()">
          <v-text-field
            v-model="state.dateRangeText"
            class="base-table__header__filter__textbox date-filter"
            :append-icon="'mdi-calendar'"
            clearable
            dense
            filled
            hide-details
            :placeholder="'Date'"
            :value="state.dateRangeSelected ? 'Custom' : ''"
            @click:clear="state.dateRangeReset++"
          />
        </div>
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
      <template #item-slot-depositAmount="{ item }">
        <span>{{ formatAmount(item.depositAmount) }}</span>
      </template>
      <template #item-slot-transactionDate="{ item }">
        <span>{{ formatDate(item.transactionDate) }}</span>
      </template>
      <template #item-slot-actions="{ item, index }">
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
            @click="openAccountLinkingDialog(item)"
          >
            Link to Account
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
                  <v-list-item-subtitle
                    @click="viewDetails(index)"
                  >
                    <v-icon small>mdi-format-list-bulleted</v-icon>
                    <span class="pl-1">View Detail</span>
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
import ConfigHelper from '@/util/config-helper'
import { BaseVDataTable, DatePicker } from '..'
import { Ref, defineComponent, onMounted, reactive, ref } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import ShortNameLookup from './ShortNameLookup.vue'
import { ShortNameStatus } from '@/util/constants'
import { UnlinkedShortNameState } from '@/models/pay/short-name'
import _ from 'lodash'
import { useShortNameTable } from '@/composables/short-name-table-factory'

export default defineComponent({
  name: 'UnlinkedShortNameTable',
  components: { BaseVDataTable, DatePicker, ModalDialog, ShortNameLookup },
  setup (props, { emit, root }) {
    const datePicker = ref(null)
    const accountLinkingDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const state = reactive<UnlinkedShortNameState>({
      results: [],
      totalResults: 1,
      filters: {
        isActive: false,
        pageNumber: 1,
        pageLimit: 20,
        filterPayload: {
          shortName: '',
          transactionDate: '',
          depositAmount: 0,
          state: ShortNameStatus.UNLINKED
        }
      },
      loading: false,
      actionDropdown: [],
      options: _.cloneDeep(DEFAULT_DATA_OPTIONS),
      shortNameLookupKey: 0,
      dateRangeReset: 0,
      clearFiltersTrigger: 0,
      selectedShortName: {},
      showDatePicker: false,
      dateRangeSelected: false,
      dateRangeText: ''
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
      createHeader('shortName', 'Bank Short Name', 'text', 'Bank Short Name'),
      {
        col: 'transactionDate',
        hasFilter: false,
        label: 'Initial Payment Received Date',
        value: 'Initial Payment Received Date',
        minWidth: '260px'
      },
      createHeader('depositAmount', 'Initial Payment Amount', 'text', 'Initial Payment Amount'),
      {
        col: 'actions',
        hasFilter: false,
        value: 'Actions',
        minWidth: '200px'
      }
    ]

    function formatAmount (amount: number) {
      if (amount) {
        return CommonUtils.formatAmount(amount)
      }
      return ''
    }

    function formatDate (date: string) {
      return CommonUtils.formatDisplayDate(date, 'MMMM DD, YYYY')
    }

    function updateDateRange ({ endDate, startDate }: { endDate?: string, startDate?: string }): void {
      state.showDatePicker = false
      state.dateRangeSelected = !!(endDate && startDate)
      if (!state.dateRangeSelected) { endDate = ''; startDate = '' }
      state.dateRangeText = state.dateRangeSelected ? `${formatDate(startDate)} - ${formatDate(endDate)}` : ''
      loadTableData('transactionDate', { endDate, startDate })
    }

    function openAccountLinkingDialog (item: any) {
      state.selectedShortName = item
      accountLinkingDialog.value.open()
    }

    function closeAccountLinkingDialog () {
      accountLinkingDialog.value.close()
    }

    async function clickDatePicker () {
      state.showDatePicker = true
    }

    async function clearFilters () {
      state.clearFiltersTrigger++
      state.dateRangeReset++
      state.filters.filterPayload = { state: ShortNameStatus.UNLINKED }
      state.filters.isActive = false
      await loadTableData()
    }

    function viewDetails (index) {
      root.$router?.push({
        name: 'shortnamedetails',
        params: {
          'shortNameId': state.results[index].id
        }
      })
    }

    onMounted(async () => {
      await loadTableData()
    })

    return {
      clearFilters,
      infiniteScrollCallback,
      headers,
      state,
      updateFilter,
      formatAmount,
      formatDate,
      updateDateRange,
      clickDatePicker,
      accountLinkingDialog,
      openAccountLinkingDialog,
      closeAccountLinkingDialog,
      datePicker,
      viewDetails
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';

#unlinked-bank-short-names {
  border: 1px solid #e9ecef
}

</style>
