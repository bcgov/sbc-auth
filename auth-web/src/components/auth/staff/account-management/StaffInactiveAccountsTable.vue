<template>
  <div>
    <v-form class="fas-search account-inactive-search">
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
              :items="inactiveOrgs"
              :server-items-length="totalAccountsCount"
              :options.sync="tableDataOptions"
              :disable-sort="true"
              :footer-props="{
                itemsPerPageOptions: getPaginationOptions
              }"
              :items-per-page="numberOfItems"
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
                  class="py-8 no-data"
                  v-html="noDataMessage"
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
                      class="open-action-btn"
                      :data-test="getIndexedTag('view-account-button', item.id)"
                      @click="view(item)"
                    >
                      View
                    </v-btn>
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
import { defineComponent, ref, reactive, computed, watch } from '@vue/composition-api'
import { AccessType, Account, AccountStatus, SessionStorageKeys } from '@/util/constants'
import { OrgAccountTypes, OrgFilterParams, OrgMap, Organization } from '@/models/Organization'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { useOrgStore } from '@/stores/org'
import { useStaffStore } from '@/stores/staff'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { EnumDictionary } from '@/models/util'
import debounce from '@/util/debounce'

export default defineComponent({
  name: 'StaffInactiveAccountsTable',
  components: {
    PaginationMixin
  },
  setup(props, { root }) {
    const paginationMixin = new PaginationMixin()
    const orgStore = useOrgStore()
    const staffStore = useStaffStore()
    const inactiveOrgs = ref<Organization[]>([])
    const totalAccountsCount = ref(0)
    const isTableLoading = ref(false)
    const tableDataOptions = ref<Partial<DataOptions>>({})
    const searchParamsExist = ref(false)
    const searchParams = reactive<OrgFilterParams>({
      name: '',
      branchName: '',
      id: '',
      decisionMadeBy: '',
      orgType: OrgAccountTypes.ALL,
      statuses: [AccountStatus.INACTIVE]
    })

    const headerAccounts = [
      { text: 'Account Name', value: 'name' },
      { text: 'Branch Name', value: 'branchName' },
      { text: 'Account Number', value: 'id' },
      { text: 'Approved By', value: 'decisionMadeBy' },
      { text: 'Account Type', value: 'orgType' },
      { text: 'Actions', value: 'action' }
    ]

    const accountTypeMap: EnumDictionary<OrgAccountTypes, OrgMap> = {
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
    }

    const accountTypes = computed(() => Object.keys(accountTypeMap))
    const formatDate = CommonUtils.formatDisplayDate

    const getIndexedTag = (tag, index) => `${tag}-${index}`

    const noDataMessage = computed(() => {
      return root.$t(
        searchParamsExist.value
          ? 'searchAccountNoResult'
          : 'searchAccountStartMessage'
      )
    })

    const setSearchFilterToStorage = (val: string) => {
      ConfigHelper.addToSession(SessionStorageKeys.InactiveAccountsSearchFilter, val)
    }

    const doSearchParametersExist = (searchParams: OrgFilterParams) => {
      return searchParams.name.length > 0 ||
        searchParams.branchName.length > 0 ||
        searchParams.id.length > 0 ||
        searchParams.decisionMadeBy.length > 0 ||
        (searchParams.orgType.length > 0 && searchParams.orgType !== OrgAccountTypes.ALL)
    }

    const numberOfItems = paginationMixin.numberOfItems;

    const debouncedOrgSearch = debounce(async (page = 1, pageLimit = numberOfItems) => {
      try {
        isTableLoading.value = true
        const completeSearchParams: OrgFilterParams = {
          ...searchParams,
          // orgType and accessType get overwritten from getOrgAndAccessTypeFromAccountType
          orgType: undefined,
          accessType: undefined,
          ...getOrgAndAccessTypeFromAccountType(searchParams.orgType),
          page: page,
          limit: pageLimit
        }
        const inactiveAccountsResp = await staffStore.searchOrgs(completeSearchParams)
        inactiveOrgs.value = inactiveAccountsResp.orgs
        totalAccountsCount.value = inactiveAccountsResp?.total || 0
      } catch (error) {
        console.error(error)
      } finally {
        isTableLoading.value = false
      }
    })

    const getOrgAndAccessTypeFromAccountType = (accountType: string): object => {
      return accountTypeMap[accountType]
    }

    const getAccountTypeFromOrgAndAccessType = (org: Organization): any => {
      const entries = Object.entries(accountTypeMap)
      const byAccessTypeAndOrgType = entries.find(([, value]) =>
        value?.accessType?.includes(org.accessType) &&
        value?.orgType === org.orgType)
      if (byAccessTypeAndOrgType) {
        return byAccessTypeAndOrgType[0]
      }
      const byAccessType = entries.find(([, value]) =>
        value?.accessType?.includes(org.accessType))
      if (byAccessType) {
        return byAccessType[0]
      }
      const byOrgType = entries.find(([, value]) =>
        value?.orgType === org.orgType)
      if (byOrgType) {
        return byOrgType[0]
      }
      return ''
    }

    const clearSearchParams = () => {
      searchParams.name = ''
      searchParams.branchName = ''
      searchParams.id = ''
      searchParams.decisionMadeBy = ''
      searchParams.orgType = OrgAccountTypes.ALL
      searchParams.accessType = []
      searchParams.statuses = [AccountStatus.INACTIVE]
    }

    const view = async (org: Organization) => {
      await syncBeforeNavigate(org)
      root.$router.push(`/account/${org.id}/settings`)
    }

    const syncBeforeNavigate = async (org: Organization) => {
      cachePageInfo(tableDataOptions.value)
      await orgStore.syncOrganization(org.id)
      await orgStore.addOrgSettings(org)
      await orgStore.syncMembership(org.id)
    }

    const cachePageInfo = paginationMixin.cachePageInfo;
    const saveItemsPerPage = paginationMixin.saveItemsPerPage;
    const getPaginationOptions = paginationMixin.getPaginationOptions;

    watch(searchParams, (value) => {
      searchParamsExist.value = doSearchParametersExist(value)
      tableDataOptions.value = { ...paginationMixin.getAndPruneCachedPageInfo(), page: 1 }
      setSearchFilterToStorage(JSON.stringify(value))
      debouncedOrgSearch(this)
    }, { deep: true })

    watch(tableDataOptions, (val) => {
      debouncedOrgSearch(val?.page, val?.itemsPerPage)
    }, { deep: true })

    return {
      inactiveOrgs,
      totalAccountsCount,
      isTableLoading,
      tableDataOptions,
      searchParamsExist,
      searchParams,
      headerAccounts,
      accountTypes,
      formatDate,
      noDataMessage,
      getIndexedTag,
      clearSearchParams,
      view,
      getOrgAndAccessTypeFromAccountType,
      getAccountTypeFromOrgAndAccessType,
      saveItemsPerPage,
      getPaginationOptions,
      numberOfItems
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

.account-inactive-search {
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
