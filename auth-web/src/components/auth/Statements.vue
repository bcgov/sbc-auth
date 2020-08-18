<template>
  <v-container>
    <header class="view-header mb-8">
      <h2 class="view-header__title">Statements</h2>
    </header>
    <div>
      <v-data-table
        class="statement-list"
        :headers="headerStatements"
        :items="statementsList"
        :custom-sort="customSortActive"
        :no-data-text="$t('noStatementsList')"
        :server-items-length="totalStatementsCount"
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
        <template v-slot:[`item.dateRange`]="{ item }">
          <div class="font-weight-bold">
            {{formatDateRange(item.startDate, item.endDate)}}
          </div>
        </template>
        <template v-slot:[`item.action`]="{ item }">
          <div class="btn-inline">
            <v-btn
              outlined
              small
              color="primary"
              class="font-weight-bold mr-2"
              :data-test="getIndexedTag('csv-button', item.id)"
              @click="downloadStatement(item, 'CSV')"
            >
              CSV
            </v-btn>
            <v-btn
              outlined
              small
              color="primary"
              class="font-weight-bold"
              :data-test="getIndexedTag('pdf-button', item.id)"
              @click="downloadStatement(item, 'PDF')"
            >
              PDF
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Account, Pages } from '@/util/constants'
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, MembershipType, Organization } from '@/models/Organization'
import { StatementFilterParams, StatementListItem, StatementListResponse } from '@/models/statement'
import { mapActions, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import moment from 'moment'

@Component({
  methods: {
    ...mapActions('org', [
      'getStatementsList'
    ])
  }
})
export default class Statements extends Mixins(AccountChangeMixin) {
  @Prop({ default: '' }) private orgId: string;
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly getStatementsList!: (filterParams: StatementFilterParams) => StatementListResponse
  private readonly ITEMS_PER_PAGE = 5
  private readonly PAGINATION_COUNTER_STEP = 4
  private formatDate = CommonUtils.formatDisplayDate
  private totalStatementsCount: number = 0
  private tableDataOptions: any = {}
  private isDataLoading: boolean = false
  private statementsList: StatementListItem[] = []

  private readonly headerStatements = [
    {
      text: 'Date',
      align: 'left',
      sortable: false,
      value: 'dateRange',
      width: '270'
    },
    {
      text: 'Frequency',
      align: 'left',
      sortable: false,
      value: 'frequency',
      width: '140'
    },
    {
      text: 'Downloads',
      align: 'right',
      sortable: false,
      value: 'action'
    }
  ]

  private get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
  }

  private async mounted () {
    this.setAccountChangedHandler(this.initialize)
    this.initialize()
  }

  private async initialize () {
    await this.loadStatementsList(this.PAGINATION_COUNTER_STEP, this.ITEMS_PER_PAGE)
  }

  formatDateRange (date1, date2) {
    let displayDate = ''
    let dateObj1 = this.getMomentDateObj(date1)
    let dateObj2 = this.getMomentDateObj(date2)
    let year = (dateObj1.year() === dateObj2.year()) ? dateObj1.year() : ''
    let month = (dateObj1.month() === dateObj2.month()) ? dateObj1.format('MMMM') : ''
    if (date1 === date2) {
      return dateObj1.format('MMMM DD, YYYY')
    } else if (year && !month) {
      return `${dateObj1.format('MMMM DD')} - ${dateObj2.format('MMMM DD')}, ${year}`
    } else if (year && month) {
      return `${month} ${dateObj1.date()} - ${dateObj2.date()}, ${year}`
    } else {
      return `${dateObj1.format('MMMM DD, YYYY')} - ${dateObj2.format('MMMM DD, YYYY')}`
    }
  }

  getMomentDateObj (dateStr) {
    return moment(dateStr, 'YYYY-MM-DD')
  }

  @Watch('tableDataOptions', { deep: true })
  async getTransactions (val, oldVal) {
    const pageNumber = val.page || 1
    const itemsPerPage = val.itemsPerPage
    await this.loadStatementsList(pageNumber, itemsPerPage)
  }

  private async loadStatementsList (pageNumber?: number, itemsPerPage?: number) {
    this.isDataLoading = true
    const filterParams: StatementFilterParams = {
      pageNumber: pageNumber,
      pageLimit: itemsPerPage
    }
    const resp = await this.getStatementsList(filterParams)
    this.statementsList = resp?.items || []
    this.totalStatementsCount = resp?.total || 0
    this.isDataLoading = false
  }

  private get isStatementsAllowed (): boolean {
    return (this.currentOrganization?.orgType === Account.PREMIUM) &&
      [MembershipType.Admin, MembershipType.Coordinator].includes(this.currentMembership.membershipTypeCode)
  }

  private customSortActive (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    items.sort((a, b) => {
      return (isDesc) ? (a[index[0]] < b[index[0]] ? -1 : 1) : (b[index[0]] < a[index[0]] ? -1 : 1)
    })
    return items
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private downloadStatement (item, type) {
    // eslint-disable-next-line no-console
    console.log(item, type)
  }
}
</script>

<style lang="scss" scoped>
.view-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.statement-list {
    .v-data-table-header {
      margin-bottom: -2px;
    }
}
</style>
