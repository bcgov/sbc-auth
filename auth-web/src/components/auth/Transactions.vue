<template>
  <v-container>
    <header class="view-header mb-6">
      <h2 class="view-header__title">Transactions</h2>
    </header>
    <div class="d-flex mb-7">
      <v-menu
        v-model="showDateFilter"
        :close-on-content-click="false"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            depressed
            large
            class="mr-2"
            color="grey lighten-2"
            v-on="on"
            @click="openDateFilter"
          >
            <v-icon class="mr-2">mdi-calendar</v-icon>
            Date Range
            <v-icon class="ml-1">mdi-menu-down</v-icon>
          </v-btn>
        </template>
        <v-card
          min-width="640"
          class="date-filter-container">
          <v-row>
            <v-col
              cols="4"
              class="date-range-list">
              <v-list
                class="mb-4"
              >
                <v-list-item-group
                  v-model="dateFilterSelectedIndex"
                  color="primary"
                  @change="dateFilterChange"
                >
                  <v-list-item
                    v-for="(filterRange, i) in dateFilterRanges"
                    :key="i"
                  >
                    <v-list-item-content>
                      <v-list-item-title
                        class="font-weight-bold px-1"
                        v-text="filterRange.label"
                      ></v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-list-item-group>
              </v-list>
              <div class="d-flex px-5 py-3">
                <v-btn
                  color="primary"
                  class="font-weight-bold"
                  depressed
                  :disabled="!isApplyFilterBtnValid"
                  @click="applyDateFilter"
                >
                  Apply
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  outlined
                  @click="showDateFilter=false"
                >
                  Cancel
                </v-btn>
              </div>
            </v-col>
            <v-col class="pb-8">
              <h3 class="mt-4 mb-6">
                {{showDateRangeSelected}}
              </h3>
              <v-date-picker
                class="text-center"
                color="primary"
                v-model="dateRangeSelected"
                no-title
                range
                :show-current="false"
                :class="{'date-picker-disable': disableDatePicker}"
                first-day-of-week="1"
              ></v-date-picker>
            </v-col>
          </v-row>
        </v-card>
      </v-menu>
      <div class="d-inline-flex search-input-with-btn">
        <v-text-field
          outlined
          label="Folio #"
          prepend-inner-icon="mdi-magnify"
          single-line
          dense
          v-model="folioNumberSearch"
          hide-details
          height="44"
          class="search-text-field"
        ></v-text-field>
        <v-btn
          color="primary"
          class="font-weight-bold search-button"
          depressed
          large
          :disabled="!folioNumberSearch"
          @click="applyFolioFilter"
        >Apply</v-btn>
      </div>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        class="font-weight-bold"
        depressed
        large
        @click="exportCSV"
      >Export CSV</v-btn>
    </div>
    <div class="d-inline-flex align-center mb-3">
      <h4>{{totalTransactionsCount}} Records found</h4>
      <v-chip
        class="mx-2 filter-chip"
        close
        close-icon="mdi-window-close"
        color="primary"
        label
        v-for="filter in filterArray"
        :key="filter.type"
        @click:close="clearFilter(filter)"
      >
        {{filter.displayText}}
      </v-chip>
      <v-btn
        v-if="filterArray.length"
        text
        color="primary"
        @click="clearFilter('', true)"
      >
        Clear all filters
      </v-btn>
    </div>
    <TransactionsDataTable
      :dateFilter="dateFilterProp"
      :folioFilter="folioFilterProp"
      :key="updateTransactionTableCounter"
      @total-transaction-count="setTotalTransactionCount"
    ></TransactionsDataTable>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { TransactionFilterParams, TransactionTableList } from '@/models/transaction'
import CommonUtils from '@/util/common-util'
import TransactionsDataTable from '@/components/auth/TransactionsDataTable.vue'
import { mapActions } from 'vuex'
import moment from 'moment'

