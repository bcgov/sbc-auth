<template>
  <v-data-table
    class="user-list"
    :headers="headerAccounts"
    :items="rejectedOrgs"
    :items-per-page.sync="tableDataOptions.itemsPerPage"
    :hide-default-footer="totalAccountsCount <= tableDataOptions.itemsPerPage"
    :custom-sort="columnSort"
    :no-data-text="$t('noActiveAccountsLabel')"
    :footer-props="{
        itemsPerPageOptions: getPaginationOptions
      }"
    :options.sync="tableDataOptions"
    @update:items-per-page="saveItemsPerPage"
    :server-items-length="totalAccountsCount"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:[`item.action`]="{ item }">
        <v-btn
          outlined
          color="primary"
          class="action-btn"
          :data-test="getIndexedTag('reset-password-button', item.id)"
          @click="view(item)"
        >
          View
        </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Watch } from 'vue-property-decorator'
import { OrgFilterParams, OrgList, Organization } from '@/models/Organization'
import { AccountStatus } from '@/util/constants'
import CommonUtils from '@/util/common-util'
import { DataOptions } from 'vuetify'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { namespace } from 'vuex-class'

const StaffModule = namespace('staff')

@Component({})
export default class StaffRejectedAccountsTable extends Mixins(PaginationMixin) {
  @StaffModule.State('rejectedStaffOrgs') private rejectedStaffOrgs!: Organization[]
  @StaffModule.Action('searchOrgs') private searchOrgs!: (filterParams: OrgFilterParams) => OrgList
  @StaffModule.State('rejectedReviewCount') private rejectedReviewCount!: number

  private columnSort = CommonUtils.customSort

  private tableDataOptions: Partial<DataOptions> = {}

  private readonly headerAccounts = [
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
      text: 'Rejected By',
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

  private orgFilter: OrgFilterParams
  private isTableLoading: boolean = false
  private rejectedOrgs: Organization[] = []
  private totalAccountsCount = 0

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
    this.rejectedOrgs = this.rejectedStaffOrgs
    this.totalAccountsCount = this.rejectedReviewCount
  }

  @Watch('tableDataOptions', { deep: true })
  async getAccounts (val, oldVal) {
    await this.getOrgs(val?.page, val?.itemsPerPage)
  }

  private async getOrgs (page: number = 1, pageLimit: number = this.numberOfItems) {
    try {
      this.orgFilter = {
        statuses: [AccountStatus.REJECTED],
        pageNumber: page,
        pageLimit: pageLimit
      }
      const activeAccountsResp:any = await this.searchOrgs(this.orgFilter)
      this.rejectedOrgs = activeAccountsResp?.orgs
      this.totalAccountsCount = activeAccountsResp?.total || 0
    } catch (error) {
      this.isTableLoading = false
      // eslint-disable-next-line no-console
      console.error(error)
    }
  }

  private view (item) {
    this.cachePageInfo(this.tableDataOptions)
    this.$router.push(`/review-account/${item.id}`)
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
</style>
