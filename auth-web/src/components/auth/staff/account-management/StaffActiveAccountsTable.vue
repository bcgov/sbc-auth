<template>
  <div>
    <SearchFilterInput
      :filterParams="searchFilter"
      :filteredRecordsCount="totalAccountsCount"
      @filter-texts="setAppliedFilterValue"
      :isDataFetchCompleted="!isTableLoading"
    ></SearchFilterInput>
    <v-data-table
      class="account-list"
      :headers="headerAccounts"
      :items="activeOrgs"
      :server-items-length="totalAccountsCount"
      :no-data-text="$t('noActiveAccountsLabel')"
      :options.sync="tableDataOptions"
      :disable-sort="true"
      :footer-props="{
        itemsPerPageOptions: getPaginationOptions
      }"
      :loading="isTableLoading"
      @update:items-per-page="saveItemsPerPage"
    >
      <template v-slot:loading>
        Loading...
      </template>
      <template v-slot:[`item.orgType`]="{ item }">
          {{formatType(item)}}
      </template>
      <template v-slot:[`item.decisionMadeBy`]="{ item }">
          {{item.decisionMadeBy ? item.decisionMadeBy : 'N/A'}}
      </template>

      <template v-slot:[`item.action`]="{ item }">
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
  </div>
</template>

<script lang="ts">
import { AccessType, Account, AccountStatus, SearchFilterCodes, SessionStorageKeys } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, OrgFilterParams, OrgList, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import OrgModule from '@/store/modules/org'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
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
  private readonly searchOrgs!: (filterParams: OrgFilterParams) => OrgList
  private searchFilter: SearchFilterParam[] = [
    {
      id: SearchFilterCodes.ACCOUNTNAME,
      placeholder: 'Account Name',
      labelKey: '',
      appliedFilterValue: '',
      filterInput: ''
    }
  ]

  private readonly headerAccounts = [
    {
      text: 'Name',
      align: 'left',
      sortable: true,
      value: 'name'
    },
    {
      text: 'Branch Name',
      align: 'left',
      sortable: true,
      value: 'branchName'
    },
    {
      text: 'Account Id',
      align: 'left',
      sortable: true,
      value: 'id'
    },
    {
      text: 'Type',
      align: 'left',
      sortable: true,
      value: 'orgType'
    },
    {
      text: 'Approved By',
      align: 'left',
      sortable: true,
      value: 'decisionMadeBy'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '105'
    }
  ]

  private formatDate = CommonUtils.formatDisplayDate

  private totalAccountsCount = 0
  private tableDataOptions: Partial<DataOptions> = {}
  private orgFilter: OrgFilterParams
  private isTableLoading: boolean = false

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  @Watch('tableDataOptions', { deep: true })
  async getAccounts (val, oldVal) {
    await this.getOrgs(val?.page, val?.itemsPerPage)
  }

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
  }

  private async getOrgs (page: number = 1, pageLimit: number = this.numberOfItems) {
    // set this variable so that the chip is shown
    const appliedFilterValue = ConfigHelper.getFromSession(SessionStorageKeys.OrgSearchFilter) || ''
    this.searchFilter[0].appliedFilterValue = appliedFilterValue
    try {
      this.orgFilter = {
        statuses: [AccountStatus.ACTIVE],
        pageNumber: page,
        pageLimit: pageLimit,
        name: appliedFilterValue
      }
      const activeAccountsResp = await this.searchOrgs(this.orgFilter)
      this.activeOrgs = activeAccountsResp.orgs
      this.totalAccountsCount = activeAccountsResp?.total || 0
    } catch (error) {
      this.isTableLoading = false
      // eslint-disable-next-line no-console
      console.error(error)
    }
  }

  private async view (org: Organization) {
    this.cachePageInfo(this.tableDataOptions)
    let orgId:number = org.id
    await this.syncOrganization(orgId)
    await this.addOrgSettings(org)
    await this.syncMembership(orgId)
    this.$router.push(`/account/${orgId}/settings`)
  }

  private formatType (org:Organization):string {
    let orgTypeDisplay = org.orgType === Account.BASIC ? 'Basic' : 'Premium'
    if (org.accessType === AccessType.ANONYMOUS) {
      return 'Director Search'
    }
    if (org.accessType === AccessType.EXTRA_PROVINCIAL) {
      return orgTypeDisplay + ' (out-of-province)'
    }
    return orgTypeDisplay
  }

  private setSearchFilterToStorage (val:string):void {
    ConfigHelper.addToSession(SessionStorageKeys.OrgSearchFilter, val)
  }

  private async setAppliedFilterValue (filter: SearchFilterParam[]) {
    // changes to reset pagination option on search
    // we dont want to reset no of page or any other option only need to reset page to first
    // so instead of this.DEFAULT_DATA_OPTIONS we use below ways
    this.tableDataOptions = { ...this.getAndPruneCachedPageInfo(), page: 1 }
    this.isTableLoading = true
    this.setSearchFilterToStorage(filter[0].appliedFilterValue)
    await this.getOrgs()
    this.isTableLoading = false
  }
}
</script>

<style lang="scss" scoped>
::v-deep {
  table {
    table-layout: fixed;

    td {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }
  }
}

.action-btn {
  width: 5rem;
}

.filter-results {
  opacity: 0;
  overflow: hidden;
  max-height: 0;
  transition: all ease-out 0.25s;
}

.filter-results.active {
  opacity: 1;
  max-height: 4rem;
}

.filter-results-label {
  font-weight: 700;
}
</style>
