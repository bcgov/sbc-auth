<template>
  <div>
    <section>
      <v-row
        justify="end"
        no-gutters
      >
        <v-col
          align-self="end"
          cols="auto"
        >
          <v-select
            v-model="headersSelected"
            class="column-selections"
            dense
            filled
            hide-details
            item-text="value"
            :items="headersSelection"
            :menu-props="{
              bottom: true,
              minWidth: '200px',
              maxHeight: 'none',
              offsetY: true
            }"
            multiple
            return-object
            style="width: 200px;"
            @change="headersChanged"
          >
            <template #selection="{ index }">
              <span
                v-if="index === 0"
                class="columns-to-show"
              >Columns to show</span>
            </template>
          </v-select>
        </v-col>
      </v-row>
    </section>
    <v-form class="datatable-search account-active-search">
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
              :headers="filteredHeaders"
              :items="activeOrgs"
              :server-items-length="totalAccountsCount"
              :options.sync="tableDataOptions"
              :disable-sort="true"
              :footer-props="{
                itemsPerPageOptions: paginationOptions
              }"
              hide-default-header
              fixed-header
              :loading="isTableLoading"
              :mobile-breakpoint="0"
              @update:options="updateItemsPerPage"
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
                      v-for="(header, i) in filteredHeaders"
                      :key="getIndexedTag('find-header-row', i)"
                      :scope="getIndexedTag('find-header-col', i)"
                      class="font-weight-bold"
                    >
                      {{ header.text }}
                      <IconTooltip
                        v-if="header.toolTip"
                        :icon-styling="{ fontSize: '20px' }"
                        icon="mdi-information-outline"
                      >
                        <div v-sanitize="header.toolTip" />
                      </IconTooltip>
                    </th>
                  </tr>

                  <!-- Second row has search boxes. -->
                  <tr class="header-row-2 mt-2 px-2">
                    <th
                      v-for="(header, i) in filteredHeaders"
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
                        :placeholder="getHeaderPlaceHolderText(header)"
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

              <template #[`item.members`]="{ item }">
                <div
                  v-if="item.displayMembers.adminMembers.length > 0"
                  class="members-layout pt-2"
                >
                  <v-icon class="member-type-icon mr-2">
                    mdi-shield-account-outline
                  </v-icon>
                  <div class="members-text-layout">
                    <span class="members-role-text">Admin</span>
                    <div v-if="!item.showOnlyFirstAdmin">
                      {{ getConcatenatedDisplayMembers(item.displayMembers.adminMembers) }}
                    </div>
                    <div v-else>
                      {{ getFirstAdminDisplayMember(item) }}
                    </div>
                  </div>
                </div>
                <div
                  v-if="item.displayMembers.coordinatorMembers.length > 0 && !item.showOnlyFirstAdmin"
                  class="members-layout"
                >
                  <v-icon class="member-type-icon mr-2">
                    mdi-account-cog-outline
                  </v-icon>
                  <div class="members-text-layout">
                    <span class="members-role-text">Coordinator</span>
                    <div>
                      {{ getConcatenatedDisplayMembers(item.displayMembers.coordinatorMembers) }}
                    </div>
                  </div>
                </div>
                <div
                  v-if="item.displayMembers.userMembers.length > 0 && !item.showOnlyFirstAdmin"
                  class="members-layout"
                >
                  <v-icon class="member-type-icon mr-2">
                    mdi-account-outline
                  </v-icon>
                  <div class="members-text-layout">
                    <span class="members-role-text">User</span>
                    <div>
                      {{ getConcatenatedDisplayMembers(item.displayMembers.userMembers) }}
                    </div>
                  </div>
                </div>
                <div
                  v-if="hasMoreMembers(item.displayMembers)"
                  class="member-view-link ml-6"
                  @click="toggleMembersView(item)"
                >
                  <span>
                    {{ item.showOnlyFirstAdmin ? 'View more' : 'View less' }}
                  </span>
                  <v-icon
                    v-if="item.showOnlyFirstAdmin"
                    color="primary"
                    class="member-type-icon"
                  >
                    mdi-chevron-down
                  </v-icon>
                  <v-icon
                    v-else
                    color="primary"
                    class="member-type-icon"
                  >
                    mdi-chevron-up
                  </v-icon>
                </div>
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
import { AccessType, Account, AccountStatus, LoginSource, SessionStorageKeys } from '@/util/constants'
import {
  DEFAULT_DATA_OPTIONS,
  cachePageInfo,
  getAndPruneCachedPageInfo,
  getPaginationOptions,
  hasCachedPageInfo
} from '@/components/datatable/resources'
import {
  DisplayMember,
  Member, MembershipStatus,
  MembershipType,
  OrgAccountTypes,
  OrgFilterParams,
  OrgMap,
  Organization
} from '@/models/Organization'
import { PropType, computed, defineComponent, reactive, toRefs, watch } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { EnumDictionary } from '@/models/util'
import { IconTooltip } from '@/components'
import debounce from '@/util/debounce'
import { useI18n } from 'vue-i18n-composable'
import { useOrgStore } from '@/stores/org'
import { useStaffStore } from '@/stores/staff'

