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
      @update:items-per-page="saveItemsPerPage"
      :server-items-length="totalAccountsCount"
    >
      <template v-slot:loading>
        Loading...
      </template>
      <template v-slot:[`item.statusCode`]="{ item }">
          <div class="value" aria-labelledby="accountStatus">
              <div class="value__title">
                <v-chip
                  small
                  label
                  class="font-weight-bold account-list__status"
                  color="error"
                >
                  {{ getStatusText(item.statusCode) }}
                </v-chip>
              </div>
            </div>
      </template>
      <template v-slot:[`item.suspendedOn`]="{ item }">
          {{formatDate(item.suspendedOn)}}
      </template>
      <template v-slot:[`item.decisionMadeBy`]="{ item }">
          {{item.decisionMadeBy ? item.decisionMadeBy : 'N/A'}}
      </template>
      <template v-slot:[`item.orgType`]="{ item }">
          {{formatType(item)}}
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
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import { getModule } from 'vuex-module-decorators'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const StaffModule = namespace('staff')
@Component({})
export default class StaffActiveAccountsTable extends Mixins(PaginationMixin) {
  @OrgModule.Action('syncOrganization') private syncOrganization!: (currentAccount: number) => Promise<Organization>
  @OrgModule.Action('addOrgSettings') private addOrgSettings!: (org: Organization) => Promise<UserSettings>
  @OrgModule.Action('syncMembership') private syncMembership!: (orgId: number) => Promise<Member>
  @StaffModule.Action('syncSuspendedStaffOrgs') private syncSuspendedStaffOrgs!: () => Organization[]
  @StaffModule.State('suspendedStaffOrgs') private suspendedStaffOrgs!: Organization[]
  @StaffModule.Action('searchOrgs') private searchOrgs!: (filterParams: OrgFilterParams) => OrgList

  private readonly headerAccounts = [
    {
      text: 'Date Suspended',
      align: 'left',
      sortable: true,
      value: 'suspendedOn'
    },
    {
      text: 'Reason',
      align: 'left',
      sortable: true,
      value: 'statusCode'
    },
    {
      text: 'Name',
      align: 'left',
      sortable: true,
      value: 'name'
    },
    {
      text: 'Type',
      align: 'left',
      sortable: true,
      value: 'orgType'
    },
    {
      text: 'Suspended by',
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
  private suspendedOrgs: Organization[] = []

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  @Watch('tableDataOptions', { deep: true })
  async getAccounts (val, oldVal) {
    await this.getOrgs(val?.page, val?.itemsPerPage)
  }

  private async mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
    this.suspendedOrgs = this.suspendedStaffOrgs
  }

  private async getOrgs (page: number = 1, pageLimit: number = this.numberOfItems) {
    // set this variable so that the chip is shown
    const appliedFilterValue = ConfigHelper.getFromSession(SessionStorageKeys.OrgSearchFilter) || ''
    try {
      this.orgFilter = {
        status: AccountStatus.NSF_SUSPENDED,
        pageNumber: page,
        pageLimit: pageLimit
      // name: appliedFilterValue
      }
      const activeAccountsResp:any = await this.searchOrgs(this.orgFilter)
      this.suspendedOrgs = activeAccountsResp.orgs
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

  private getStatusText (status:string) {
    return status === AccountStatus.NSF_SUSPENDED ? 'NSF' : status
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
