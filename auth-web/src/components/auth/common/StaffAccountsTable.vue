<template>
  <div>
    <v-form class="fas-search account-active-search">
      <v-row
        dense
        class="row-margin"
      >
        <v-col
          sm="12"
          cols="6"
        >
          <transition name="slide-fade">
            <v-data-table
              :headers="headerAccounts"
              :items="activeOrgs"
              :server-items-length="totalAccountsCount"
              :options.sync="tableDataOptions"
              :disable-sort="true"
              :footer-props="{
                itemsPerPageOptions: paginationOptions
              }"
              :items-per-page="numOfItems"
              hide-default-header
              fixed-header
              :loading="isTableLoading"
              :mobile-breakpoint="0"
              @update:items-per-page="saveItemsPerPage"
            >
              <!-- Loading -->
              <template #loading>
                <div
                  class="py-8 loading-datatable"
                >
                  Loading items...
                </div>
              </template>

              <!-- No data -->
              <template #no-data>
                <div
                  v-sanitize="noDataMessage"
                  class="py-8 no-data"
                />
              </template>

              <!-- Headers (two rows) -->
              <template #header="{}">
                <thead class="v-data-table-header">
                  <!-- First row has titles. -->
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

                  <!-- Second row has search boxes. -->
                  <tr class="header-row-2 mt-2 px-2">
                    <th
                      v-for="(header, i) in headerAccounts"
                      :key="getIndexedTag('find-header-row2', i)"
                      :scope="getIndexedTag('find-header-col2', i)"
                    >
                      <v-text-field
                        v-if="!['orgType','action'].includes(header.value)"
                        :id="header.value"
                        v-model.trim="searchParams[header.value]"
                        input
                        type="search"
                        autocomplete="off"
                        class="text-input-style"
                        filled
                        :placeholder="header.text"
                        dense
                        hide-details="auto"
                      />

                      <div
                        v-else-if="['orgType'].includes(header.value)"
                        class="mt-0"
                      >
                        <v-select
                          v-model="searchParams[header.value]"
                          :items="accountTypes"
                          filled
                          item-text="description"
                          item-value="code"
                          return-object
                          data-test="select-status"
                          v-bind="$attrs"
                          hide-details="auto"
                          v-on="$listeners"
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

              <template #[`item.orgType`]="{ item }">
                {{ getAccountTypeFromOrgAndAccessType(item) }}
              </template>
              <template #[`item.decisionMadeBy`]="{ item }">
                {{ item.decisionMadeBy ? item.decisionMadeBy : 'N/A' }}
              </template>

              <!-- Item Actions -->
              <template #[`item.action`]="{ item }">
                <div class="actions text-right">
                  <span class="open-action">
                    <v-btn
                      color="primary"
                      :class="['open-action-btn', { active: isActiveAccounts }]"
                      :data-test="getIndexedTag('view-account-button', item.id)"
                      @click="view(item)"
                    >
                      View
                    </v-btn>
                  </span>

                  <!-- More Actions Menu -->
                  <span
                    v-if="isActiveAccounts"
                    class="more-actions"
                  >
                    <v-menu
                      v-model="dropdown[item.id]"
                      offset-y
                      nudge-left="212"
                    >
                      <template #activator="{ on }">
                        <v-btn
                          color="primary"
                          class="more-actions-btn"
                          v-on="on"
                        >
                          <v-icon>{{ dropdown[item.id] ? 'mdi-menu-up' : 'mdi-menu-down' }}</v-icon>
                        </v-btn>
                      </template>
                      <v-list>
                        <v-list-item @click="viewInBusinessRegistryDashboard(item)">
                          <v-list-item-subtitle>
                            <v-icon style="font-size: 14px">mdi-view-dashboard</v-icon>
                            <span class="pl-2">Business Registry Dashboard</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item @click="view(item)">
                          <v-list-item-subtitle>
                            <v-icon style="font-size: 14px">mdi-account</v-icon>
                            <span class="pl-2">Manage Account</span>
                          </v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-menu>
                  </span>
                </div>
              </template>
            </v-data-table>
          </transition>
        </v-col>
      </v-row>
    </v-form>
  </div>
</template>

