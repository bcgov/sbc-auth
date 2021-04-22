<template>
  <v-data-table
    class="user-list"
    :headers="headerAccounts"
    :items="pendingOrgs"
    :items-per-page.sync="tableDataOptions.itemsPerPage"
    :hide-default-footer="pendingOrgs.length <= tableDataOptions.itemsPerPage"
    :custom-sort="columnSort"
    :no-data-text="$t('noActiveAccountsLabel')"
    :footer-props="{
        itemsPerPageOptions: getPaginationOptions
      }"
    :options.sync="tableDataOptions"
    :loading="isTableLoading"
    @update:items-per-page="saveItemsPerPage"
    :server-items-length="totalAccountsCount"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:[`item.created`]="{ item }">
      {{formatDate(item.created, 'MMM DD, YYYY')}}
    </template>
    <template v-slot:[`item.action`]="{ item }">
      <div class="btn-inline">
        <v-btn
          outlined
          color="primary"
          :data-test="getIndexedTag('reset-password-button', item.id)"
          @click="review(item)"
        >
          Review
        </v-btn>
      </div>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { AccountStatus, SessionStorageKeys } from '@/util/constants'
import { Component, Mixins, Prop, Watch } from 'vue-property-decorator'
import { OrgFilterParams, OrgList, Organization } from '@/models/Organization'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { mapState } from 'vuex'
import { namespace } from 'vuex-class'

const StaffModule = namespace('staff')

@Component({})
export default class StaffPendingAccountsTable extends Mixins(PaginationMixin) {
  @StaffModule.State('pendingStaffOrgs') private pendingStaffOrgs!: Organization[]
  @StaffModule.Action('searchOrgs') private searchOrgs!: (filterParams: OrgFilterParams) => OrgList
  @StaffModule.State('pendingReviewCount') private pendingReviewCount!: number

  private columnSort = CommonUtils.customSort
  private tableDataOptions: Partial<DataOptions> = {}

  private readonly headerAccounts = [
    {
      text: 'Date Submittted',
      align: 'left',
      sortable: true,
      value: 'created',
      width: '150'
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
  private pendingOrgs: Organization[] = []
  private totalAccountsCount = 0

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
    this.pendingOrgs = this.pendingStaffOrgs
    this.totalAccountsCount = this.pendingReviewCount
  }

  @Watch('tableDataOptions', { deep: true })
  async getAccounts (val, oldVal) {
    await this.getOrgs(val?.page, val?.itemsPerPage)
  }

  private async getOrgs (page: number = 1, pageLimit: number = this.numberOfItems) {
    // set this variable so that the chip is shown
    const appliedFilterValue = ConfigHelper.getFromSession(SessionStorageKeys.OrgSearchFilter) || ''
    try {
      this.orgFilter = {
        statuses: [AccountStatus.PENDING_STAFF_REVIEW],
        pageNumber: page,
        pageLimit: pageLimit
      // name: appliedFilterValue
      }
      const activeAccountsResp:any = await this.searchOrgs(this.orgFilter)
      this.pendingOrgs = activeAccountsResp?.orgs
      this.totalAccountsCount = activeAccountsResp?.total || 0
    } catch (error) {
      this.isTableLoading = false
      // eslint-disable-next-line no-console
      console.error(error)
    }
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private review (item) {
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
