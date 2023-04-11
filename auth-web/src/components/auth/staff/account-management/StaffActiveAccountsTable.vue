  <template>
  <div>
    <v-form class="fas-search account-active-search">
      <v-row dense class="row-margin">
        <v-col sm="12" cols="6">
          <transition name="slide-fade">
            <v-data-table
              :headers="headerAccounts"
              :items="activeOrgs"
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
              <template v-slot:loading>
                <div
                  class="py-8 loading-datatable"
                  >
                  Loading items...
                </div>
              </template>

              <!-- No data -->
              <template v-slot:no-data>
                <div
                  class="py-8 no-data"
                  v-html='noDataMessage'
                />
              </template>

              <!-- Headers (two rows) -->
              <template v-slot:header="{}">
                <thead class="v-data-table-header">
                  <!-- First row has titles. -->
                  <tr class="header-row-1">
                    <th
                      v-for="(header, i) in headerAccounts"
                      :scope="i"
                      :key="getIndexedTag('find-header-row', i)"
                      class="font-weight-bold"
                    >
                      {{ header.text }}
                    </th>
                  </tr>

                  <!-- Second row has search boxes. -->
                  <tr class="header-row-2 mt-2 px-2">
                    <th
                      v-for="(header, i) in headerAccounts"
                      :scope="i"
                      :key="getIndexedTag('find-header-row2', i)"
                    >
                      <v-text-field
                        v-if="!['orgType','action'].includes(header.value)"
                        :id="header.value"
                        input type="search"
                        autocomplete="off"
                        class="text-input-style"
                        filled
                        :placeholder="header.text"
                        v-model.trim="searchParams[header.value]"
                        dense
                        hide-details="auto"
                      />

                      <div v-else-if="['orgType'].includes(header.value)" class="mt-0">
                          <v-select
                            :items="accountTypes"
                            v-model="searchParams[header.value]"
                            filled
                            item-text="description"
                            item-value="code"
                            return-object
                            data-test="select-status"
                            v-bind="$attrs"
                            v-on="$listeners"
                            hide-details="auto"
                          />
                      </div>

                      <v-btn v-else-if="searchParamsExist && header.value === 'action'"
                        outlined
                        color="primary"
                        class="action-btn clear-filter-button"
                        @click="clearSearchParams()"
                      >
                        <span class="clear-filter cursor-pointer">
                          Clear Filters
                          <v-icon small color="primary">mdi-close</v-icon>
                        </span>
                      </v-btn>
                    </th>
                  </tr>
                </thead>
              </template>

              <template v-slot:[`item.orgType`]="{ item }">
                  {{getAccountTypeFromOrgAndAccessType(item)}}
              </template>
              <template v-slot:[`item.decisionMadeBy`]="{ item }">
                  {{item.decisionMadeBy ? item.decisionMadeBy : 'N/A'}}
              </template>

               <!-- Item Actions -->
              <template v-slot:[`item.action`]="{ item }">
                <div class="actions text-right">
                  <span class="open-action">
                    <v-btn
                      color="primary"
                      class="open-action-btn"
                      @click="view(item)"
                      :data-test="getIndexedTag('view-account-button', item.id)"
                    >
                      View
                    </v-btn>
                  </span>

                  <!-- More Actions Menu -->
                  <span class="more-actions">
                    <v-menu
                      offset-y
                      nudge-left=212
                      v-model="dropdown[item.id]"
                    >
                      <template v-slot:activator="{ on }">
                        <v-btn
                          color="primary"
                          class="more-actions-btn"
                          v-on="on"
                        >
                          <v-icon>{{dropdown[item.id] ? 'mdi-menu-up' : 'mdi-menu-down'}}</v-icon>
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
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { Member, OrgAccountTypes, OrgFilterParams, OrgList, OrgMap, Organization } from '@/models/Organization'
import { EnumDictionary } from '@/models/util'
import OrgModule from '@/store/modules/org'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { AccessType, Account, AccountStatus, SessionStorageKeys } from '@/util/constants'
import debounce from '@/util/debounce'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import { Component, Mixins, Watch } from 'vue-property-decorator'
import { DataOptions } from 'vuetify'
import { namespace } from 'vuex-class'
import { getModule } from 'vuex-module-decorators'

const StaffBinding = namespace('staff')
const OrgBinding = namespace('org')

@Component({
  components: {
    SearchFilterInput
  }
})
export default class StaffActiveAccountsTable extends Mixins(PaginationMixin) {
  @OrgBinding.Action('syncOrganization') protected readonly syncOrganization!: (currentAccount: number) => Promise<Organization>
  @OrgBinding.Action('addOrgSettings') protected addOrgSettings!: (org: Organization) => Promise<UserSettings>
  @OrgBinding.Action('syncMembership') protected syncMembership!: (orgId: number) => Promise<Member>
  @StaffBinding.Action('searchOrgs') protected searchOrgs!: (filterParams: OrgFilterParams) => Promise<OrgList>

