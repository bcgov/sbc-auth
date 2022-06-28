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
                  class="loading-datatable"
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
                      :key="'find-header-row-1-'+i"
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
                      :key="'find-header-row-2-'+i"
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
                            :placeholder="header.text"
                          />
                      </div>

                      <v-btn v-else-if="searchParamsExist && header.value === 'action'"
                        outlined
                        color="primary"
                        class="action-btn"
                        @click="clearSearchParams()"
                      >
                        Clear Filters
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
                            <v-img class="business-dashboard-icon" src="@/assets/img/StaffActive_business_dashboard_icon.svg"/>
                            <span class="pl-1">Business Registry Dashboard</span>
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
import { AccessType, Account, AccountStatus, SearchFilterCodes, SessionStorageKeys } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, OrgFilterParams, OrgList, OrgMap, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import OrgModule from '@/store/modules/org'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import debounce from '@/util/debounce'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    SearchFilterInput
  },
  methods: {
    ...mapActions('org', ['syncOrganization', 'addOrgSettings', 'syncMembership']),
    ...mapActions('staff', ['searchOrgs'])
  }
})
export default class StaffActiveAccountsTable extends Mixins(PaginationMixin) {
  private orgStore = getModule(OrgModule, this.$store)
  private activeOrgs: Organization[] = []
  private readonly syncOrganization!: (currentAccount: number) => Promise<Organization>
  private readonly addOrgSettings!: (org: Organization) => Promise<UserSettings>
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly searchOrgs!: (filterParams: OrgFilterParams) => Promise<OrgList>
  private readonly headerAccounts = [
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
  private readonly accountTypeMap = new Map<string, OrgMap>([
    [
      'Basic', {
        accessType: [AccessType.REGULAR, AccessType.REGULAR_BCEID],
        orgType: Account.BASIC
      }
    ],
    [
      'Basic (out-of-province)', {
        accessType: [AccessType.EXTRA_PROVINCIAL],
        orgType: Account.BASIC
      }
    ],
    [
      'Premium', {
        accessType: [AccessType.REGULAR, AccessType.REGULAR_BCEID],
        orgType: Account.PREMIUM
      }
    ],
    [
      'Premium (out-of-province)', {
        accessType: [AccessType.EXTRA_PROVINCIAL],
        orgType: Account.PREMIUM
      }
    ],
    [
      'GovM', {
        accessType: [AccessType.GOVM]
      }
    ],
    [
      'GovN', {
        accessType: [AccessType.GOVN]
      }
    ],
    [
      'Director Search', {
        accessType: [AccessType.ANONYMOUS]
      }
    ]
  ])
  private readonly accountTypes = Array.from(this.accountTypeMap.keys())
  private formatDate = CommonUtils.formatDisplayDate
  private totalAccountsCount = 0
  private tableDataOptions: Partial<DataOptions> = {}
  private isTableLoading = false
  private searchParamsExist = false
  /* V-model for dropdown menus. */
  private readonly dropdown: Array<boolean> = []
  /* V-model for searching */
  private searchParams: OrgFilterParams = {
    name: '',
    branchName: '',
    id: '',
    decisionMadeBy: '',
    orgType: '',
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
  searchChanged (value: OrgFilterParams, oldValue: OrgFilterParams) {
    this.searchParamsExist = this.doSearchParametersExist(value)
    this.tableDataOptions = { ...this.getAndPruneCachedPageInfo(), page: 1 }
    this.setSearchFilterToStorage(JSON.stringify(value))
    this.debouncedOrgSearch(this)
  }

  @Watch('tableDataOptions', { deep: true })
  async tableDataOptionsChange (val, oldVal) {
    this.debouncedOrgSearch(this, val?.page, val?.itemsPerPage)
  }

  // Needed context here instead of this.
  private readonly debouncedOrgSearch = debounce(async (context: StaffActiveAccountsTable, page = 1, pageLimit = context.numberOfItems) => {
    try {
      context.isTableLoading = true
      const completeSearchParams: OrgFilterParams = {
        ...context.searchParams,
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

  private async viewInBusinessRegistryDashboard (org: Organization) {
    await this.syncBeforeNavigate(org)
    this.$router.push(`/account/business/business?accountid=${org.id}`)
  }

  private async view (org: Organization) {
    await this.syncBeforeNavigate(org)
    this.$router.push(`/account/${org.id}/settings`)
  }

  private clearSearchParams () {
    this.searchParams = {
      name: '',
      branchName: '',
      id: '',
      decisionMadeBy: '',
      orgType: '',
      accessType: [],
      statuses: [AccountStatus.ACTIVE]
    }
  }

  private async syncBeforeNavigate (org: Organization) {
    this.cachePageInfo(this.tableDataOptions)
    await this.syncOrganization(org.id)
    await this.addOrgSettings(org)
    await this.syncMembership(org.id)
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  // Used to go from 'Basic' -> accessType: AccessType.REGULAR, orgType: Account.BASIC
  private getOrgAndAccessTypeFromAccountType (accountType: string): object {
    return this.accountTypeMap.get(accountType)
  }

  // Used to go from accessType: AccessType.REGULAR, orgType: Account.BASIC -> 'Basic'
  private getAccountTypeFromOrgAndAccessType (org:Organization): any {
    for (const [key, value] of this.accountTypeMap.entries()) {
      if (value?.accessType.includes(org.accessType) && value.orgType === org.orgType) {
        return key
      }
    }
    for (const [key, value] of this.accountTypeMap.entries()) {
      if (value?.accessType.includes(org.accessType)) {
        return key
      }
    }
    for (const [key, value] of this.accountTypeMap.entries()) {
      if (value?.orgType === org.orgType) {
        return key
      }
    }
  }

  private get noDataMessage () {
    return this.$t(
      this.searchParamsExist
        ? 'searchAccountNoResult'
        : 'searchAccountStartMessage'
    )
  }

  private setSearchFilterToStorage (val:string):void {
    ConfigHelper.addToSession(SessionStorageKeys.OrgSearchFilter, val)
  }

  private doSearchParametersExist (searchParams: OrgFilterParams) {
    return searchParams.name.length > 0 ||
          searchParams.branchName.length > 0 ||
          searchParams.id.length > 0 ||
          searchParams.decisionMadeBy.length > 0 ||
          searchParams.orgType.length > 0
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

  .v-data-table th {
    font-size: 0.75rem;
  }

  ::v-deep .v-data-footer {
    min-width: 100%;
  }

  .no-data, .loading-datatable {
    border: 0px;
    position: sticky;
    width: 1260px;
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
