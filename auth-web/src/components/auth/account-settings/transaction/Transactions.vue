<template>
  <v-container class="transaction-container">
    <header class="view-header align-center mb-5">
      <h2 class="view-header__title">Transactions</h2>
    </header>
     <section v-if="credit !==0">
       <v-divider class="mb-8"></v-divider>
          <h2>Account Credit: <span class="cad-credit ml-4">CAD</span> ${{credit.toFixed(2)}}</h2>
          <p class="credit-details mt-1">You have a credit of ${{credit.toFixed(2)}} on this account.</p>
       <v-divider class="mb-8 mt-8"></v-divider>
      </section>
    <section>
      <div class="d-flex">
        <v-btn
          large
          color="primary"
          class="font-weight-bold"
          :loading="isLoading"
          @click="exportCSV"
          :disabled="isLoading"
          data-test="btn-export-csv"
        >Export CSV</v-btn>
      </div>
      <TransactionsDataTable
        class="mt-4"
        :transactionFilters="transactionFilterProp"
        :key="updateTransactionTableCounter"
      />
    </section>
  </v-container>
</template>

<script lang="ts">
import { Account, Pages } from '@/util/constants'
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, MembershipType, OrgPaymentDetails, Organization } from '@/models/Organization'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import { TransactionFilter } from '@/models/transaction'
import TransactionsDataTable from '@/components/auth/account-settings/transaction/TransactionsDataTable.vue'

import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component({
  components: {
    TransactionsDataTable,
    SearchFilterInput
  }
})
export default class Transactions extends Mixins(AccountChangeMixin) {
  @Prop({ default: '' }) private orgId: string;

  @OrgModule.State('currentOrganization') private currentOrganization!: Organization
  @OrgModule.State('currentMembership') private currentMembership!: Member
  @OrgModule.State('currentOrgPaymentDetails') private currentOrgPaymentDetails!: OrgPaymentDetails

  @OrgModule.Action('getOrgPayments') private getOrgPayments!: (orgId: number) => OrgPaymentDetails

  private updateTransactionTableCounter: number = 0
  private totalTransactionsCount: number = 0
  private isLoading: boolean = false
  private searchFilter: SearchFilterParam[] = []
  private transactionFilterProp: TransactionFilter = {} as TransactionFilter
  private isTransactionFetchDone: boolean = false
  public credit:any = 0

  private async mounted () {
    this.setAccountChangedHandler(this.initUser)
  }

  private async getPaymentDetails () {
    const { accountId, credit } = this.currentOrgPaymentDetails
    if (!accountId || Number(accountId) !== this.currentOrganization?.id) {
      const paymentDetails: OrgPaymentDetails = await this.getOrgPayments(this.currentOrganization?.id)
      this.credit = paymentDetails.credit && paymentDetails.credit !== null ? paymentDetails.credit : 0
    } else {
      this.credit = credit && credit !== null ? credit : 0
    }
  }

  // private initializeFilters () {
  //   this.searchFilter = [
  //     {
  //       id: SearchFilterCodes.DATERANGE,
  //       placeholder: 'Date Range',
  //       labelKey: 'Date',
  //       appliedFilterValue: '',
  //       filterInput: ''
  //     },
  //     {
  //       id: SearchFilterCodes.USERNAME,
  //       placeholder: 'Initiated by',
  //       labelKey: 'Initiated by',
  //       appliedFilterValue: '',
  //       filterInput: ''
  //     },
  //     {
  //       id: SearchFilterCodes.FOLIONUMBER,
  //       placeholder: 'Folio Number',
  //       labelKey: 'Folio Number',
  //       appliedFilterValue: '',
  //       filterInput: ''
  //     }
  //   ]
  //   this.isTransactionFetchDone = false
  // }

  // private setAppliedFilterValue (filters: SearchFilterParam[]) {
  //   filters.forEach(filter => {
  //     switch (filter.id) {
  //       case SearchFilterCodes.DATERANGE:
  //         this.transactionFilterProp.dateFilter = filter.appliedFilterValue || {}
  //         break
  //       case SearchFilterCodes.FOLIONUMBER:
  //         this.transactionFilterProp.folioNumber = filter.appliedFilterValue
  //         break
  //       case SearchFilterCodes.USERNAME:
  //         this.transactionFilterProp.createdBy = filter.appliedFilterValue
  //         break
  //     }
  //   })
  //   this.isTransactionFetchDone = false
  //   this.updateTransactionTableCounter++
  // }

  private initUser () {
    if (this.isTransactionsAllowed) {
      // this.initializeFilters()
      this.getPaymentDetails()
      // this.updateTransactionTableCounter++
    } else {
      // if the account switing happening when the user is already in the transaction page,
      // redirect to account info if its a basic account
      this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
    }
  }

  // private setTotalTransactionCount (value) {
  //   this.totalTransactionsCount = value
  //   this.isTransactionFetchDone = true
  // }

  private async exportCSV () {
    this.isLoading = true
    // grab from composable**
    // const downloadData = await this.getTransactionReport(filterParams)
    // CommonUtils.fileDownload(downloadData, `bcregistry-transactions-${moment().format('MM-DD-YYYY')}.csv`, 'text/csv')
    this.isLoading = false
  }

  private get isTransactionsAllowed (): boolean {
    return [Account.PREMIUM, Account.STAFF, Account.SBC_STAFF].includes(this.currentOrganization?.orgType as Account) &&
      [MembershipType.Admin, MembershipType.Coordinator].includes(this.currentMembership.membershipTypeCode)
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
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
  .cad-credit {
    font-size: 14px;
    color: $gray6;
  }
  .credit-details {
     color: $gray7;
  }
</style>