const DATEFILTER_CODES = {
  TODAY: 'TODAY',
  YESTERDAY: 'YESTERDAY',
  LASTWEEK: 'LASTWEEK',
  LASTMONTH: 'LASTMONTH',
  CUSTOMRANGE: 'CUSTOMRANGE'
}

@Component({
  components: {
    TransactionsDataTable
  },
  methods: {
    ...mapActions('org', [
      'getTransactionReport'
    ])
  }
})
export default class Transactions extends Vue {
  @Prop({ default: '' }) private orgId: string;
  private readonly getTransactionReport!: (filterParams: any) => TransactionTableList
  private showDateFilter: boolean = false
  private dateRangeSelected: any = []
  private readonly dateFilterRanges = [
    {
      label: 'Today',
      code: DATEFILTER_CODES.TODAY
    },
    {
      label: 'Yesterday',
      code: DATEFILTER_CODES.YESTERDAY
    },
    {
      label: 'Last Week',
      code: DATEFILTER_CODES.LASTWEEK
    },
    {
      label: 'Last Month',
      code: DATEFILTER_CODES.LASTMONTH
    },
    {
      label: 'Custom Range',
      code: DATEFILTER_CODES.CUSTOMRANGE
    }
  ]
  private dateFilterSelectedIndex: number = 0
  private dateFilterSelected: any = this.dateFilterRanges[this.dateFilterSelectedIndex]
  private dateFilterProp: any = {}
  private folioFilterProp: string = ''
  private updateTransactionTableCounter: number = 0
  private folioNumberSearch: string = ''
  private filterArray = []
  private totalTransactionsCount: number = 0

  private beforeMount () {
    this.initDatePicker()
  }

  private get showDateRangeSelected () {
    if ((this.dateFilterSelected?.code === DATEFILTER_CODES.TODAY) || (this.dateFilterSelected?.code === DATEFILTER_CODES.YESTERDAY)) {
      return `${this.dateFilterSelected.label} - ${CommonUtils.formatDisplayDate(this.dateRangeSelected[0], 'MMM DD, YYYY')}`
    }
    return `${this.dateFilterSelected.label} 
      - ${CommonUtils.formatDisplayDate(this.dateRangeSelected[0], 'MMM DD, YYYY')} 
      - ${CommonUtils.formatDisplayDate(this.dateRangeSelected[1], 'MMM DD, YYYY')}`
  }

  private get disableDatePicker () {
    return this.dateFilterSelected?.code !== DATEFILTER_CODES.CUSTOMRANGE
  }

  // apply filter button enable only if the date ranges are selected and start date <= end date
  private get isApplyFilterBtnValid () {
    return this.dateRangeSelected[0] && this.dateRangeSelected[1] && (this.dateRangeSelected[0] <= this.dateRangeSelected[1])
  }

  private initDatePicker () {
    this.dateRangeSelected = [
      this.formatDatePickerDate(moment(this.dateFilterProp?.startDate)),
      this.formatDatePickerDate(moment(this.dateFilterProp?.endDate))
    ]
    this.dateFilterSelected = this.dateFilterRanges[this.dateFilterSelectedIndex]
  }

  openDateFilter () {
    this.initDatePicker()
    this.showDateFilter = true
  }

  dateFilterChange (val) {
    if (val > -1) {
      this.dateFilterSelected = this.dateFilterRanges[val]
      switch (this.dateFilterSelected.code) {
        case DATEFILTER_CODES.YESTERDAY:
          const yesterday = this.formatDatePickerDate(moment().subtract(1, 'days'))
          this.dateRangeSelected = [yesterday, yesterday]
          break
        case DATEFILTER_CODES.LASTWEEK:
          // Week should start from  Monday and Ends on Sunday
          const weekStart = this.formatDatePickerDate(moment().subtract(1, 'weeks').startOf('isoWeek'))
          const weekEnd = this.formatDatePickerDate(moment().subtract(1, 'weeks').endOf('isoWeek'))
          this.dateRangeSelected = [weekStart, weekEnd]
          break
        case DATEFILTER_CODES.LASTMONTH:
          const monthStart = this.formatDatePickerDate(moment().subtract(1, 'months').startOf('month'))
          const monthEnd = this.formatDatePickerDate(moment().subtract(1, 'months').endOf('month'))
          this.dateRangeSelected = [monthStart, monthEnd]
          break
        case DATEFILTER_CODES.CUSTOMRANGE:
        case DATEFILTER_CODES.TODAY:
          const today = this.formatDatePickerDate(moment())
          this.dateRangeSelected = [today, today]
      }
    }
  }

