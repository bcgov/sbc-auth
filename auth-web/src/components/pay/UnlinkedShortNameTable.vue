<template>
  <div>
    <ShortNameLinkingDialog
      :isShortNameLinkingDialogOpen="isShortNameLinkingDialogOpen"
      :selectedShortName="selectedShortName"
      @close-short-name-linking-dialog="closeShortNameLinkingDialog"
      @on-link-account="onLinkAccount"
    />
    <DatePicker
      v-show="showDatePicker"
      ref="datePicker"
      :reset="dateRangeReset"
      class="date-picker"
      :setEndDate="endDate"
      :setStartDate="startDate"
      @submit="updateDateRange($event)"
    />
    <BaseVDataTable
      id="unlinked-bank-short-names"
      :clearFiltersTrigger="clearFiltersTrigger"
      itemKey="id"
      :loading="false"
      loadingText="Loading Unlinked Payments..."
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
      @update-table-options="options = $event"
    >
      <template #header-title>
        <h2 class="ml-4 py-6">
          Unlinked Payments
          <span class="font-weight-regular">
            ({{ totalResults }})
          </span>
        </h2>
      </template>
      <template #header-filter-slot-transactionDate>
        <div @click="clickDatePicker()">
          <v-text-field
            v-model="dateRangeText"
            class="base-table__header__filter__textbox date-filter"
            :append-icon="'mdi-calendar'"
            clearable
            dense
            filled
            hide-details
            :placeholder="'Initial Payment Received Date'"
            :value="dateRangeSelected ? 'Custom' : ''"
            @click:clear="dateRangeReset++"
          />
        </div>
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
              v-model="actionDropdown[index]"
              :attach="`#action-menu-${index}`"
              offset-y
              nudge-left="74"
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
                  class="actions-dropdown_item"
                  data-test="link-account-button"
                >
                  <v-list-item-subtitle
                    @click="viewDetails(index)"
                  >
                    <v-icon small>mdi-format-list-bulleted</v-icon>
                    <span class="pl-1 cursor-pointer">View Detail</span>
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
import { BaseVDataTable, DatePicker } from '..'
import { Ref, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { SessionStorageKeys, ShortNameStatus } from '@/util/constants'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { EFTShortnameResponse } from '@/models/eft-transaction'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import ShortNameLinkingDialog from '@/components/pay/eft/ShortNameLinkingDialog.vue'
import { UnlinkedShortNameState } from '@/models/pay/short-name'
import _ from 'lodash'
import { useShortNameTable } from '@/composables/short-name-table-factory'

export default defineComponent({
  name: 'UnlinkedShortNameTable',
  components: { BaseVDataTable, DatePicker, ShortNameLinkingDialog },
  emits: ['on-link-account'],
  setup (props, { emit, root }) {
    const datePicker = ref(null)
    const accountLinkingDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const accountLinkingErrorDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)
    const state = reactive<UnlinkedShortNameState>({
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
      shortNameLookupKey: 0,
      dateRangeReset: 0,
      clearFiltersTrigger: 0,
      selectedShortName: {},
      showDatePicker: false,
      dateRangeSelected: false,
      dateRangeText: '',
      accountLinkingErrorDialogTitle: '',
      accountLinkingErrorDialogText: '',
      isShortNameLinkingDialogOpen: false,
      startDate: '',
      endDate: ''
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
      depositAmount = ''
    } = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.UnlinkedShortNamesFilter) || '{}')

    const headers = [
      createHeader('shortName', 'Bank Short Name', 'text', 'Bank Short Name', shortName),
      createHeader(
        'transactionDate',
        'Initial Payment Received Date',
        'text',
        'Initial Payment Received Date',
        '',
        false,
        '260px'
      ),
      createHeader('depositAmount', 'Initial Payment Amount', 'text', 'Initial Payment Amount', depositAmount),
      {
        col: 'actions',
        hasFilter: false,
        value: 'Actions',
        minWidth: '200px'
      }
    ]

    function defaultFilterPayload () {
      return {
        shortName: '',
        transactionDate: '',
        depositAmount: '',
        state: ShortNameStatus.UNLINKED,
        transactionStartDate: '',
        transactionEndDate: ''
      }
    }

    function formatAmount (amount: number) {
      return amount ? CommonUtils.formatAmount(amount) : ''
    }

    function formatDate (date: string) {
      return date ? CommonUtils.formatDisplayDate(date, 'MMMM DD, YYYY') : ''
    }

    function openAccountLinkingDialog (item: EFTShortnameResponse) {
      state.selectedShortName = item
      state.isShortNameLinkingDialogOpen = true
    }

    function closeShortNameLinkingDialog () {
      state.selectedShortName = {}
      state.isShortNameLinkingDialogOpen = false
    }

    function resetAccountLinkingDialog () {
      state.shortNameLookupKey++
    }

    function cancelAndResetAccountLinkingDialog () {
      accountLinkingDialog.value.close()
      resetAccountLinkingDialog()
    }

    function closeAccountAlreadyLinkedDialog () {
      accountLinkingErrorDialog.value.close()
    }

    function viewDetails (index) {
      root.$router?.push({
        name: 'shortnamedetails',
        params: {
          'shortNameId': state.results[index].id.toString()
        }
      })
    }

    function setDateRangeText (startDate: string, endDate: string) {
      if (!startDate || !endDate) {
        return
      }
      return `${formatDate(startDate)} - ${formatDate(endDate)}`
    }

    async function onLinkAccount (account: any) {
      emit('on-link-account', account)
      await loadTableData()
    }

    async function updateDateRange ({ endDate, startDate }: { endDate?: string, startDate?: string }): void {
      state.showDatePicker = false
      state.dateRangeSelected = !!(endDate && startDate)
      if (!state.dateRangeSelected) { endDate = ''; startDate = '' }
      state.dateRangeText = state.dateRangeSelected ? setDateRangeText(startDate, endDate) : ''
      state.filters.filterPayload.transactionStartDate = startDate
      state.filters.filterPayload.transactionEndDate = endDate
      ConfigHelper.addToSession(SessionStorageKeys.UnlinkedShortNamesFilter, JSON.stringify(state.filters.filterPayload))
      await loadTableData()
    }

    async function clickDatePicker () {
      state.showDatePicker = true
    }

    async function clearFilters () {
      state.clearFiltersTrigger++
      state.dateRangeReset++
      state.filters.filterPayload = defaultFilterPayload()
      state.filters.isActive = false
      await loadTableData()
    }

    onMounted(async () => {
      const orgSearchFilter = ConfigHelper.getFromSession(SessionStorageKeys.UnlinkedShortNamesFilter)
      if (orgSearchFilter) {
        try {
          const payload = JSON.parse(orgSearchFilter)
          state.filters.filterPayload = payload
          if (payload.transactionStartDate) {
            state.dateRangeText = setDateRangeText(payload.transactionStartDate, payload.transactionEndDate)
          }
        } catch {
          // Silent catch
        }
      }
      await loadTableData()
    })

    watch(() => state.filters, (filters: any) => {
      ConfigHelper.addToSession(SessionStorageKeys.UnlinkedShortNamesFilter, JSON.stringify(filters.filterPayload))
    }, { deep: true })

    return {
      ...toRefs(state),
      clearFilters,
      infiniteScrollCallback,
      headers,
      updateFilter,
      formatAmount,
      formatDate,
      updateDateRange,
      onLinkAccount,
      clickDatePicker,
      accountLinkingDialog,
      accountLinkingErrorDialog,
      openAccountLinkingDialog,
      closeShortNameLinkingDialog,
      resetAccountLinkingDialog,
      cancelAndResetAccountLinkingDialog,
      closeAccountAlreadyLinkedDialog,
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

.actions-dropdown_item {
  padding: 0.5rem 1rem;
  &:hover {
    background-color: $gray1;
    color: $app-blue !important;
  }
}

#unlinked-bank-short-names {
  border: 1px solid #e9ecef
}

</style>
