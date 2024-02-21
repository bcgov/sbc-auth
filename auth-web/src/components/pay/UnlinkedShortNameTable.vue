<template>
  <div>
    <ModalDialog
      ref="accountLinkingDialog"
      max-width="720"
      :show-icon="false"
      :showCloseIcon="true"
      dialog-class="lookup-dialog"
      :title="`Linking ${state.selectedShortName.shortName} to an Account`"
      @close-dialog="resetAccountLinkingDialog"
    >
      <template #text>
        <p
          v-if="state.selectedAccount.accountId"
          class="py-4 px-6 important"
        >
          <span class="font-weight-bold">Important:</span> Once an account is linked, all payment received
          from the same short name will be applied to settle outstanding balances of
          the selected account.
        </p>
        <h4>
          Search by Account ID or Name to Link:
        </h4>
        <ShortNameLookup
          :key="state.shortNameLookupKey"
          @account="state.selectedAccount = $event"
          @reset="resetAccountLinkingDialog"
        />
      </template>
      <template #actions>
        <div class="d-flex align-center justify-center w-100 h-100 ga-3">
          <v-btn
            large
            outlined
            color="outlined"
            data-test="dialog-ok-button"
            @click="cancelAndResetAccountLinkingDialog()"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            color="primary"
            data-test="dialog-ok-button"
            @click="linkAccount()"
          >
            Link to an Account and Settle Payment
          </v-btn>
        </div>
      </template>
    </ModalDialog>
    <ModalDialog
      ref="accountLinkingErrorDialog"
      max-width="720"
      dialog-class="notify-dialog"
      :title="state.accountLinkingErrorDialogTitle"
      :text="state.accountLinkingErrorDialogText"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          data-test="dialog-ok-button"
          @click="closeAccountAlreadyLinkedDialog"
        >
          Close
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
            :placeholder="'Initial Payment Received Date'"
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
                  <v-icon>{{ state.actionDropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
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
import { Ref, defineComponent, onMounted, reactive, ref, watch } from '@vue/composition-api'
import { SessionStorageKeys, ShortNameResponseStatus, ShortNameStatus } from '@/util/constants'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { EFTShortnameResponse } from '@/models/eft-transaction'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PaymentService from '@/services/payment.services'
import ShortNameLookup from './ShortNameLookup.vue'
import { UnlinkedShortNameState } from '@/models/pay/short-name'
import _ from 'lodash'
import { useShortNameTable } from '@/composables/short-name-table-factory'

export default defineComponent({
  name: 'UnlinkedShortNameTable',
  components: { BaseVDataTable, DatePicker, ModalDialog, ShortNameLookup },
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
      selectedAccount: {},
      showDatePicker: false,
      dateRangeSelected: false,
      dateRangeText: '',
      accountLinkingErrorDialogTitle: '',
      accountLinkingErrorDialogText: ''
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
      accountLinkingDialog.value.open()
    }

    function resetAccountLinkingDialog () {
      state.selectedAccount = {}
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
          'shortNameId': state.results[index].id
        }
      })
    }

    function setDateRangeText (startDate: string, endDate: string) {
      if (!startDate || !endDate) {
        return
      }
      return `${formatDate(startDate)} - ${formatDate(endDate)}`
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

    async function linkAccount () {
      if (!state.selectedShortName?.id || !state.selectedAccount?.accountId) {
        return
      }
      try {
        const response = await PaymentService.patchEFTShortname(state.selectedShortName.id, state.selectedAccount.accountId)
        if (response?.data) {
          emit('on-link-account', response.data)
          cancelAndResetAccountLinkingDialog()
          await loadTableData()
        }
      } catch (error) {
        if (error.response.data.type === ShortNameResponseStatus.EFT_SHORT_NAME_ALREADY_MAPPED) {
          state.accountLinkingErrorDialogTitle = 'Account Already Linked'
          state.accountLinkingErrorDialogText = 'The selected bank short name is already linked to an account.'
          cancelAndResetAccountLinkingDialog()
          accountLinkingErrorDialog.value.open()
        } else {
          state.accountLinkingErrorDialogTitle = 'Something Went Wrong'
          state.accountLinkingErrorDialogText = 'An error occurred while linking the bank short name to an account.'
          cancelAndResetAccountLinkingDialog()
          accountLinkingErrorDialog.value.open()
        }
        console.error('Failed to patchEFTShortname.', error)
      }
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
      accountLinkingErrorDialog,
      openAccountLinkingDialog,
      resetAccountLinkingDialog,
      cancelAndResetAccountLinkingDialog,
      closeAccountAlreadyLinkedDialog,
      datePicker,
      viewDetails,
      linkAccount
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/ShortnameTables.scss';
// @import '@/assets/scss/overrides';

.actions-dropdown_item {
  cursor: pointer;
  padding: 0.5rem 1rem;
  &:hover {
    background-color: $gray1;
    color: $app-blue !important;
  }
}

h4 {
  color: black;
}

#unlinked-bank-short-names {
  border: 1px solid #e9ecef
}

.important {
  background-color: #fff7e3;
  border: 2px solid #fcba19;
  color: #495057;
  font-size: 12px;
}

.w-100 {
  width: 100%;
}

.h-100 {
  height: 100%;
}

.ga-3 {
  gap: 12px;
}

::v-deep {
  .v-btn.v-btn--outlined {
      border-color: var(--v-primary-base);
      color: var(--v-primary-base);
  }
}

</style>
