<template>
  <v-container class="transaction-container">
    <header class="view-header align-center mb-7">
      <h2 class="view-header__title">Transactions</h2>
      <div>

        <v-dialog v-model="addFundsDialog" max-width="640">
          <template v-slot:activator="{ attrs }">
            <v-btn
              large
              outlined
              color="primary"
              class="font-weight-bold"
              v-bind="attrs"
              @click="showAddFundsDialog()"
            >
              <v-icon class="mr-2 ml-n2">mdi mdi-plus</v-icon>
              Add Funds
            </v-btn>
          </template>
          <v-card>
            <v-card-title>
              Add Funds
            </v-card-title>
            <v-card-text>
              <form>
                <v-row>
                  <v-col cols="12">
                    <v-select
                      :items="paymentSources"
                      filled
                      hide-details
                      label="Funds Received by"
                    ></v-select>
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12">
                    <v-text-field
                      filled
                      hide-details
                      type="number"
                      label="Amount (CDN)"
                      prepend-inner-icon="mdi-currency-usd"
                      v-model="fundsAmount"
                    >
                    </v-text-field>
                  </v-col>
                </v-row>
                <v-row class="pt-0">
                  <v-col cols="12">
                    <v-menu
                      max-width="350px"
                      ref="dateMenu"
                      v-model="dateMenu"
                      :close-on-content-click="false"
                      :return-value.sync="dateFundsAdded"
                      transition="scale-transition"
                    >
                      <template v-slot:activator="{ on, attrs }">
                        <v-text-field
                          filled
                          v-model="dateFundsAdded"
                          label="Date Funds Received"
                          append-icon="mdi-calendar"
                          readonly
                          v-bind="attrs"
                          v-on="on"
                        ></v-text-field>
                      </template>
                      <v-date-picker
                        no-title
                        full-width
                        v-model="dateFundsAdded"
                        @input="$refs.dateMenu.save(dateFundsAdded)"
                      ></v-date-picker>
                    </v-menu>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col class="d-flex justify-end">
                    <v-btn
                      large
                      color="primary"
                      class="font-weight-bold"
                      @click="addFunds()"
                      :disabled="addingFunds"
                      :loading="addingFunds">
                        Add Funds
                    </v-btn>
                    <v-btn
                      large
                      depressed
                      color="default"
                      class="ml-2"
                      @click="hideAddFundsDialog()">
                        Cancel
                    </v-btn>
                  </v-col>
                </v-row>
              </form>
            </v-card-text>
          </v-card>
        </v-dialog>

        <ModalDialog
          ref="successDialog"
          :show-icon="true"
          :show-actions="true"
          :is-persistent="true"
          :is-scrollable="true"
          dialog-class="notify-dialog"
          max-width="640"
        >

          <template v-slot:icon>
            <v-icon large color="success">mdi-check</v-icon>
          </template>

          <template v-slot:title>
            Funds Added Successfully
          </template>

          <template v-slot:actions>
            <v-btn
              large
              color="success"
              @click="closeSuccessDialog($refs.successDialog)"
            >
              OK
            </v-btn>
          </template>

          <template v-slot:text>
            The amount of <strong>${{fundsAmount}} CDN</strong> was successfully applied to this account.
          </template>
        </ModalDialog>

        <ModalDialog
          ref="errorDialog"
          :show-icon="true"
          :show-actions="true"
          :is-persistent="true"
          :is-scrollable="true"
          dialog-class="notify-dialog"
          max-width="640"
        >

          <template v-slot:icon>
            <v-icon large color="error">mdi-alert-circle-outline</v-icon>
          </template>

          <template v-slot:title>
            An error has occurred
          </template>

          <template v-slot:actions>
            <v-btn
              large
              depressed
              color="default"
              class="font-weight-bold"
              @click="closeSuccessDialog($refs.successDialog)"
            >
              OK
            </v-btn>
          </template>

          <template v-slot:text>
            An error has occurred while attempting to apply funds to this account.<br> Please try again later.
          </template>
        </ModalDialog>

      </div>
    </header>
    <v-divider class="mt-0 mb-8" />
    <div class="d-flex">
      <SearchFilterInput
        :filterParams="searchFilter"
        :filteredRecordsCount="totalTransactionsCount"
        @filter-texts="setAppliedFilterValue"
        :isDataFetchCompleted="isTransactionFetchDone"
      ></SearchFilterInput>
      <v-btn
        large
        depressed
        color="default"
        class="ml-auto font-weight-bold"
        @click="exportCSV"
      >
      Export CSV
      </v-btn>
    </div>

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
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import TransactionsDataTable from '@/components/auth/account-settings/transaction/TransactionsDataTable.vue'
import moment from 'moment'

@Component({
  components: {
    ModalDialog,
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

  $refs: {
    successDialog: ModalDialog
    errorDialog: ModalDialog
  }

  // Prototype Add Funds to Account
  private addFundsDialog: boolean = false
  private errorDialog: boolean = false
  private balanceDue: boolean = true
  private dateMenu: boolean = false
  private dateFundsAdded: null
  private fundsAmount: ''
  private addingFunds: boolean = false
  private paymentSources = [
    'Electronic Funds Transfer (EFT)',
    'Wire Transfer'
  ]

  private transactionsHeaders = [
    {
      text: 'name'
    },
    {
      value: 'value'
    }
  ]

  private transactions = [
    {
      name: 'test', value: 'blah'
    },
    {
      name: 'test', value: 'blah'
    }
  ]

  private showAddFundsDialog () {
    this.addFundsDialog = true
    this.fundsAmount = ''
    this.dateFundsAdded = null
  }

  private hideAddFundsDialog () {
    this.addFundsDialog = false
    this.fundsAmount = ''
    this.dateFundsAdded = null
  }

  private addFunds () {
    this.addingFunds = true
    setTimeout((this.showSuccessDialog), 5000)
  }

  private showSuccessDialog () {
    this.addFundsDialog = false
    this.addingFunds = false
    this.$refs.successDialog.open()
  }

  private closeSuccessDialog () {
    this.$refs.successDialog.close()
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

  .balance-title {
    display: flex;
    align-items: center;
    font-size: 1.5rem;

    .currency {
      margin-top: 2px;
      margin-right: 0.25rem;
      margin-left: 1rem;
      font-size: 0.8em;
      color: var(--v-grey-darken1);
    }
  }
</style>
