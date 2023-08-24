<template>
  <v-container>
    <v-fade-transition>
      <div
        v-if="isLoading"
        class="loading-container"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </v-fade-transition>
    <header class="view-header mb-6">
      <h2 class="view-header__title">
        Statements
      </h2>
      <v-btn
        large
        depressed
        aria-label="Statement Settings"
        title="Open Statement Settings"
        @click.stop="openSettingsModal"
      >
        <v-icon
          small
          class="mr-2 ml-n1"
        >
          mdi-settings
        </v-icon>
        Settings
      </v-btn>
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
        <template #loading>
          Loading...
        </template>
        <template #[`item.dateRange`]="{ item }">
          <div class="font-weight-bold">
            {{ formatDateRange(item.fromDate, item.toDate) }}
          </div>
        </template>
        <template #[`item.action`]="{ item }">
          <div>
            <v-btn
              text
              color="primary"
              class="mr-1"
              aria-label="Download CSV"
              title="Download statement as a CSV file"
              :data-test="getIndexedTag('csv-button', item.id)"
              @click="downloadStatement(item, 'CSV')"
            >
              <v-icon class="ml-n2">
                mdi-file-table-outline
              </v-icon>
              <span class="ml-n1 font-weight-bold">CSV</span>
            </v-btn>
            <v-btn
              text
              color="primary"
              aria-label="Download PDF"
              title="Download statement as a PDF file"
              :data-test="getIndexedTag('pdf-button', item.id)"
              @click="downloadStatement(item, 'PDF')"
            >
              <v-icon class="ml-n2">
                mdi-file-pdf-outline
              </v-icon>
              <span class="ml-n1 font-weight-bold">PDF</span>
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </div>
    <StatementsSettings
      ref="statementSettingsModal"
    />
  </v-container>
</template>

<script lang="ts">
import { Account, Pages } from '@/util/constants'
import { Component, Mixins, Prop, Watch } from 'vue-property-decorator'
import { Member, MembershipType, Organization } from '@/models/Organization'
import { StatementFilterParams, StatementListItem, StatementListResponse } from '@/models/statement'
import { mapActions, mapState } from 'pinia'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import StatementsSettings from '@/components/auth/account-settings/statement/StatementsSettings.vue'
import moment from 'moment'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    StatementsSettings
  },
  methods: {
    ...mapActions(useOrgStore, [
      'getStatementsList',
      'getStatement'
    ])
  },
  computed: {
    ...mapState(useOrgStore, [
      'currentOrganization',
      'currentMembership'
    ])
  }
})
export default class Statements extends Mixins(AccountChangeMixin) {
  @Prop({ default: '' }) private orgId: string
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly getStatementsList!: (filterParams: StatementFilterParams) => StatementListResponse
  private readonly getStatement!: (statementParams: any) => any
  private readonly ITEMS_PER_PAGE = 5
  private readonly PAGINATION_COUNTER_STEP = 4
  private formatDate = CommonUtils.formatDisplayDate
  private totalStatementsCount: number = 0
  private tableDataOptions: any = {}
  private isDataLoading: boolean = false
  private statementsList: StatementListItem[] = []
  private isLoading: boolean = false

  $refs: {
    statementSettingsModal: StatementsSettings
  }

  private readonly headerStatements = [
    {
      text: 'Date',
      align: 'left',
      sortable: false,
      value: 'dateRange'
    },
    {
      text: 'Frequency',
      align: 'left',
      sortable: false,
      value: 'frequency'
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
    if (!this.isStatementsAllowed) {
      // if the account switing happening when the user is already in the statements page,
      // redirect to account info if its a basic account
      this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
    } else {
      await this.loadStatementsList()
    }
  }

  formatDateRange (date1, date2) {
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
  async getTransactions (val) {
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
    return [Account.PREMIUM, Account.STAFF, Account.SBC_STAFF].includes(this.currentOrganization?.orgType as Account) &&
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

  private async downloadStatement (item, type) {
    this.isLoading = true // to avoid rapid download clicks
    try {
      const downloadType = (type === 'CSV') ? 'text/csv' : 'application/pdf'
      const response = await this.getStatement({ statementId: item.id, type: downloadType })
      const contentDispArr = response?.headers['content-disposition'].split('=')
      const fileName = (contentDispArr.length && contentDispArr[1]) ? contentDispArr[1] : `bcregistry-statement-${type.toLowerCase()}`
      CommonUtils.fileDownload(response.data, fileName, downloadType)
      this.isLoading = false
    } catch (error) {
      this.isLoading = false
    }
  }

  private openSettingsModal () {
    this.$refs.statementSettingsModal.openSettings()
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

.loading-container {
  background: rgba(255,255,255, 0.8);
}
</style>
