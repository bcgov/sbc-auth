<template>
  <v-container class="pa-0">
    <DatePicker
      v-show="showDatePicker"
      ref="datePicker"
      :setEndDate="searchParams.endDate"
      :setStartDate="searchParams.startDate"
      @submit="updateDateRange($event)"
    />
    <v-form class="fas-search account-rejected-search">
      <v-row
        dense
        class="row-margin"
      >
        <v-col
          sm="12"
          cols="6"
        >
          <transition name="slide-fade">
            <v-data-table
              v-model:items-per-page="tableDataOptions.itemsPerPage"
              v-model:options="tableDataOptions"
              class="user-list"
              :headers="headerAccounts"
              :items="rejectedTasks"
              :custom-sort="columnSort"
              :no-data-text="$t('noActiveAccountsLabel')"
              :footer-props="{
                itemsPerPageOptions: getPaginationOptions
              }"
              :server-items-length="totalRejectedTasks"
              hide-default-header
              fixed-header
              @update:items-per-page="saveItemsPerPage"
            >
              <template #loading>
                Loading...
              </template>

              <template #header="{}">
                <thead class="v-data-table-header">
                  <tr class="header-row-1">
                    <th
                      v-for="(header, i) in headerAccounts"
                      :key="getIndexedTag('find-header-row', i)"
                      :scope="i"
                      class="font-weight-bold"
                    >
                      {{ header.text }}
                    </th>
                  </tr>

                  <tr
                    id="header-filter-row"
                    class="header-row-2 header-row-2-no-padding"
                  >
                    <th
                      v-for="(header, i) in headerAccounts"
                      :key="getIndexedTag('find-header-row2', i)"
                      :scope="i"
                    >
                      <v-text-field
                        v-if="!['status', 'action', 'dateSubmitted', 'type'].includes(header.value)"
                        :id="header.value"
                        v-model.trim="searchParams[header.value]"
                        input
                        type="search"
                        autocomplete="off"
                        class="text-input-style"
                        filled
                        :placeholder="header.text"
                        dense
                        hide-details="auto"
                      />

                      <div
                        v-else-if="['status'].includes(header.value)"
                        class="mt-0"
                      >
                        <v-select
                          v-model="searchParams[header.value]"
                          :items="statuses"
                          filled
                          item-text="text"
                          item-value="code"
                          data-test="select-status"
                          v-bind="$attrs"
                          hide-details="auto"
                          :menu-props="{ bottom: true, offsetY: true }"
                          v-on="$listeners"
                        />
                      </div>

                      <div
                        v-else-if="['type'].includes(header.value)"
                        class="mt-0"
                      >
                        <v-select
                          v-model="searchParams[header.value]"
                          :items="accountTypes"
                          filled
                          v-bind="$attrs"
                          hide-details="auto"
                          item-text="desc"
                          item-value="val"
                          :menu-props="{ bottom: true, offsetY: true }"
                          class="account-type-list"
                          v-on="$listeners"
                        />
                      </div>

                      <div
                        v-else-if="['dateSubmitted'].includes(header.value)"
                        class="mt-0 pt-5"
                        @click="showDatePicker = true"
                      >
                        <v-text-field
                          v-model="dateTxt"
                          class="text-input-style"
                          append-icon="mdi-calendar"
                          dense
                          filled
                          hide-details="true"
                          :placeholder="header.text"
                        />
                      </div>

                      <v-btn
                        v-else-if="searchParamsExist && header.value === 'action'"
                        outlined
                        color="primary"
                        class="action-btn clear-filter-button"
                        @click="clearSearchParams()"
                      >
                        <span class="clear-filter cursor-pointer">
                          Clear Filters
                          <v-icon
                            small
                            color="primary"
                          >mdi-close</v-icon>
                        </span>
                      </v-btn>
                    </th>
                  </tr>
                </thead>
              </template>
              <template #[`item.dateSubmitted`]="{ item }">
                {{ formatDate(item.dateSubmitted, 'MMM DD, YYYY') }}
              </template>
              <template #[`item.action`]="{ item }">
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
          </transition>
        </v-col>
      </v-row>
    </v-form>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Watch } from 'vue-property-decorator'
import { SessionStorageKeys, TaskRelationshipStatus, TaskStatus } from '@/util/constants'
import { Task, TaskFilterParams, TaskList } from '@/models/Task'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import { DataOptions } from 'vuetify'
import { DatePicker } from '@/components'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { ProductCode } from '@/models/Staff'
import moment from 'moment'
import { namespace } from 'vuex-class'

const TaskModule = namespace('task')

@Component({
  components: {
    DatePicker
  },
  computed: {
    ...mapState('staff', ['products'])
  },
  methods: {
    ...mapActions('staff', ['getProducts'])
  }
})
export default class StaffRejectedAccountsTable extends Mixins(PaginationMixin) {
  @TaskModule.Action('fetchTasks') private fetchTasks!: (filterParams: TaskFilterParams) => TaskList
  private rejectedTasks: Task[] = []
  private taskFilter: TaskFilterParams
  private totalRejectedTasks = 0

  private columnSort = CommonUtils.customSort
  private tableDataOptions: Partial<DataOptions> = {}
  protected searchParamsExist = false
  private datePicker = null
  private dateTxt = ''
  private showDatePicker = false
  private isTableLoading = false

