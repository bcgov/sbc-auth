<template>
  <v-container class="transaction-container">
    <header class="view-header align-center mb-7">
      <h2 class="view-header__title">Transactions</h2>
      <v-btn
        large
        color="primary"
        class="font-weight-bold ml-auto"
        @click="exportCSV"
      >Export CSV</v-btn>
    </header>
    <SearchFilterInput
      :filterParams="searchFilter"
      :filteredRecordsCount="totalTransactionsCount"
      @filter-texts="setAppliedFilterValue"
      :isDataFetchCompleted="isTransactionFetchDone"
    ></SearchFilterInput>
    <TransactionsDataTable
      class="mt-4"
      :transactionFilters="transactionFilterProp"
      :key="updateTransactionTableCounter"
      @total-transaction-count="setTotalTransactionCount"
    ></TransactionsDataTable>
  </v-container>
</template>

<script lang="ts">
import { Account, Pages, SearchFilterCodes } from '@/util/constants'
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { Member, MembershipType, Organization } from '@/models/Organization'
import { TransactionFilter, TransactionFilterParams, TransactionTableList } from '@/models/transaction'
import { mapActions, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import CommonUtils from '@/util/common-util'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import TransactionsDataTable from '@/components/auth/TransactionsDataTable.vue'
import moment from 'moment'

@Component({
  components: {
    TransactionsDataTable,
    SearchFilterInput
  },
  methods: {
    ...mapActions('org', [
      'getTransactionReport'
    ])
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentMembership'
    ])
  }
})
export default class Transactions extends Mixins(AccountChangeMixin) {
  @Prop({ default: '' }) private orgId: string;
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly getTransactionReport!: (filterParams: TransactionFilter) => TransactionTableList
  private updateTransactionTableCounter: number = 0
  private totalTransactionsCount: number = 0
  private searchFilter: SearchFilterParam[] = []
  private transactionFilterProp: TransactionFilter = {} as TransactionFilter
  private isTransactionFetchDone: boolean = false

  private async mounted () {
    this.setAccountChangedHandler(this.initFilter)
    this.initFilter()
  }

  private initializeFilters () {
    this.searchFilter = [
      {
        id: SearchFilterCodes.DATERANGE,
        placeholder: 'Date Range',
        labelKey: 'Date',
        appliedFilterValue: '',
        filterInput: ''
      },
      {
        id: SearchFilterCodes.USERNAME,
        placeholder: 'Initiated by',
        labelKey: 'Initiated by',
        appliedFilterValue: '',
        filterInput: ''
      },
      {
        id: SearchFilterCodes.FOLIONUMBER,
        placeholder: 'Folio Number',
        labelKey: 'Folio Number',
        appliedFilterValue: '',
        filterInput: ''
      }
    ]
    this.isTransactionFetchDone = false
  }

  private setAppliedFilterValue (filters: SearchFilterParam[]) {
    filters.forEach(filter => {
      switch (filter.id) {
        case SearchFilterCodes.DATERANGE:
          this.transactionFilterProp.dateFilter = filter.appliedFilterValue || {}
          break
        case SearchFilterCodes.FOLIONUMBER:
          this.transactionFilterProp.folioNumber = filter.appliedFilterValue
          break
        case SearchFilterCodes.USERNAME:
          this.transactionFilterProp.createdBy = filter.appliedFilterValue
          break
      }
    })
    this.isTransactionFetchDone = false
    this.updateTransactionTableCounter++
  }

  private initFilter () {
    if (this.isTransactionsAllowed) {
      this.initializeFilters()
      this.updateTransactionTableCounter++
    } else {
      // if the account switing happening when the user is already in the transaction page,
      // redirect to account info if its a basic account
      this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
    }
  }

  private setTotalTransactionCount (value) {
    this.totalTransactionsCount = value
    this.isTransactionFetchDone = true
  }

  private async exportCSV () {
    const filterParams: TransactionFilter = this.transactionFilterProp
    const downloadData = await this.getTransactionReport(filterParams)
    CommonUtils.fileDownload(downloadData, `bcregistry-transactions-${moment().format('MM-DD-YYYY')}.csv`, 'text/csv')
  }

  private get isTransactionsAllowed (): boolean {
    return (this.currentOrganization?.orgType === Account.PREMIUM) &&
      [MembershipType.Admin, MembershipType.Coordinator].includes(this.currentMembership.membershipTypeCode)
  }
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .transaction-container {
    overflow: hidden;
  }

  .folio-number-field {
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    max-width: 180px;
  }

  .folio-number-apply-btn {
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
  }

  .date-filter-container {
    .date-range-list {
      border-right: 1px solid #999;
      padding-right: 0;
    }
  }

  .date-range-options {
    width: 15rem;
    border-radius: 0 !important;
    border-right: 1px solid var(--v-grey-lighten1);
  }

  .date-range-label {
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--v-grey-lighten1);
  }

  .v-picker.v-card {
    box-shadow: none !important;
  }

  .filter-results {
    opacity: 0;
    overflow: hidden;
    max-height: 0;
    transition: all ease-out 0.25s;
  }

  .filter-results.active {
    opacity: 1;
    max-height: 4rem;
  }

  .filter-results-label {
    font-weight: 700;
  }

  .v-chip {
    height: 36px;
  }

  ::v-deep {
    .v-text-field--outlined.v-input--dense .v-label {
      top: 14px !important;
    }

    .date-picker-disable {
      .v-date-picker-table {
        pointer-events: none;
      }
    }

    .date-range-label strong {
      margin-right: 0.25rem;
    }

    .v-progress-linear {
      margin-top: -2px !important
    }
  }
</style>
