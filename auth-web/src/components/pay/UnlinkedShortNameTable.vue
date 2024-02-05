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
          Linking to an Account
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
            @click="closeSettings"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
      </template>
      <template #text>
        <h4>
          Search by Account ID or Name to Link:
        </h4>
        <v-text-field
          v-model="accountSearch"
          filled
          label="Account ID or Account Name"
          persistent-hint
          autocomplete="off"
          type="text"
          maxlength="50"
          class="passcode mt-0 mb-2"
          aria-label="Account ID or Account Name"
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
      v-show="showDatePicker"
      ref="datePicker"
      :reset="dateRangeReset"
      class="date-picker"
      @submit="updateDateRange($event)"
    />
    <BaseVDataTable
      id="linked-bank-short-names"
      :clearFiltersTrigger="clearFiltersTrigger"
      itemKey="id"
      :loading="false"
      loadingText="Loading Unlinked Bank Short Names..."
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
      <template #header-filter-slot-depositDate>
        <div @click="clickDatePicker()">
          <v-text-field
            class="base-table__header__filter__textbox date-filter"
            :append-icon="'mdi-calendar'"
            clearable
            dense
            filled
            hide-details
            :placeholder="'Date'"
            :value="dateRangeSelected ? 'Custom' : ''"
            @click:clear="dateRangeReset++"
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
      <template #item-slot-depositDate="{ item }">
        <span>{{ formatDate(item.depositDate) }}</span>
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
            @click="openAccountLinkingDialog(item)"
          >
            Link to Account
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
import { BaseVDataTable, DatePicker } from '..'
import { Ref, computed, defineComponent, nextTick, onMounted, reactive, ref } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { DataOptions } from 'vuetify'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'
import { UnlinkedShortNameFilterParams } from '@/models/pay/shortname'
import _ from 'lodash'
import moment from 'moment'

export default defineComponent({
  name: 'UnlinkedShortNameTable',
  components: { BaseVDataTable, DatePicker, ModalDialog },
  setup (props, { emit }) {
    const datePicker = ref(null)
    const dateRangeReset = ref(0)
    const showDatePicker = ref(false)
    const dateRangeSelected = ref(false)
    const clearFiltersTrigger = ref(0)
    const accountSearch = ref('')
    const actionDropdown: Ref<boolean[]> = ref([])
    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)
    const accountLinkingDialog: Ref<InstanceType<typeof ModalDialog>> = ref(null)

    const createHeader = (col, label, type, value, hasFilter = true, minWidth = '125px') => ({
      col,
      customFilter: {
        filterApiFn: hasFilter ? (val: any) => loadTableData(col, val || '') : null,
        clearable: true,
        label,
        type,
        value
      },
      hasFilter,
      minWidth,
      value
    })

    const headers = [
      createHeader('shortName', 'Bank Short Name', 'text', 'Bank Short Name'),
      // createHeader('depositDate', 'Initial Payment Received Date', 'text', ''),
      {
        col: 'depositDate',
        hasFilter: false,
        label: 'Initial Payment Received Date',
        itemFn: (val: any) => {
          // Example format: 2023-03-11T00:55:05.909229 without timezone
          const createdOn = moment.utc().toDate()
          return CommonUtils.formatDisplayDate(createdOn, 'MMMM DD, YYYY<br/>h:mm A')
        },
        value: 'Initial Payment Received Date',
        minWidth: '165px'
      },
      createHeader('depositAmount', 'Initial Payment Amount', 'text', 'Initial Payment Amount'),
      {
        col: 'actions',
        hasFilter: false,
        value: 'Actions',
        minWidth: '200px'
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
          shortName: '',
          depositDate: '',
          depositAmount: ''
        }
      } as UnlinkedShortNameFilterParams,
      loading: false
    })

    const title = computed(() => {
      return `Unlinked Bank Short Names (${state.totalResults})`
    })

    onMounted(async () => {
      headers.forEach((header) => {
        if (header.hasFilter) {
          (header.customFilter as any).filterApiFn = (val: any) => loadTableData(header.col, val || '')
        }
      })
      await loadTableData()
    })

    function formatAmount (amount: number) {
      return CommonUtils.formatAmount(amount)
    }

    function formatDate (date: string) {
      return CommonUtils.formatCurrentDate(date)
    }

    async function clickDatePicker () {
      showDatePicker.value = true
      // await for datePicker ref to update
      await nextTick()
      // datePicker.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function updateDateRange ({ endDate, startDate }: { endDate?: string, startDate?: string }): void {
      showDatePicker.value = false
      dateRangeSelected.value = !!(endDate && startDate)
      if (!dateRangeSelected.value) { endDate = ''; startDate = '' }
      // loadTableData('depositDate', { endDate, startDate })
      loadTableData('depositDate', endDate)
    }

    function handleFilters (filterField?: string, value?: any): void {
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
    }

    // This is also called inside of the HeaderFilter component inside of the BaseVDataTable component
    async function loadTableData (filterField?: string, value?: any, appendToResults = false): Promise<void> {
      handleFilters(filterField, value)
      try {
        const response = await PaymentService.getEFTShortNames(state.filters, 'UNLINKED')
        if (response?.data) {
          /* We use appendToResults for infinite scroll, so we keep the existing results. */
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

    function openAccountLinkingDialog (item: any) {
      accountLinkingDialog.value.open()
    }

    function closeAccountLinkingDialog () {
      accountLinkingDialog.value.close()
    }

    async function clearFilters () {
      clearFiltersTrigger.value++
      dateRangeReset.value++
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

    async function infiniteScrollCallback () {
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
      updateFilter,
      formatAmount,
      formatDate,
      updateDateRange,
      showDatePicker,
      dateRangeReset,
      clickDatePicker,
      dateRangeSelected,
      accountLinkingDialog,
      openAccountLinkingDialog,
      closeAccountLinkingDialog,
      datePicker
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';

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
