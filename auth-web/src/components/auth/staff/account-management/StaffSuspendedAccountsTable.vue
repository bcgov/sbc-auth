<template>
  <div>
    <v-data-table
      class="account-list"
      :headers="headerAccounts"
      :items="suspendedOrgs"
      :no-data-text="$t('noActiveAccountsLabel')"
      :options.sync="tableDataOptions"
      :disable-sort="false"
      :footer-props="{
        itemsPerPageOptions: getPaginationOptions
      }"
      :loading="isTableLoading"
      :server-items-length="totalAccountsCount"
      @update:items-per-page="saveItemsPerPage"
    >
      <template #loading>
        Loading...
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
      <template #[`item.orgType`]="{ item }">
        {{ formatType(item) }}
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
  </div>
</template>

<script lang="ts">
import { AccessType, Account, AccountStatus } from '@/util/constants'
import { Action, State } from 'pinia-class'
import { Component, Mixins, Watch } from 'vue-property-decorator'
import { Member, OrgFilterParams, OrgList, Organization } from '@/models/Organization'
import { Code } from '@/models/Code'
import CommonUtils from '@/util/common-util'
import { DataOptions } from 'vuetify'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import { useCodesStore } from '@/store/codes'
import { useOrgStore } from '@/store/org'
import { useStaffStore } from '@/store/staff'

@Component({})
export default class StaffActiveAccountsTable extends Mixins(PaginationMixin) {
  @Action(useOrgStore) syncOrganization!: (currentAccount: number) => Promise<Organization>
  @Action(useOrgStore) addOrgSettings!: (org: Organization) => Promise<UserSettings>
  @Action(useOrgStore) syncMembership!: (orgId: number) => Promise<Member>
  @Action(useStaffStore) syncSuspendedStaffOrgs!: () => Organization[]
  @State(useStaffStore) suspendedStaffOrgs!: Organization[]
  @Action(useStaffStore) searchOrgs!: (filterParams: OrgFilterParams) => OrgList
  @State(useStaffStore) suspendedReviewCount!: number
  @State(useCodesStore) suspensionReasonCodes!: Code[]

  readonly headerAccounts = [
    {
      text: 'Name',
      align: 'left',
      sortable: false,
      value: 'name'
    },
    {
      text: 'Type',
      align: 'left',
      sortable: false,
      value: 'orgType'
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
      text: 'Reason',
      align: 'left',
      sortable: false,
      value: 'statusCode'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '105'
    }
  ]

  formatDate = CommonUtils.formatDisplayDate

  totalAccountsCount = 0
  tableDataOptions: Partial<DataOptions> = {}
  orgFilter: OrgFilterParams
  isTableLoading: boolean = false
  suspendedOrgs: Organization[] = []

  getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  @Watch('tableDataOptions', { deep: true })
  async getAccounts (val) {
    await this.getOrgs(val?.page, val?.itemsPerPage)
  }

  private async mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
    this.suspendedOrgs = this.suspendedStaffOrgs
    this.totalAccountsCount = this.suspendedReviewCount
  }

  private async getOrgs (page: number = 1, pageLimit: number = this.numberOfItems) {
    // set this variable so that the chip is shown
    try {
      this.orgFilter = {
        statuses: [AccountStatus.NSF_SUSPENDED, AccountStatus.SUSPENDED],
        page: page,
        limit: pageLimit
      // name: appliedFilterValue
      }
      const activeAccountsResp:any = await this.searchOrgs(this.orgFilter)
      this.suspendedOrgs = activeAccountsResp?.orgs
      this.totalAccountsCount = activeAccountsResp?.total || 0
    } catch (error) {
      this.isTableLoading = false
      // eslint-disable-next-line no-console
      console.error(error)
    }
  }

  async view (org: Organization) {
    this.cachePageInfo(this.tableDataOptions)
    let orgId:number = org.id
    await this.syncOrganization(orgId)
    await this.addOrgSettings(org)
    await this.syncMembership(orgId)
    this.$router.push(`/account/${orgId}/settings`)
  }

  formatType (org:Organization):string {
    let orgTypeDisplay = org.orgType === Account.BASIC ? 'Basic' : 'Premium'
    if (org.accessType === AccessType.ANONYMOUS) {
      return 'Director Search'
    }
    if (org.accessType === AccessType.EXTRA_PROVINCIAL) {
      return orgTypeDisplay + ' (out-of-province)'
    }
    return orgTypeDisplay
  }

  getStatusText (org: Organization) {
    if (org.statusCode === AccountStatus.NSF_SUSPENDED) {
      return 'NSF'
    } else if (org.statusCode === AccountStatus.SUSPENDED) {
      return this.getSuspensionReasonCode(org)
    } else {
      return org.statusCode
    }
  }

  private getSuspensionReasonCode (org: Organization) : string {
    return this.suspensionReasonCodes?.find(suspensionReasonCode =>
      suspensionReasonCode?.code === org?.suspensionReasonCode)?.desc
  }
}
</script>

<style lang="scss" scoped>
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