<script lang="ts">
import { AccessType, Account, AccountStatus, SessionStorageKeys } from '@/util/constants'
import {
  DEFAULT_DATA_OPTIONS,
  cachePageInfo,
  getAndPruneCachedPageInfo,
  getPaginationOptions,
  hasCachedPageInfo,
  numberOfItems,
  saveItemsPerPage
} from '@/components/datatable/resources'
import { OrgAccountTypes, OrgFilterParams, OrgMap, Organization } from '@/models/Organization'
import { PropType, computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { EnumDictionary } from '@/models/util'
import debounce from '@/util/debounce'
import { useI18n } from 'vue-i18n-composable'
import { useOrgStore } from '@/stores/org'
import { useStaffStore } from '@/stores/staff'

export default defineComponent({
  name: 'StaffAccountsTable',
  props: {
    accountStatus: {
      type: String as PropType<AccountStatus>,
      default: AccountStatus.ACTIVE
    }
  },
  setup (props, { root }) {
    const { t } = useI18n()
    const orgStore = useOrgStore()
    const staffStore = useStaffStore()

    const state = reactive({
      activeOrgs: [] as Organization[],
      headerAccounts: [
        { text: 'Account Name', value: 'name' },
        { text: 'Branch Name', value: 'branchName' },
        { text: 'Account Number', value: 'id' },
        { text: 'BCOL Account Number', value: 'bcolAccountId' },
        { text: 'Approved By', value: 'decisionMadeBy' },
        { text: 'Account Type', value: 'orgType' },
        { text: 'Actions', value: 'action' }
      ],
      accountTypeMap: {
        [OrgAccountTypes.ALL]: {},
        [OrgAccountTypes.BASIC]: {
          accessType: [AccessType.REGULAR, AccessType.REGULAR_BCEID],
          orgType: Account.BASIC
        },
        [OrgAccountTypes.BASIC_OUT_OF_PROVINCE]: {
          accessType: [AccessType.EXTRA_PROVINCIAL],
          orgType: Account.BASIC
        },
        [OrgAccountTypes.PREMIUM]: {
          accessType: [AccessType.REGULAR, AccessType.REGULAR_BCEID],
          orgType: Account.PREMIUM
        },
        [OrgAccountTypes.PREMIUM_OUT_OF_PROVINCE]: {
          accessType: [AccessType.EXTRA_PROVINCIAL],
          orgType: Account.PREMIUM
        },
        [OrgAccountTypes.GOVM]: {
          accessType: [AccessType.GOVM]
        },
        [OrgAccountTypes.GOVN]: {
          accessType: [AccessType.GOVN]
        },
        [OrgAccountTypes.DIRECTOR_SEARCH]: {
          accessType: [AccessType.ANONYMOUS]
        },
        [OrgAccountTypes.STAFF]: {
          accessType: [AccessType.GOVM],
          orgType: Account.STAFF
        },
        [OrgAccountTypes.SBC_STAFF]: {
          accessType: [AccessType.GOVM],
          orgType: Account.SBC_STAFF
        }
      } as EnumDictionary<OrgAccountTypes, OrgMap>,
      accountTypes: [] as string[],
      formatDate: CommonUtils.formatDisplayDate,
      totalAccountsCount: 0,
      tableDataOptions: {} as Partial<DataOptions>,
      isTableLoading: false,
      searchParamsExist: false,
      dropdown: [] as Array<boolean>,
      searchParams: {
        name: '',
        branchName: '',
        id: '',
        bcolAccountId: '',
        decisionMadeBy: '',
        orgType: OrgAccountTypes.ALL,
        statuses: [props.accountStatus]
      } as OrgFilterParams
    })

    state.accountTypes = Array.from(Object.keys(state.accountTypeMap))
    const paginationOptions = computed(() => getPaginationOptions())
    const numOfItems = computed(() => numberOfItems())

    const debouncedOrgSearch = debounce(async function (page = 1, pageLimit = numOfItems.value) {
      try {
        state.isTableLoading = true
        const completeSearchParams: OrgFilterParams = {
          ...state.searchParams,
          orgType: undefined,
          accessType: undefined,
          ...getOrgAndAccessTypeFromAccountType(state.searchParams.orgType),
          page: page,
          limit: pageLimit
        }
        const activeAccountsResp = await staffStore.searchOrgs(completeSearchParams)
        state.activeOrgs = activeAccountsResp.orgs
        state.totalAccountsCount = activeAccountsResp?.total || 0
      } catch (error) {
        console.error(error)
      } finally {
        state.isTableLoading = false
      }
    })

    function mounted () {
      state.tableDataOptions = DEFAULT_DATA_OPTIONS
      const orgSearchFilter = ConfigHelper.getFromSession(SessionStorageKeys.OrgSearchFilter) || ''
      try {
        state.searchParams = JSON.parse(orgSearchFilter)
      } catch {
        // Do nothing, we have defaults for searchParams.
      }
      if (hasCachedPageInfo) {
        state.tableDataOptions = getAndPruneCachedPageInfo()
      }
    }

    watch(() => state.searchParams, function (value) {
      state.searchParamsExist = doSearchParametersExist(value)
      state.tableDataOptions = { ...getAndPruneCachedPageInfo(), page: 1 }
      setSearchFilterToStorage(JSON.stringify(value))
      debouncedOrgSearch()
    }, { deep: true })

    watch(() => state.tableDataOptions, function (val) {
      debouncedOrgSearch(val?.page, val?.itemsPerPage)
    }, { deep: true })

    async function viewInBusinessRegistryDashboard (org: Organization) {
      await syncBeforeNavigate(org)
      root.$router.push(`/account/${org.id}/business`)
    }

    async function view (org: Organization) {
      await syncBeforeNavigate(org)
      root.$router.push(`/account/${org.id}/settings`)
    }

    function clearSearchParams () {
      state.searchParams = {
        name: '',
        branchName: '',
        id: '',
        decisionMadeBy: '',
        bcolAccountId: '',
        orgType: OrgAccountTypes.ALL,
        accessType: [],
        statuses: [props.accountStatus]
      }
    }

    async function syncBeforeNavigate (org: Organization) {
      cachePageInfo(state.tableDataOptions)
      await orgStore.syncOrganization(org.id)
      await orgStore.addOrgSettings(org)
      await orgStore.syncMembership(org.id)
    }

    function getIndexedTag (tag: string, index: number): string {
      return `${tag}-${index}`
    }

    function getOrgAndAccessTypeFromAccountType (accountType: string): object {
      return state.accountTypeMap[accountType]
    }

    function getAccountTypeFromOrgAndAccessType (org: Organization): any {
      const entries = Object.entries(state.accountTypeMap)
      const byAccessTypeAndOrgType = entries.find(([, value]) =>
        value?.accessType?.includes(org.accessType) &&
                value?.orgType === org.orgType
      )
      if (byAccessTypeAndOrgType) {
        return byAccessTypeAndOrgType[0]
      }
      const byAccessType = entries.find(([, value]) =>
        value?.accessType?.includes(org.accessType)
      )
      if (byAccessType) {
        return byAccessType[0]
      }
      const byOrgType = entries.find(([, value]) =>
        value?.orgType === org.orgType
      )
      if (byOrgType) {
        return byOrgType[0]
      }
      return ''
    }

    const noDataMessage = computed(() => {
      return t(
        state.searchParamsExist
          ? 'searchAccountNoResult'
          : 'searchAccountStartMessage'
      )
    })

    function setSearchFilterToStorage (val: string): void {
      ConfigHelper.addToSession(SessionStorageKeys.OrgSearchFilter, val)
    }

    function doSearchParametersExist (params: OrgFilterParams): boolean {
      return params.name.length > 0 ||
                params.branchName.length > 0 ||
                params.id.length > 0 ||
                params.bcolAccountId.length > 0 ||
                params.decisionMadeBy.length > 0 ||
                (params.orgType.length > 0 && params.orgType !== OrgAccountTypes.ALL)
    }

    const isActiveAccounts = computed(() => {
      return props.accountStatus === AccountStatus.ACTIVE
    })

    mounted()

    return {
      ...toRefs(state),
      debouncedOrgSearch,
      viewInBusinessRegistryDashboard,
      view,
      clearSearchParams,
      syncBeforeNavigate,
      getIndexedTag,
      getOrgAndAccessTypeFromAccountType,
      getAccountTypeFromOrgAndAccessType,
      noDataMessage,
      setSearchFilterToStorage,
      doSearchParametersExist,
      paginationOptions,
      numOfItems,
      saveItemsPerPage,
      isActiveAccounts
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
// Note this uses .fas-search
@import '~/fas-ui/src/assets/scss/search.scss';

// Vuetify Override
.theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  .v-icon.v-icon {
    color: $app-blue;
  }
}

// Class binding a vuetify override.
// To handle the sticky elements overlap in the custom scrolling data table.
.header-high-layer {
  ::v-deep {
    th {
      z-index: 2 !important;
    }
  }
}

::v-deep .theme--light.v-data-table .v-data-table__empty-wrapper {
  color: $gray7;
  &:hover {
    background-color: transparent;
  }
}

.business-dashboard-icon {
  opacity: 1;
  width: 14px;
  height: 14px;
  transform: rotate(0deg);
  display: inline-flex;
}

.account-active-search {
  table > thead > tr > th {
    width: 210px !important;
    min-width: 210px !important;
  }

  .open-action-btn,
  .more-actions-btn {
    box-shadow: 0 1px 1px 0px rgb(0 0 0 / 20%), 0 2px 2px 0 rgb(0 0 0 / 14%), 0 1px 5px 0 rgb(0 0 0 / 12%);
    -webkit-box-shadow: 0 1px 1px 0px rgb(0 0 0 / 20%), 0 2px 2px 0 rgb(0 0 0 / 14%), 0 1px 5px 0 rgb(0 0 0 / 12%);
  }

  .open-action-btn {
    &.active {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }
    min-width: 4.9rem !important;
  }

  .more-actions-btn {
    padding-left: 0px;
    padding-right: 0px;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
    max-width: 30px !important;
    min-width: 30px !important;
    margin-left: 0.05rem;
  }

  // Inline for Clear Filters
  .clear-filter-button {
    padding: 7px !important;
  }

  .clear-filter {
    line-height: 1.5;
  }

  // As requested by Tracey.
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
    width: 130px !important;
    min-width: 130px !important;
  }

  // The TD cells don't seem to be scoped properly.
  // Thus the usage of v-deep.
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
  }

  ::v-deep table > tbody > tr > td:last-child:not([colspan]) {
    padding-left: 3px !important;
    padding-right: 3px !important;
  }

}
</style>