export default defineComponent({
  name: 'StaffAccountsTable',
  components: { IconTooltip },
  props: {
    accountStatus: {
      type: String as PropType<AccountStatus>,
      default: AccountStatus.ACTIVE
    },
    sessionStorageKey: {
      type: String as PropType<SessionStorageKeys>,
      default: SessionStorageKeys.OrgSearchFilter
    },
    paginationNumberOfItemsKey: {
      type: String as PropType<SessionStorageKeys>,
      default: SessionStorageKeys.PaginationNumberOfItems
    },
    paginationOptionsKey: {
      type: String as PropType<SessionStorageKeys>,
      default: SessionStorageKeys.PaginationOptions
    }
  },
  setup (props, { root }) {
    const { t } = useI18n()
    const orgStore = useOrgStore()
    const staffStore = useStaffStore()
    const defaultHeaders = [
      { text: 'Account Name', value: 'name', visible: true },
      { text: 'Branch Name', value: 'branchName', visible: true },
      { text: 'Account Number', value: 'id', visible: true },
      { text: 'BCOL Account Number', value: 'bcolAccountId', visible: true },
      { text: 'Team Member',
        value: 'members',
        visible: false,
        toolTip: 'Search by entering last name [space] first name or username'
      },
      { text: 'Approved By', value: 'decisionMadeBy', visible: true },
      { text: 'Account Type', value: 'orgType', visible: true },
      { text: 'Actions', value: 'action', visible: true }
    ]

    const state = reactive({
      activeOrgs: [] as Organization[],
      headers: defaultHeaders,
      filteredHeaders: defaultHeaders.filter(item => item.visible),
      headersSelected: defaultHeaders
        .filter(item => item.value !== 'action' && item.visible)
        .map(item => item.text),
      headersSelection: defaultHeaders
        .filter(item => item.value !== 'action')
        .map(item => item.text),
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

    const debouncedOrgSearch = debounce(async function (page = 1, pageLimit = state.tableDataOptions.itemsPerPage) {
      try {
        state.isTableLoading = true
        const completeSearchParams: OrgFilterParams = {
          ...state.searchParams,
          orgType: undefined,
          accessType: undefined,
          ...getOrgAndAccessTypeFromAccountType(state.searchParams.orgType),
          includeMembers: true,
          page: page,
          limit: pageLimit
        }
        const activeAccountsResp = await staffStore.searchOrgs(completeSearchParams)
        state.activeOrgs = activeAccountsResp.orgs
        state.totalAccountsCount = activeAccountsResp?.total || 0
        transformMemberDataStructure()
      } catch (error) {
        console.error(error)
      } finally {
        state.isTableLoading = false
      }
    })

    function hasMoreMembers (displayMembers: any) : boolean {
      if (!displayMembers ||
          (displayMembers.adminMembers.length === 1 &&
          displayMembers.coordinatorMembers.length === 0 &&
          displayMembers.userMembers.length === 0)) {
        return false
      }
      return true
    }

    function toggleMembersView (org: any): void {
      org.showOnlyFirstAdmin = !org.showOnlyFirstAdmin
      this.$forceUpdate()
    }

    function getFirstAdminDisplayMember (item: any) {
      const displayName = item?.displayMembers?.adminMembers[0].memberDisplayName
      if (!displayName) return ''
      return displayName
    }

    function getConcatenatedDisplayMembers (members: DisplayMember[]) {
      return members.map((member) => member.memberDisplayName).join(',')
    }

    function buildDisplayMemberObject (member: Member) {
      const username = member.user?.loginSource === LoginSource.BCEID
        ? `(BCeID: ${member.user.username.split('@')[0]})` : ''
      const firstname = member.user.firstname || ''
      const lastname = member.user.lastname || ''

      return {
        memberDisplayName: `${firstname} ${lastname}${username}`.trim(),
        loginSource: member.user.loginSource
      }
    }

    function filterMembersByType (members, membershipType: MembershipType) {
      if (!members || members.length === 0) return []
      return members.filter(member => {
        return member.membershipTypeCode === membershipType &&
            member.membershipStatus === MembershipStatus.Active
      })
    }

    function transformMemberDataStructure () {
      state.activeOrgs.forEach((org: Organization) => {
        org.displayMembers = {
          adminMembers: filterMembersByType(org.members, MembershipType.Admin)
            .map(buildDisplayMemberObject),
          coordinatorMembers: filterMembersByType(org.members, MembershipType.Coordinator)
            .map(buildDisplayMemberObject),
          userMembers: filterMembersByType(org.members, MembershipType.User)
            .map(buildDisplayMemberObject)
        }
        org.showOnlyFirstAdmin = true
      })
    }

    function headersChanged (selectedHeaders) {
      state.headers.forEach(item => {
        if (item.value !== 'action') {
          item.visible = selectedHeaders.includes(item.text)
        }
      })
      state.filteredHeaders = state.headers.filter(item => item.visible)
    }

    function mounted () {
      state.tableDataOptions = DEFAULT_DATA_OPTIONS
      const orgSearchFilter = ConfigHelper.getFromSession(props.sessionStorageKey) || ''
      try {
        state.searchParams = JSON.parse(orgSearchFilter)
      } catch {
        // Do nothing, we have defaults for searchParams.
      }
      const hasInfo = hasCachedPageInfo(props.paginationOptionsKey)
      if (hasInfo) {
        state.tableDataOptions = getAndPruneCachedPageInfo(props.paginationOptionsKey)
      }
    }

    watch(() => state.searchParams, function (value) {
      state.searchParamsExist = doSearchParametersExist(value)
      state.tableDataOptions = { ...getAndPruneCachedPageInfo(props.paginationOptionsKey), page: 1 }
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
        statuses: [props.accountStatus],
        members: ''
      }
    }

    async function syncBeforeNavigate (org: Organization) {
      cachePageInfo(state.tableDataOptions, props.paginationOptionsKey)
      await orgStore.syncOrganization(org.id)
      await orgStore.addOrgSettings(org)
      await orgStore.syncMembership(org.id)
    }

    function getIndexedTag (tag: string, index: number): string {
      return `${tag}-${index}`
    }

    function updateItemsPerPage (options: DataOptions): void {
      cachePageInfo(options, props.paginationOptionsKey)
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

    function getHeaderPlaceHolderText (header: any): string {
      if (header.text === 'Team Member') {
        return 'Name or username'
      }
      return header.text
    }

    const noDataMessage = computed(() => {
      return t(
        state.searchParamsExist
          ? 'searchAccountNoResult'
          : 'searchAccountStartMessage'
      )
    })

    function setSearchFilterToStorage (val: string): void {
      ConfigHelper.addToSession(props.sessionStorageKey, val)
    }

    function doSearchParametersExist (params: OrgFilterParams): boolean {
      return params.name.length > 0 ||
                params.branchName.length > 0 ||
                params.id.length > 0 ||
                params.bcolAccountId.length > 0 ||
                params.decisionMadeBy.length > 0 ||
                (params.orgType.length > 0 && params.orgType !== OrgAccountTypes.ALL) ||
                params.members.length > 0
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
      updateItemsPerPage,
      isActiveAccounts,
      getHeaderPlaceHolderText,
      hasMoreMembers,
      getConcatenatedDisplayMembers,
      getFirstAdminDisplayMember,
      toggleMembersView,
      headersChanged
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
// Note this uses .datatable-search
@import '@/assets/scss/search.scss';

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

.columns-to-show {
  color: $gray7;
  font-size: 14px;
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
    vertical-align: text-top;
  }

  ::v-deep table > tbody > tr > td:last-child:not([colspan]) {
    padding-left: 3px !important;
    padding-right: 3px !important;
  }

  .member-view-link {
    font-weight: bold;
    color: $app-blue;
  }
  .members-layout {
    display: flex;
    align-items: flex-start;

    .member-type-icon {
      font-size: 16px;
      color: $gray9;
      margin-top: 2px;
    }
    .members-text-layout {
      display: flex;
      flex-direction: column;
      .members-role-text {
        font-weight: bold;
      }
    }
  }
}
</style>
