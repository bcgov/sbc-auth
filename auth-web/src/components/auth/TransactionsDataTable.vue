<template>
  <v-data-table
    class="user-list"
    :headers="headerTranscations"
    :items="transactionList"
    :items-per-page="ITEMS_PER_PAGE"
    :hide-default-footer="transactionList.length <= ITEMS_PER_PAGE"
    :footer-props="{
      itemsPerPageOptions: getPaginationOptions
    }"
    :custom-sort="customSortActive"
    :no-data-text="$t('noTransactionList')"
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
      <v-list-item-title
        class="user-name"
        :data-test="getIndexedTag('transaction-name', item.index)"
        >
        <div
          v-for="(name, nameIndex) in item.transactionNames"
          :key="nameIndex">
          {{ name }}
        </div>
      </v-list-item-title>
      <v-list-item-subtitle
        :data-test="getIndexedTag('transaction-sub', item.index)"
      >Business Registry</v-list-item-subtitle>
    </template>
    <template v-slot:item.transactionDate="{ item }">
      {{formatDate(item.transactionDate)}}
    </template>
    <template v-slot:item.totalAmount="{ item }">
      <div class="font-weight-bold">
        ${{item.totalAmount.toFixed(2)}}
      </div>
    </template>
    <template v-slot:item.status="{ item }">
      <div
        class="font-weight-bold"
        v-bind:class="getStatusClass(item)"
      >
        {{item.status}}
      </div>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Account, TransactionStatus } from '@/util/constants'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization, RoleInfo } from '@/models/Organization'
import { Transaction, TransactionDateFilter, TransactionListResponse, TransactionTableList, TransactionTableRow } from '@/models/transaction'
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
  private readonly currentOrganization!: Organization
  private readonly getTransactionList!: (dateFilter: TransactionDateFilter) => TransactionTableList

  private transactionList: TransactionTableRow[] = [];
  private formatDate = CommonUtils.formatDisplayDate
  private readonly ITEMS_PER_PAGE = 10
  private readonly PAGINATION_COUNTER_STEP = 4

  private readonly headerTranscations = [
    {
      text: 'Transaction',
      align: 'left',
      sortable: true,
      value: 'transactionNames'
    },
    {
      text: 'Folio #',
      align: 'left',
      sortable: true,
      value: 'folioNumber'
    },
    {
      text: 'Initiated By',
      align: 'left',
      sortable: true,
      value: 'initiatedBy'
    },
    {
      text: 'Date',
      align: 'left',
      value: 'transactionDate',
      sortable: true
    },
    {
      text: 'Total Amount',
      align: 'left',
      value: 'totalAmount',
      sortable: true
    },
    {
      text: 'Status',
      align: 'left',
      value: 'status',
      sortable: true
    }
  ]

  private readonly transactionStatus = [
    {
      status: TransactionStatus.COMPLETED,
      description: 'Funds received'
    },
    {
      status: TransactionStatus.CREATED,
      description: 'Transaction Created'
    },
    {
      status: TransactionStatus.DELETED,
      description: 'Transaction Deleted'
    }
  ]

  private get getPaginationOptions () {
    let pagination = [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
    pagination[pagination.length - 1] = -1
    return pagination
  }

  private async mounted () {
    this.loadTransactionList()
  }

  private async loadTransactionList () {
    // TODO: Filter using date once filter is done, fetching all records from 2020 for now
    const dateFilter: TransactionDateFilter = {
      'dateFilter': {
        'startDate': '01/01/2020',
        'endDate': '12/31/2020'
      }
    }
    const resp = await this.getTransactionList(dateFilter)
    this.transactionList = resp?.transactionsList || []
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private getStatusClass (item) {
    switch (item.status) {
      case TransactionStatus.COMPLETED: return 'status-paid'
      case TransactionStatus.CREATED: return 'status-pending'
      case TransactionStatus.DELETED: return 'status-deleted'
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
@import '~vuetify/src/styles/styles.sass';
@import '$assets/scss/theme.scss';

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

.role-list {
  width: 20rem;
}

.status-pending {
  color: map-get($grey, darken-1);
}

.status-paid {
  color: map-get($green, darken-1);
}
.status-deleted {
  color: map-get($red, lighten-2);
}

.status-tooltip-icon {
  margin-top: -2px;
  margin-right: 5px;
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
</style>