  // date formatting required by the date picker
  private formatDatePickerDate (dateObj) {
    return dateObj.format('YYYY-MM-DD')
  }

  // filter date desired for the API payload
  private formatDateFilter (dateStr) {
    if (!dateStr) return null
    const [year, month, day] = dateStr.split('-')
    return `${month}/${day}/${year}`
  }

  private applyDateFilter () {
    this.dateFilterProp = this.prepDateFilterObj()
    this.updateTransactionTableCounter++
    this.setFilterArray()
    this.showDateFilter = false
  }

  private prepDateFilterObj () {
    return {
      startDate: this.formatDateFilter(this.dateRangeSelected[0]),
      endDate: this.formatDateFilter(this.dateRangeSelected[1])
    }
  }

  private setFilterArray () {
    this.filterArray = []
    if (this.dateFilterProp?.startDate && this.dateFilterProp?.endDate) {
      this.filterArray.push({
        type: 'DATE',
        displayText: (this.dateFilterProp?.startDate === this.dateFilterProp?.endDate)
          ? CommonUtils.formatDisplayDate(new Date(this.dateFilterProp?.startDate))
          : `${CommonUtils.formatDisplayDate(new Date(this.dateFilterProp?.startDate))} - ${CommonUtils.formatDisplayDate(new Date(this.dateFilterProp?.endDate))}`
      })
    }
    if (this.folioNumberSearch) {
      this.filterArray.push({
        type: 'FOLIO',
        displayText: `Folio: ${this.folioNumberSearch}`
      })
    }
  }

  private clearFilter (filter, isAll: boolean = false) {
    if (isAll) {
      this.dateFilterProp = {}
      this.folioNumberSearch = this.folioFilterProp = ''
      this.dateFilterSelectedIndex = 0
      this.filterArray = []
    } else {
      switch (filter.type) {
        case 'DATE':
          this.dateFilterProp = {}
          this.dateFilterSelectedIndex = 0
          break
        case 'FOLIO':
          this.folioNumberSearch = this.folioFilterProp = ''
          break
      }
      const index = this.filterArray.findIndex((elem) => elem.type === filter.type)
      if (index > -1) {
        this.filterArray.splice(index, 1)
      }
    }
    this.updateTransactionTableCounter++
  }

  private setTotalTransactionCount (value) {
    this.totalTransactionsCount = value
  }

  private applyFolioFilter () {
    this.folioFilterProp = this.folioNumberSearch
    this.updateTransactionTableCounter++
    this.setFilterArray()
  }

  private async exportCSV () {
    const filterParams = {
      dateFilter: this.dateFilterProp,
      folioNumber: this.folioFilterProp
    }
    const downloadData = await this.getTransactionReport(filterParams)
    CommonUtils.fileDownload(downloadData, `bcregistry-transactions-${moment().format('MM-DD-YYYY')}.csv`)
  }
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .search-input-with-btn {
    .search-text-field {
      border-top-right-radius: 0px;
      border-bottom-right-radius: 0px;
      max-width: 180px;
    }
    .search-button {
      border-top-left-radius: 0px;
      border-bottom-left-radius: 0px;
    }
  }

  .date-filter-container {
    .date-range-list {
      border-right: 1px solid #999;
      padding-right: 0;
    }
  }

  ::v-deep {
    .date-picker-disable {
      .v-date-picker-table {
        pointer-events: none;
      }
    }
  }

  .filter-chip {
    font-size: .9rem;
  }

</style>
