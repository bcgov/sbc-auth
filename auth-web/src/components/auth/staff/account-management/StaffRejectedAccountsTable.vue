<template>
  <v-data-table
    class="user-list"
    :headers="headerAccounts"
    :items="rejectedTasks"
    :items-per-page.sync="tableDataOptions.itemsPerPage"
    :custom-sort="columnSort"
    :no-data-text="$t('noActiveAccountsLabel')"
    :footer-props="{
        itemsPerPageOptions: getPaginationOptions
      }"
    :options.sync="tableDataOptions"
    @update:items-per-page="saveItemsPerPage"
    :server-items-length="totalRejectedTasks"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:[`item.dateSubmitted`]="{ item }">
      {{formatDate(item.dateSubmitted, 'MMM DD, YYYY')}}
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
import { Task, TaskFilterParams, TaskList } from '@/models/Task'
import { TaskRelationshipStatus, TaskStatus } from '@/util/constants'
import CommonUtils from '@/util/common-util'
import { DataOptions } from 'vuetify'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { namespace } from 'vuex-class'

const TaskModule = namespace('task')

@Component({
})
export default class StaffRejectedAccountsTable extends Mixins(PaginationMixin) {
  @TaskModule.Action('fetchTasks') private fetchTasks!: (filterParams: TaskFilterParams) => TaskList
  private rejectedTasks: Task[] = []
  private taskFilter: TaskFilterParams
  private totalRejectedTasks = 0

  private columnSort = CommonUtils.customSort
  private tableDataOptions: Partial<DataOptions> = {}
  private isTableLoading: boolean = false

 private readonly headerAccounts = [
   {
     text: 'Date Submittted',
     align: 'left',
     sortable: false,
     value: 'dateSubmitted',
     width: '150'
   },
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
     value: 'type'
   },
   {
     text: 'Rejected By',
     align: 'left',
     sortable: false,
     value: 'modifiedBy'
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

  @Watch('tableDataOptions', { deep: true })
  async getStaffTasks (val, oldVal) {
    await this.searchStaffTasks(val?.page, val?.itemsPerPage)
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
  }

  private async searchStaffTasks (page: number = 1, pageLimit: number = this.numberOfItems) {
    // set this variable so that the chip is shown
    try {
      this.taskFilter = {
        relationshipStatus: TaskRelationshipStatus.REJECTED,
        pageNumber: page,
        pageLimit: pageLimit,
        statuses: [TaskStatus.COMPLETED]
      }
      const rejectedTasksResp = await this.fetchTasks(this.taskFilter)
      this.rejectedTasks = rejectedTasksResp.tasks
      this.totalRejectedTasks = rejectedTasksResp?.total || 0
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