  protected orgStore = getModule(OrgModule, this.$store)
  protected activeOrgs: Organization[] = []
  protected readonly headerAccounts = [
    {
      text: 'Account Name',
      value: 'name'
    },
    {
      text: 'Branch Name',
      value: 'branchName'
    },
    {
      text: 'Account Number',
      value: 'id'
    },
    {
      text: 'Approved By',
      value: 'decisionMadeBy'
    },
    {
      text: 'Account Type',
      value: 'orgType'
    },
    {
      text: 'Actions',
      value: 'action'
    }
  ]
  protected readonly accountTypeMap: EnumDictionary<OrgAccountTypes, OrgMap> =
  {
    [OrgAccountTypes.ALL]: {
    },
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
  protected readonly accountTypes = Array.from(Object.keys(this.accountTypeMap))
  protected formatDate = CommonUtils.formatDisplayDate
  protected totalAccountsCount = 0
  protected tableDataOptions: Partial<DataOptions> = {}
  protected isTableLoading = false
  protected searchParamsExist = false
  /* V-model for dropdown menus. */
  protected readonly dropdown: Array<boolean> = []
  /* V-model for searching */
  protected searchParams: OrgFilterParams = {
    name: '',
    branchName: '',
    id: '',
    decisionMadeBy: '',
    orgType: OrgAccountTypes.ALL,
    statuses: [AccountStatus.ACTIVE]
  }

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    const orgSearchFilter = ConfigHelper.getFromSession(SessionStorageKeys.OrgSearchFilter) || ''
    try {
      this.searchParams = JSON.parse(orgSearchFilter)
    } catch {
      // Do nothing, we have defaults for searchParams.
    }
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
  }

  @Watch('searchParams', { deep: true })
  searchChanged (value: OrgFilterParams) {
    this.searchParamsExist = this.doSearchParametersExist(value)
    this.tableDataOptions = { ...this.getAndPruneCachedPageInfo(), page: 1 }
    this.setSearchFilterToStorage(JSON.stringify(value))
    this.debouncedOrgSearch(this)
  }

  @Watch('tableDataOptions', { deep: true })
  async tableDataOptionsChange (val) {
    this.debouncedOrgSearch(this, val?.page, val?.itemsPerPage)
  }

  // Needed context here instead of this.
  protected readonly debouncedOrgSearch = debounce(async (context: StaffActiveAccountsTable, page = 1, pageLimit = context.numberOfItems) => {
    try {
      context.isTableLoading = true
      const completeSearchParams: OrgFilterParams = {
        ...context.searchParams,
        // orgType and accessType get overwritten from getOrgAndAccessTypeFromAccountType
        orgType: undefined,
        accessType: undefined,
        ...context.getOrgAndAccessTypeFromAccountType(context.searchParams.orgType),
        page: page,
        limit: pageLimit
      }
      const activeAccountsResp = await context.searchOrgs(completeSearchParams)
      context.activeOrgs = activeAccountsResp.orgs
      context.totalAccountsCount = activeAccountsResp?.total || 0
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error(error)
    } finally {
      context.isTableLoading = false
    }
  })

  protected async viewInBusinessRegistryDashboard (org: Organization) {
    await this.syncBeforeNavigate(org)
    this.$router.push(`/account/business/business?accountid=${org.id}`)
  }

  protected async view (org: Organization) {
    await this.syncBeforeNavigate(org)
    this.$router.push(`/account/${org.id}/settings`)
  }

  protected clearSearchParams () {
    this.searchParams = {
      name: '',
      branchName: '',
      id: '',
      decisionMadeBy: '',
      orgType: OrgAccountTypes.ALL,
      accessType: [],
      statuses: [AccountStatus.ACTIVE]
    }
  }

  protected async syncBeforeNavigate (org: Organization) {
    this.cachePageInfo(this.tableDataOptions)
    await this.syncOrganization(org.id)
    await this.addOrgSettings(org)
    await this.syncMembership(org.id)
  }

  protected getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  // Used to go from 'Basic' -> accessType: AccessType.REGULAR, orgType: Account.BASIC
  protected getOrgAndAccessTypeFromAccountType (accountType: string): object {
    return this.accountTypeMap[accountType]
  }

  // Used to go from OrgType -> OrgAccountTypes
  protected getAccountTypeFromOrgAndAccessType (org:Organization): any {
    const entries = Object.entries(this.accountTypeMap)
    const byAccessTypeAndOrgType = entries.find(([key, value]) =>
      value?.accessType?.includes(org.accessType) &&
      value?.orgType === org.orgType)
    if (byAccessTypeAndOrgType) {
      return byAccessTypeAndOrgType[0]
    }
    const byAccessType = entries.find(([key, value]) =>
      value?.accessType?.includes(org.accessType))
    if (byAccessType) {
      return byAccessType[0]
    }
    const byOrgType = entries.find(([key, value]) =>
      value?.orgType === org.orgType)
    if (byOrgType) {
      return byOrgType[0]
    }
    return ''
  }

  protected get noDataMessage () {
    return this.$t(
      this.searchParamsExist
        ? 'searchAccountNoResult'
        : 'searchAccountStartMessage'
    )
  }

  protected setSearchFilterToStorage (val:string):void {
    ConfigHelper.addToSession(SessionStorageKeys.OrgSearchFilter, val)
  }

  protected doSearchParametersExist (searchParams: OrgFilterParams) {
    return searchParams.name.length > 0 ||
          searchParams.branchName.length > 0 ||
          searchParams.id.length > 0 ||
          searchParams.decisionMadeBy.length > 0 ||
          (searchParams.orgType.length > 0 && searchParams.orgType !== OrgAccountTypes.ALL)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
// Note this uses .fas-search
@import '~fas-ui/src/assets/scss/search.scss';

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
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
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
