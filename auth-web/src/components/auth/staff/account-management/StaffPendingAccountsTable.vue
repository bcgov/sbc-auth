<template>
  <v-data-table
    class="user-list"
    :headers="headerAccounts"
    :items="staffTasks"
    :server-items-length="totalStaffTasks"
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
    <template v-slot:[`item.dateSubmitted`]="{ item }">
      {{formatDate(item.dateSubmitted, 'MMM DD, YYYY')}}
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
import { Component, Mixins, Prop, Watch } from 'vue-property-decorator'
import { Task, TaskFilterParams, TaskList } from '@/models/Task'
import CommonUtils from '@/util/common-util'
import { DataOptions } from 'vuetify'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { namespace } from 'vuex-class'

const TaskModule = namespace('task')

@Component({
})
export default class StaffPendingAccountsTable extends Mixins(PaginationMixin) {
  @TaskModule.Action('fetchTasks') private fetchTasks!: (filterParams: TaskFilterParams) => TaskList
  private staffTasks: Task[] = []
  private taskFilter: TaskFilterParams
  private totalStaffTasks = 0

  private columnSort = CommonUtils.customSort
  private tableDataOptions: Partial<DataOptions> = {}
  private isTableLoading: boolean = false

  private readonly headerAccounts = [
    {
      text: 'Date Submittted',
      align: 'left',
      sortable: true,
      value: 'dateSubmitted',
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
      value: 'type'
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

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private async searchStaffTasks (page: number = 1, pageLimit: number = this.numberOfItems) {
    // set this variable so that the chip is shown
    try {
      this.taskFilter = {
        pageNumber: page,
        pageLimit: pageLimit
      }
      const staffTasksResp = await this.fetchTasks(this.taskFilter)
      this.staffTasks = staffTasksResp.tasks
      this.totalStaffTasks = staffTasksResp?.total || 0
    } catch (error) {
      this.isTableLoading = false
      // eslint-disable-next-line no-console
      console.error(error)
    }
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
