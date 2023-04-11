<template>
  <v-container>
    <v-fade-transition>
      <div v-if="isLoading" class="loading-container">
        <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
      </div>
    </v-fade-transition>
    <header class="view-header mb-6">
      <h2 class="view-header__title">Activity Log</h2>
    </header>
    <div>
      <v-data-table
        class="activity-list"
        :headers="activityHeader"
        :items="activityList"
        :no-data-text="$t('noActivityLogList')"
        :server-items-length="totalActivityCount"
        :options.sync="tableDataOptions"
        :loading="isDataLoading"
        loading-text="loading text"
        :footer-props="{
          itemsPerPageOptions: getPaginationOptions
        }"
      >
        <template v-slot:loading>
          Loading...
        </template>
        <template v-slot:[`item.created`]="{ item }">
          <div class="font-weight-bold">
            {{formatDate(item.created,'MMMM DD, YYYY')}}
          </div>
        </template>
      </v-data-table>
    </div>

  </v-container>
</template>

<script lang="ts">
import { ActivityLog, ActivityLogFilterParams } from '@/models/activityLog'

import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { Member, Organization } from '@/models/Organization'
import CommonUtils from '@/util/common-util'
import { Component, Mixins, Prop, Watch } from 'vue-property-decorator'

import { namespace } from 'vuex-class'

const ActivityLogModule = namespace('activity')
const OrgModule = namespace('org')

@Component({})
export default class ActivityLogs extends Mixins(AccountChangeMixin) {
  @Prop({ default: '' }) private orgId: number;
  @OrgModule.State('currentOrganization') public currentOrganization!: Organization
  @OrgModule.State('currentMembership') public currentMembership!: Member
  @ActivityLogModule.State('currentOrgActivity') public currentOrgActivity!: ActivityLog
  @ActivityLogModule.Action('getActivityLog') public getActivityLog!:(filterParams:ActivityLogFilterParams) =>Promise<ActivityLog>

  private readonly ITEMS_PER_PAGE = 5
  private readonly PAGINATION_COUNTER_STEP = 4
  public formatDate = CommonUtils.formatDisplayDate
  public totalActivityCount: number = 0
  public tableDataOptions: any = {}
  public isDataLoading: boolean = false
  public activityList: ActivityLog[] = []
  public isLoading: boolean = false

  public readonly activityHeader = [
    {
      text: 'Date',
      align: 'left',
      sortable: false,
      value: 'created',
      class: 'bold-header'
    },

    {
      text: 'Initiated by',
      align: 'left',
      sortable: false,
      value: 'actor',
      class: 'bold-header'
    },
    {
      text: 'Subject',
      align: 'left',
      sortable: false,
      value: 'action',
      class: 'bold-header'
    }
  ]

  public get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
  }

  public async mounted () {
    this.setAccountChangedHandler(this.initialize)
    this.initialize()
  }

  public async initialize () {
    await this.loadActivityList()
  }

  @Watch('tableDataOptions', { deep: true })
  async getActivityLogs (val) {
    const pageNumber = val?.page || 1
    const itemsPerPage = val?.itemsPerPage
    await this.loadActivityList(pageNumber, itemsPerPage)
  }

  public async loadActivityList (pageNumber?: number, itemsPerPage?: number) {
    this.isDataLoading = true
    const filterParams: ActivityLogFilterParams = {
      pageNumber: pageNumber,
      pageLimit: itemsPerPage,
      orgId: this.currentOrganization.id
    }
    try {
      const resp:any = await this.getActivityLog(filterParams)
      this.activityList = resp?.activityLogs || []
      this.totalActivityCount = resp?.total || 0
      this.isDataLoading = false
    } catch {
      this.activityList = []
      this.totalActivityCount = 0
      this.isDataLoading = false
    }
  }
}
</script>

<style lang="scss" scoped>
.view-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.sactivitylist {
  .v-data-table-header {
    margin-bottom: -2px;
  }
}

.loading-container {
  background: rgba(255,255,255, 0.8);
}

</style>
