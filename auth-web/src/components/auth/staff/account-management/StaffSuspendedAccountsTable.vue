<template>
  <div>
    <DatePicker
      v-show="showDatePicker"
      ref="datePicker"
      :reset="dateRangeReset"
      :setEndDate="searchParams.suspendedDateTo"
      :setStartDate="searchParams.suspendedDateFrom"
      @submit="updateDateRange($event)"
    />
    <v-form class="datatable-search account-suspended-search">
      <v-data-table
        class="account-list"
        :headers="headerAccounts"
        :items="suspendedOrgs"
        :no-data-text="$t('noActiveAccountsLabel')"
        :options.sync="tableDataOptions"
        :disable-sort="true"
        :footer-props="{
          itemsPerPageOptions: getPaginationOptions()
        }"
        :loading="isTableLoading"
        :server-items-length="totalAccountsCount"
        hide-default-header
        fixed-header
        @update:items-per-page="saveItemsPerPage"
      >
        <template #loading>
          <div class="py-8 loading-datatable">
            Loading items...
          </div>
        </template>

        <template #no-data>
          <div class="py-8 no-data">
            <div v-html="noDataMessage" />
          </div>
        </template>

        <template #header="{}">
          <thead class="v-data-table-header">
            <tr class="header-row-1">
              <th
                v-for="(header, i) in headerAccounts"
                :key="getIndexedTag('find-header-row', i)"
                :scope="getIndexedTag('find-header-col', i)"
                class="font-weight-bold"
              >
                {{ header.text }}
              </th>
            </tr>

            <tr class="header-row-2">
              <th
                v-for="(header, i) in headerAccounts"
                :key="getIndexedTag('find-header-row2', i)"
                :scope="getIndexedTag('find-header-col2', i)"
              >
                <v-text-field
                  v-if="['name', 'id', 'decisionMadeBy'].includes(header.value)"
                  :id="header.value"
                  v-model.trim="searchParams[header.value]"
                  input
                  type="search"
                  autocomplete="off"
                  class="text-input-style"
                  filled
                  :placeholder="getHeaderPlaceHolderText(header)"
                  dense
                  hide-details="auto"
                />

                <div
                  v-else-if="header.value === 'suspendedOn'"
                  class="date-filter-wrapper"
                  @click="showDatePicker = true"
                >
                  <v-text-field
                    v-model="dateTxt"
                    class="text-input-style"
                    dense
                    filled
                    hide-details="auto"
                    :placeholder="header.text"
                  >
                    <template #append>
                      <v-icon>
                        mdi-calendar
                      </v-icon>
                    </template>
                  </v-text-field>
                </div>

                <div
                  v-else-if="header.value === 'statusCode'"
                  class="mt-0"
                >
                  <v-select
                    v-model="searchParams.suspensionReasonCode"
                    :items="suspensionReasonOptions"
                    filled
                    item-text="desc"
                    item-value="code"
                    data-test="select-reason"
                    hide-details="auto"
                  />
                </div>

                <v-btn
                  v-else-if="searchParamsExist && header.value === 'action'"
                  outlined
                  color="primary"
                  class="action-btn clear-filter-button"
                  @click="clearSearchParams()"
                >
                  <span class="clear-filter cursor-pointer">
                    Clear Filters
                    <v-icon
                      small
                      color="primary"
                    >mdi-close</v-icon>
                  </span>
                </v-btn>
              </th>
            </tr>
          </thead>
        </template>

        <template #[`item.id`]="{ item }">
          {{ item.id || 'N/A' }}
        </template>
        <template #[`item.statusCode`]="{ item }">
          {{ getStatusText(item) }}
        </template>
        <template #[`item.suspendedOn`]="{ item }">
          {{ formatDate(item.suspendedOn) }}
        </template>
        <template #[`item.decisionMadeBy`]="{ item }">
          {{ item.decisionMadeBy ? item.decisionMadeBy : 'N/A' }}
        </template>
        <template #[`item.action`]="{ item }">
          <v-btn
            outlined
            color="primary"
            class="action-btn"
            :data-test="getIndexedTag('view-account-button', item.id)"
            @click="view(item)"
          >
            View
          </v-btn>
        </template>
      </v-data-table>
    </v-form>
  </div>
