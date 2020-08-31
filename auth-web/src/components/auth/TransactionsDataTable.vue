<template>
  <div>
    <v-data-table
      class="transaction-list"
      :headers="headerTranscations"
      :items="transactionList"
      :custom-sort="customSortActive"
      :no-data-text="$t('noTransactionList')"
      :server-items-length="totalTransactionsCount"
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
      <template v-slot:header.status="{ header }">
        {{header.text}}
        <v-tooltip bottom color="grey darken-4">
          <template v-slot:activator="{ on }">
            <v-icon small class="status-tooltip-icon" v-on="on">mdi-information-outline</v-icon>
          </template>
          <div v-for="(status, index) in transactionStatus" :key="index">
            {{status.status}} - {{status.description}}
          </div>
        </v-tooltip>
      </template>
      <template v-slot:item.transactionNames="{ item }">
        <div class="product-purchased font-weight-bold"
          :data-test="getIndexedTag('transaction-name', item.index)"
          >
          <div class="product-name font-weight-bold"
            v-for="(name, nameIndex) in item.transactionNames"
            :key="nameIndex">
            {{ name }}
          </div>
        </div>
        <div
          v-if="item.businessIdentifier"
          :data-test="getIndexedTag('transaction-incorp-number', item.index)"
        >
          Incorporation Number: {{ item.businessIdentifier }}
        </div>
      </template>
      <template v-slot:item.transactionDate="{ item }">
        {{formatDate(item.transactionDate)}}
      </template>
      <template v-slot:item.totalAmount="{ item }">
        <div class="font-weight-bold">
          ${{item.totalAmount}}
        </div>
      </template>
      <template v-slot:item.status="{ item }">
        {{item.status}}
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Account, TransactionStatus } from '@/util/constants'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization, RoleInfo } from '@/models/Organization'
import { Transaction, TransactionFilterParams, TransactionListResponse, TransactionTableList, TransactionTableRow } from '@/models/transaction'
import { mapActions, mapState } from 'vuex'
import { Business } from '@/models/business'
import CommonUtils from '@/util/common-util'

@Component({
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions('org', [
      'getTransactionList'
    ])
  }
})
export default class TransactionsDataTable extends Vue {
  @Prop({ default: undefined }) private dateFilter: any;
  @Prop({ default: '' }) private folioFilter: string;
  private readonly currentOrganization!: Organization
  private readonly getTransactionList!: (filterParams: TransactionFilterParams) => TransactionTableList

  private readonly ITEMS_PER_PAGE = 5
  private readonly PAGINATION_COUNTER_STEP = 4
  private transactionList: TransactionTableRow[] = [];
  private formatDate = CommonUtils.formatDisplayDate
  private totalTransactionsCount = 0
  private isDataLoading = false
  private tableDataOptions: any = {}

  private readonly headerTranscations = [
    {
      text: 'Transaction',
      align: 'left',
      sortable: false,
      value: 'transactionNames'
    },
    {
      text: 'Folio #',
      align: 'left',
      sortable: false,
      value: 'folioNumber',
      width: '140'
    },
    {
      text: 'Initiated By',
      align: 'left',
      sortable: false,
      value: 'initiatedBy'
    },
    {
      text: 'Date',
      align: 'left',
      value: 'transactionDate',
      sortable: false,
      width: '115'
    },
    {
      text: 'Total Amount',
      align: 'right',
      value: 'totalAmount',
      sortable: false,
      width: '125'
    },
    {
      text: 'Status',
      align: 'left',
      value: 'status',
      sortable: false,
      width: '115'
    }
  ]

  private readonly transactionStatus = [
    {
      status: TransactionStatus.COMPLETED.toUpperCase(),
      description: 'Funds received'
    },
    {
      status: TransactionStatus.PENDING.toUpperCase(),
      description: 'Transaction is pending'
    },
    {
      status: TransactionStatus.CANCELLED.toUpperCase(),
      description: 'Transaction is cancelled'
    }
  ]

  private get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
  }

  private async loadTransactionList (pageNumber?: number, itemsPerPage?: number) {
    this.isDataLoading = true
    const filterParams: TransactionFilterParams = {
      filterPayload: {
        dateFilter: this.dateFilter,
        folioNumber: this.folioFilter
      },
      pageNumber: pageNumber,
      pageLimit: itemsPerPage
    }
    const resp = await this.getTransactionList(filterParams)
    this.transactionList = resp?.transactionsList || []
    this.totalTransactionsCount = resp?.total || 0
    this.emitTotalCount()
    this.isDataLoading = false
  }

  @Watch('tableDataOptions', { deep: true })
  async getTransactions (val, oldVal) {
    const pageNumber = val.page || 1
    const itemsPerPage = val.itemsPerPage
    await this.loadTransactionList(pageNumber, itemsPerPage)
  }

  @Emit('total-transaction-count')
  private emitTotalCount () {
    return this.totalTransactionsCount
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private getStatusClass (item) {
    switch (item.status) {
      case TransactionStatus.COMPLETED: return 'status-paid'
      case TransactionStatus.PENDING: return 'status-pending'
      case TransactionStatus.CANCELLED: return 'status-deleted'
      default: return ''
    }
  }

  private customSortActive (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    items.sort((a, b) => {
      return (isDesc) ? (a[index[0]] < b[index[0]] ? -1 : 1) : (b[index[0]] < a[index[0]] ? -1 : 1)
    })
    return items
  }
}
</script>

<style lang="scss" scoped>
.v-list--dense {
  .v-list-item {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }

  .v-list-item .v-list-item__title {
    margin-bottom: 0.25rem;
    font-weight: 700;
  }
}

.status-tooltip-icon {
  margin-top: -4px;
  margin-right: 5px;
  margin-left: 2px;
}

.v-tooltip__content:before {
  content: ' ';
  position: absolute;
  top: -20px;
  left: 50%;
  margin-left: -10px;
  width: 20px;
  height: 20px;
  border-width: 10px 10px 10px 10px;
  border-style: solid;
  border-color: transparent transparent var(--v-grey-darken4) transparent;
}

::v-deep {
  td {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    height: auto;
    vertical-align: top;
    overflow: hidden;
  }

  .transaction-list {
    .v-data-table-header {
      margin-bottom: -2px;
    }

    .product-name {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }
}

thead + thead {
  position: absolute;
  top: -2px;
}
</style>
