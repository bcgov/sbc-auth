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

      <template v-slot:[`header.status`]="{ header }">
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
      <!-- Need to show detaisl in another tr  -->
      <template
        v-slot:body="{ headers, items }"
        >
        <tbody v-for="item in items"
        class="product-tr-body"
          :key="item.id">
          <tr class="product-tr">
            <td>
              <div class="product-purchased font-weight-bold"
                :data-test="getIndexedTag('transaction-name', item.index)"
                >
                <div class="product-name font-weight-bold"
                  v-for="(name, nameIndex) in item.transactionNames"
                  :key="nameIndex">
                  {{ name }}
                </div>
              </div>
            </td>
            <td>{{item.folioNumber}}</td>
            <td><span style="white-space: nowrap;">{{formatInitiatedBy(item.initiatedBy)}}</span></td>
            <td><span style="white-space: nowrap;">{{formatDate(item.transactionDate, 'MMMM DD, YYYY hh:mm A')}}</span></td>
            <td>
              <div class="font-weight-bold text-right">
                ${{item.totalAmount}}
              </div>
            </td>
            <td>
              <v-chip
                small
                label
                :color="getStatusColor(item.status)"
                class="text-uppercase font-weight-bold mt-n1"
                >
                {{formatStatus(item.status)}}
              </v-chip>
            </td>
          </tr>
          <!-- no tr if no details -->
          <tr class="product-details-tr" v-if="item.details && item.details.length > 0">
            <td :colspan="headers.length">
              <div  v-for="detail in item.details"
                :key="detail && detail.id"
                >
                {{detail && detail.label}}&nbsp;{{detail && detail.value}}
              </div>
            </td>
          </tr>
        </tbody>
      </template>

    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { TransactionFilter, TransactionFilterParams, TransactionTableList, TransactionTableRow } from '@/models/transaction'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import { Organization } from '@/models/Organization'
import { TransactionStatus } from '@/util/constants'

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
  @Prop({ default: () => ({} as TransactionFilter) }) private transactionFilters: TransactionFilter;
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
      text: 'Folio Number',
      align: 'left',
      sortable: false,
      value: 'folioNumber'
    },
    {
      text: 'Initiated by',
      align: 'left',
      sortable: false,
      value: 'initiatedBy',
      width: '170'
    },
    {
      text: 'Date (Pacific Time)',
      align: 'left',
      value: 'transactionDate',
      sortable: false,
      width: '110'
    },
    {
      text: 'Total Amount',
      align: 'right',
      value: 'totalAmount',
      sortable: false
    },
    {
      text: 'Status',
      align: 'left',
      value: 'status',
      sortable: false,
      width: '110'
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
      filterPayload: this.transactionFilters,
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

  private formatInitiatedBy (name) {
    return (name === 'None None') ? '-' : name
  }

  private formatStatus (status) {
    // status show as pending array
    const statusMapToPending = ['Settlement Scheduled', 'PAD Invoice Approved']
    return statusMapToPending.includes(status) ? 'Pending' : status
  }

  private getStatusColor (status) {
    switch (status?.toUpperCase()) {
      case TransactionStatus.COMPLETED.toUpperCase():
        return 'success'
      case TransactionStatus.CANCELLED.toUpperCase():
        return 'error'
      default:
        return ''
    }
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
  th {
    white-space: nowrap;
  }

  td {
    padding-bottom: .5rem !important;
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
.product-tr-body{
  &:hover{
    background: #eee;
  }
  & .product-tr > td {
      border-bottom: none !important;
      padding-top: 1rem !important;
  }

  & tr:last-child > td{
      border-bottom: thin solid rgba(0,0,0,.12) !important;
      padding-bottom: 1rem !important;
  }
}
</style>