  private readonly getProducts!: () => Promise<ProductCode[]>
  private readonly products!: ProductCode[]

  private readonly headerAccounts = [
    {
      text: 'Date Submitted',
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

  private accountTypes = [
    { desc: 'All', val: '' },
    { desc: 'New Account', val: 'New Account' },
    { desc: 'BCeID Admin', val: 'BCeID Admin' },
    { desc: 'GovM', val: 'GovM' },
    { desc: 'GovN', val: 'GovN' }
  ]

  private searchParams: TaskFilterParams = JSON.parse(ConfigHelper.getFromSession(SessionStorageKeys.RejectedAccountsSearchFilter)) || {
    name: '',
    startDate: '',
    endDate: '',
    type: '',
    modifiedBy: ''
  }

  protected clearSearchParams () {
    this.searchParams = {
      name: '',
      startDate: '',
      endDate: '',
      type: '',
      modifiedBy: ''
    }
    this.dateTxt = ''
  }

  private formatDate = CommonUtils.formatDisplayDate

  @Watch('searchParams', { deep: true, immediate: true })
  async searchChanged (value: TaskFilterParams) {
    this.searchParamsExist = this.doSearchParametersExist(value)
    const itemsPerPage = this.getNumberOfItemsFromSessionStorage() || this.DEFAULT_ITEMS_PER_PAGE
    if (this.cachedPageInfo()) {
      this.tableDataOptions = { ...this.getAndPruneCachedPageInfo(), itemsPerPage }
    } else {
      this.tableDataOptions = { ...this.tableDataOptions, page: 1, itemsPerPage }
    }
    this.setRejectedSearchFilterToStorage(JSON.stringify(value))
  }

  @Watch('tableDataOptions', { deep: true })
  async getStaffTasks (val) {
    await this.searchStaffTasks(val?.page, val?.itemsPerPage)
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  async mounted () {
    await this.getProducts()
    if (this.products) {
      this.products.forEach((element) => {
        this.accountTypes.push({ desc: `Access Request (${element.desc})`, val: element.desc })
      })
    }
    try {
      if (this.searchParams.startDate && this.searchParams.endDate) {
        this.dateTxt = `${moment(this.searchParams.startDate).format('MMM DD, YYYY')} - ${moment(this.searchParams.endDate).format('MMM DD, YYYY')}`
      }
    } catch {
      // Do nothing
    }
  }

  private async searchStaffTasks (page: number = 1, pageLimit: number = this.numberOfItems) {
    // set this variable so that the chip is shown
    try {
      this.taskFilter = {
        ...this.searchParams,
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

  protected doSearchParametersExist (taskFilterParams: TaskFilterParams) {
    return taskFilterParams.name.length > 0 ||
      taskFilterParams.type.length > 0 ||
      taskFilterParams.modifiedBy.length > 0 ||
      taskFilterParams.startDate.length > 0 ||
      taskFilterParams.endDate.length > 0
  }

  private setRejectedSearchFilterToStorage (val: string): void {
    ConfigHelper.addToSession(SessionStorageKeys.RejectedAccountsSearchFilter, val)
  }

  private updateDateRange (event) {
    if (!(event.endDate && event.startDate)) {
      this.dateTxt = ''
    } else {
      this.dateTxt = `${moment(event.startDate).format('MMM DD, YYYY')} - ${moment(event.endDate).format('MMM DD, YYYY')}`
    }

    this.searchParams.startDate = event.startDate
    this.searchParams.endDate = event.endDate
    this.showDatePicker = false
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '~/fas-ui/src/assets/scss/search.scss';

#header-filter-row {
    th {
      padding: 0px 3px 0px 3px !important;
    }
  }

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

.account-rejected-search {
  table>thead>tr>th {
    width: 210px !important;
    min-width: 210px !important;
  }

  // Inline for Clear Filters
  .clear-filter-button {
    padding: 7px !important;
    width: 110px
  }

  .clear-filter {
    line-height: 1.5;
  }

  ::v-deep input,
  ::v-deep .v-select__selection {
    color: #212529 !important;
  }

  ::v-deep ::placeholder {
    color: #495057 !important;
  }

  .v-data-table th {
    font-size: 0.75rem;
  }

  ::v-deep .v-data-footer {
    min-width: 100%;
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

  table>thead>tr>th:last-child {
    width: 130px !important;
    min-width: 130px !important;
  }

  // The TD cells don't seem to be scoped properly.
  // Thus the usage of v-deep.
  ::v-deep tr:hover td:last-child {
    background-color: inherit !important;
  }

  table>thead>tr>th:last-child,
  ::v-deep table>tbody>tr>td:last-child:not([colspan]) {
    position: sticky !important;
    position: -webkit-sticky !important;
    right: 0;
    z-index: 1;
    background: white;
    text-align: right !important;
  }

  ::v-deep table>tbody>tr>td {
    border: 0px;
    padding-top: 0.5rem;
    padding-bottom: 0.5rem;
  }

  ::v-deep table>tbody>tr>td:last-child:not([colspan]) {
    padding-left: 3px !important;
    padding-right: 3px !important;
  }
}
</style>