</template>

<script lang="ts">
import { AccountStatus, SessionStorageKeys, SuspensionReason, SuspensionReasonCode } from '@/util/constants'
import {
  DEFAULT_DATA_OPTIONS,
  cachePageInfo,
  getAndPruneCachedPageInfo,
  getPaginationOptions,
  hasCachedPageInfo,
  numberOfItems,
  saveItemsPerPage as saveItemsPerPageUtil
} from '@/components/datatable/resources'
import { OrgAccountTypes, Organization } from '@/models/Organization'
import { computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { getAccountTypeFromOrgAndAccessType, getOrgAndAccessTypeFromAccountType } from '@/util/account-type-utils'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { DatePicker } from '@/components'
import debounce from '@/util/debounce'
import moment from 'moment'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores/org'
import { useStaffStore } from '@/stores/staff'

export default defineComponent({
  name: 'StaffSuspendedAccountsTable',
  components: {
    DatePicker
  },
  setup (props, { root }) {
    const orgStore = useOrgStore()
    const staffStore = useStaffStore()
    const codesStore = useCodesStore()

    const headerAccounts = [
      {
        text: 'Name',
        align: 'left',
        sortable: false,
        value: 'name'
      },
      {
        text: 'Account Number',
        align: 'left',
        sortable: false,
        value: 'id'
      },
      {
        text: 'Reason',
        align: 'left',
        sortable: false,
        value: 'statusCode'
      },
      {
        text: 'Suspended by',
        align: 'left',
        sortable: false,
        value: 'decisionMadeBy'
      },
      {
        text: 'Date Suspended',
        align: 'left',
        sortable: false,
        value: 'suspendedOn'
      },
      {
        text: 'Actions',
        align: 'left',
        value: 'action',
        sortable: false,
        width: '90'
      }
    ]

    const state = reactive({
      totalAccountsCount: 0,
      tableDataOptions: {} as Partial<DataOptions>,
      isTableLoading: false,
      suspendedOrgs: [] as Organization[],
      searchParams: {
        name: '',
        id: '',
        decisionMadeBy: '',
        orgType: OrgAccountTypes.ALL,
        suspendedDateFrom: '',
        suspendedDateTo: '',
        suspensionReasonCode: '',
        statuses: [AccountStatus.NSF_SUSPENDED, AccountStatus.SUSPENDED]
      } as any,
      accountTypes: [
        { code: OrgAccountTypes.ALL, description: 'All' },
        { code: OrgAccountTypes.PREMIUM, description: 'Premium' },
        { code: OrgAccountTypes.PREMIUM_OUT_OF_PROVINCE, description: 'Premium (out-of-province)' },
        { code: OrgAccountTypes.GOVM, description: 'GovM' },
        { code: OrgAccountTypes.GOVN, description: 'GovN' },
        // Remove this when API is ready
        { code: OrgAccountTypes.DIRECTOR_SEARCH, description: 'Director Search' },
        { code: OrgAccountTypes.STAFF, description: 'BC Registries Staff' },
        { code: OrgAccountTypes.SBC_STAFF, description: 'Service BC Staff' },
        { code: OrgAccountTypes.MAXIMUS_STAFF, description: 'Maximus Staff' }
      ],
      dateTxt: '',
      showDatePicker: false,
      dateRangeReset: 1
    })

    const formatDate = CommonUtils.formatDisplayDate

    const getIndexedTag = (tag: string, index: number): string => {
      return `${tag}-${index}`
    }

    const searchParamsExist = computed(() => {
      return (state.searchParams.name && state.searchParams.name.length > 0) ||
        (state.searchParams.id && state.searchParams.id.length > 0) ||
        (state.searchParams.decisionMadeBy && state.searchParams.decisionMadeBy.length > 0) ||
        (state.searchParams.orgType && state.searchParams.orgType !== OrgAccountTypes.ALL) ||
        (state.searchParams.suspendedDateFrom && state.searchParams.suspendedDateFrom.length > 0) ||
        (state.searchParams.suspendedDateTo && state.searchParams.suspendedDateTo.length > 0) ||
        (state.searchParams.suspensionReasonCode && state.searchParams.suspensionReasonCode.length > 0)
    })

    const suspensionReasonOptions = computed(() => {
      const options = [{ desc: 'All', code: '' }]
      if (codesStore.suspensionReasonCodes && codesStore.suspensionReasonCodes.length > 0) {
        return options.concat(codesStore.suspensionReasonCodes.map(code => ({ desc: code.desc, code: code.code })))
      }
      return options
    })

    const noDataMessage = computed(() => {
      return searchParamsExist.value
        ? root.$t('searchAccountNoResult') as string
        : root.$t('searchAccountStartMessage') as string
    })

    const getHeaderPlaceHolderText = (header: any): string => {
      return header.text
    }

    const getOrgs = async (page: number = 1, pageLimit: number = numberOfItems(SessionStorageKeys.PaginationNumberOfItems)) => {
      try {
        state.isTableLoading = true
        const completeSearchParams: any = {
          ...state.searchParams,
          orgType: undefined,
          accessType: undefined,
          ...getOrgAndAccessTypeFromAccountType(state.searchParams.orgType),
          page: page,
          limit: pageLimit
        }
        if (state.searchParams.orgType === OrgAccountTypes.ALL) {
          delete completeSearchParams.orgType
          delete completeSearchParams.accessType
        }
        const isEmpty = (value: string) => !value || value === ''
        if (isEmpty(state.searchParams.suspensionReasonCode)) {
          delete completeSearchParams.suspensionReasonCode
        }
        if (isEmpty(state.searchParams.id)) {
          delete completeSearchParams.id
        }
        if (isEmpty(state.searchParams.suspendedDateFrom)) {
          delete completeSearchParams.suspendedDateFrom
        }
        if (isEmpty(state.searchParams.suspendedDateTo)) {
          delete completeSearchParams.suspendedDateTo
        }
        const activeAccountsResp: any = await staffStore.searchOrgs(completeSearchParams)
        state.suspendedOrgs = activeAccountsResp?.orgs || []
        state.totalAccountsCount = activeAccountsResp?.total || 0
        if (!activeAccountsResp?.orgs) {
          console.warn('No orgs in response:', activeAccountsResp)
        }
      } catch (error) {
        state.isTableLoading = false
        console.error(error)
      } finally {
        state.isTableLoading = false
      }
    }

    const debouncedOrgSearch = debounce(async (page = 1, pageLimit = state.tableDataOptions.itemsPerPage) => {
      await getOrgs(page, pageLimit)
    })

    const clearSearchParams = () => {
      state.dateTxt = ''
      state.dateRangeReset++
      Object.assign(state.searchParams, {
        name: '',
        id: '',
        decisionMadeBy: '',
        orgType: OrgAccountTypes.ALL,
        suspendedDateFrom: '',
        suspendedDateTo: '',
        suspensionReasonCode: '',
        statuses: [AccountStatus.NSF_SUSPENDED, AccountStatus.SUSPENDED]
      })
    }

    const formatDateRange = (startDate: string, endDate: string): string => {
      return `${moment(startDate).format('MMM DD, YYYY')} - ${moment(endDate).format('MMM DD, YYYY')}`
    }

    const updateDateRange = (event: any) => {
      if (event.endDate && event.startDate) {
        state.dateTxt = formatDateRange(event.startDate, event.endDate)
      } else {
        state.dateTxt = ''
      }

      state.searchParams.suspendedDateFrom = event.startDate
      state.searchParams.suspendedDateTo = event.endDate
      state.showDatePicker = false
    }

    const setSearchFilterToStorage = (val: string): void => {
      ConfigHelper.addToSession(SessionStorageKeys.SuspendedAccountsSearchFilter, val)
    }

    const view = async (org: Organization) => {
      cachePageInfo(state.tableDataOptions, SessionStorageKeys.PaginationOptions)
      const orgId: number = org.id
      await orgStore.syncOrganization(orgId)
      await orgStore.addOrgSettings(org)
      await orgStore.syncMembership(orgId)
      root.$router.push(`/account/${orgId}/settings`)
    }

    const getSuspensionReasonCode = (org: Organization): string => {
      return codesStore.suspensionReasonCodes?.find(suspensionReasonCode =>
        suspensionReasonCode?.code === org?.suspensionReasonCode)?.desc || ''
    }

    const getStatusText = (org: Organization) => {
      if (org.statusCode === AccountStatus.NSF_SUSPENDED) {
        return org.suspensionReasonCode === SuspensionReasonCode.OVERDUE_EFT ? SuspensionReason.OVERDUE_EFT : SuspensionReason.NSF
      }
      return org.statusCode === AccountStatus.SUSPENDED
        ? getSuspensionReasonCode(org)
        : org.statusCode
    }

    const saveItemsPerPage = (val: number): void => {
      saveItemsPerPageUtil(val, SessionStorageKeys.PaginationNumberOfItems)
    }

    let isInitialized = false

    watch(() => state.tableDataOptions, async (val) => {
      if (isInitialized && val?.page && val?.itemsPerPage) {
        await getOrgs(val.page, val.itemsPerPage)
      }
    }, { deep: true })

    watch(() => state.searchParams, () => {
      if (isInitialized) {
        state.tableDataOptions = { ...state.tableDataOptions, page: 1 }
        setSearchFilterToStorage(JSON.stringify(state.searchParams))
        debouncedOrgSearch()
      }
    }, { deep: true })

    onMounted(async () => {
      const orgSearchFilter = ConfigHelper.getFromSession(SessionStorageKeys.SuspendedAccountsSearchFilter) || ''
      try {
        const parsed = JSON.parse(orgSearchFilter)
        if (parsed) {
          Object.assign(state.searchParams, parsed)
        }
        if (state.searchParams.suspendedDateFrom && state.searchParams.suspendedDateTo) {
          state.dateTxt = formatDateRange(state.searchParams.suspendedDateFrom, state.searchParams.suspendedDateTo)
        }
      } catch {
        console.warn('Error parsing org search filter from session:', orgSearchFilter)
      }

      const initialTableOptions = {
        ...DEFAULT_DATA_OPTIONS,
        itemsPerPage: numberOfItems(SessionStorageKeys.PaginationNumberOfItems)
      }
      if (hasCachedPageInfo(SessionStorageKeys.PaginationOptions)) {
        const cached = getAndPruneCachedPageInfo(SessionStorageKeys.PaginationOptions)
        if (cached) {
          Object.assign(initialTableOptions, cached)
        }
      }

      state.tableDataOptions = initialTableOptions
      await getOrgs(initialTableOptions.page || 1, initialTableOptions.itemsPerPage || numberOfItems(SessionStorageKeys.PaginationNumberOfItems))
      isInitialized = true
    })

    return {
      ...toRefs(state),
      headerAccounts,
      formatDate,
      searchParamsExist,
      suspensionReasonOptions,
      noDataMessage,
      getIndexedTag,
      getHeaderPlaceHolderText,
      clearSearchParams,
      updateDateRange,
      view,
      getStatusText,
      getAccountTypeFromOrgAndAccessType,
      saveItemsPerPage,
      getPaginationOptions
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/search.scss';

.account-suspended-search {
  table > thead > tr > th {
    width: 210px !important;
    min-width: 210px !important;
  }

  ::v-deep table {
    border-collapse: separate;
    border-spacing: 0;
  }

  ::v-deep table th,
  ::v-deep table td {
    border-right: none !important;
    border-left: none !important;
  }

  .header-row-1 {
    th {
      font-size: 14px;
      font-weight: bold !important;
      padding: 18px 3px 18px 3px !important;
      border-bottom: thin solid rgba(0, 0, 0, 0.12);
      border-right: none !important;
      border-left: none !important;
    }

    th:first-child {
      padding-left: 14px !important;
    }

    th:last-child {
      padding-right: 20px !important;
    }
  }

  .header-row-2 {
    th {
      padding: 18px 3px 18px 3px !important;
      border-bottom: thin solid rgba(0, 0, 0, 0.12);
      border-right: none !important;
      border-left: none !important;
      vertical-align: top !important;
    }

    th:first-child {
      padding-left: 14px !important;
    }

    .v-text-field,
    .v-select {
      margin: 0 !important;
      padding: 0 !important;
    }

    .v-text-field .v-input__control,
    .v-select .v-input__control {
      padding: 0 !important;
      margin: 0 !important;
      min-height: auto !important;
    }

    .v-text-field .v-input__control .v-input__slot,
    .v-select .v-input__control .v-input__slot {
      min-height: auto !important;
      height: 28px !important;
      margin: 0 !important;
      padding: 0 8px !important;
      background-color: transparent !important;
      border: none !important;
      border-bottom: thin solid rgba(0, 0, 0, 0.12) !important;
      border-radius: 0 !important;
      box-shadow: none !important;
    }

    .v-text-field--filled .v-input__control,
    .v-select--filled .v-input__control {
      padding-top: 0 !important;
      margin-top: 0 !important;
    }

    .v-text-field--filled .v-input__slot::before,
    .v-select--filled .v-input__slot::before {
      display: none !important;
    }

    .v-text-field--filled .v-input__slot::after,
    .v-select--filled .v-input__slot::after {
      display: none !important;
    }

    .v-text-field input {
      padding: 0 !important;
      font-size: 14px !important;
      height: 28px !important;
      line-height: 28px !important;
    }

    .v-select .v-select__selection {
      margin: 0 !important;
      padding: 0 !important;
      font-size: 14px !important;
      line-height: 28px !important;
    }

    .v-text-field .v-input__append-inner,
    .v-text-field .v-input__append-outer {
      margin-top: 0 !important;
      padding-top: 0 !important;
      align-self: center !important;
    }

    .date-filter-wrapper {
      margin: 0 !important;
      padding: 0 !important;

      .v-text-field {
        margin: 0 !important;
        padding: 0 !important;
      }

      .v-input__control {
        margin: 0 !important;
        padding: 0 !important;
        min-height: auto !important;
      }

      .v-input__slot {
        margin: 0 !important;
        height: 28px !important;
        padding: 0 8px !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: thin solid rgba(0, 0, 0, 0.12) !important;
        border-radius: 0 !important;
        box-shadow: none !important;
      }

      .v-text-field--filled .v-input__slot::before,
      .v-text-field--filled .v-input__slot::after {
        display: none !important;
      }

      input {
        padding: 0 !important;
        font-size: 14px !important;
        height: 28px !important;
        line-height: 28px !important;
      }

      .v-input__append-inner {
        margin-top: 0 !important;
        padding-top: 0 !important;
        align-self: center !important;
      }
    }

    th:last-child {
      padding-right: 14px !important;
      background: white !important;
    }
  }

  .clear-filter-button {
    margin-top: 2px;
    padding: 7px 12px !important;
    min-width: auto !important;
    white-space: nowrap !important;
    width: auto !important;
  }

  .clear-filter {
    line-height: 1.5;
    white-space: nowrap;
  }

  ::v-deep input, ::v-deep .v-select__selection {
    color:#212529 !important;
  }

  ::v-deep ::placeholder{
    color:#495057 !important;
  }

  .v-data-table th {
    font-size: 0.75rem;
  }

  ::v-deep .v-data-footer {
    min-width: 100%;
  }

  .no-data, .loading-datatable {
    border: 0px;
    position: sticky;
    width: 1230px;
    left: 0;
    flex-grow: 0;
    flex-shrink: 0;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar {
    width: .625rem;
    height: 0.50rem;
    overflow-x: hidden;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-track {
    overflow: auto;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-thumb {
    border-radius: 5px;
    background-color: lightgray;
  }

  table > thead > tr > th:last-child {
    width: auto !important;
    min-width: 90px !important;
    padding-right: 14px !important;
  }

  ::v-deep tr:hover td:last-child {
    background-color: inherit !important;
  }

  table > thead > tr > th:last-child,
  ::v-deep table > tbody > tr > td:last-child:not([colspan]) {
    position: sticky !important;
    position: -webkit-sticky !important;
    right: 0;
    z-index: 1;
    background: white;
    text-align: right !important;
  }

  ::v-deep table > tbody > tr > td {
    border: 0px;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
    vertical-align: text-top;
  }

  ::v-deep table > tbody > tr > td:last-child:not([colspan]) {
    padding-left: 3px !important;
    padding-right: 3px !important;
  }
}

.account-list{
  &__status {
      display: flex;
      justify-content: center;
      max-width: 75%;
  }
  .action-btn {
    width: 5rem;
  }
}

</style>
