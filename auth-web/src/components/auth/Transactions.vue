<template>
  <v-container>
    <header class="view-header mb-8">
      <h2 class="view-header__title">Transactions</h2>
    </header>
    <div class="filter-bar d-flex mb-8">
      <v-menu
        v-model="showDateFilter"
        :close-on-content-click="false"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            depressed
            large
            class="mr-3 px-3"
            color="default"
            v-on="on"
            @click="openDateFilter"
          >
            <v-icon class="mr-2">mdi-calendar-range</v-icon>
            Date Range
            <v-icon class="ml-1">mdi-menu-down</v-icon>
          </v-btn>
        </template>
        <v-card class="date-range-container d-flex">
          <div class="date-range-options d-flex flex-column justify-space-between flex-grow-0 pb-6 pt-3">
            <v-list dense class="py-0"
            >
              <v-list-item-group
                v-model="dateFilterSelectedIndex"
                color="primary"
                @change="dateFilterChange"
              >
                <v-list-item class="py-2 px-6"
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
            <div class="date-filter-btns px-6 mt-4 d-flex flex-end">
              <v-btn large
                color="primary"
                class="font-weight-bold flex-grow-1"
                :disabled="!isApplyFilterBtnValid"
                @click="applyDateFilter"
              >
                Apply
              </v-btn>
              <v-btn large
                outlined
                color="primary"
                class="flex-grow-1 ml-2"
                @click="showDateFilter=false"
              >
                Cancel
              </v-btn>
            </div>
          </div>
          <div class="date-range-calendars pb-6">
            <div class="date-range-label py-6 mx-6 mb-3" v-html="showDateRangeSelected"></div>
            <v-date-picker
              color="primary"
              width="400"
              class="text-center"
              v-model="dateRangeSelected"
              no-title
              range
              :first-day-of-week="1"
              :show-current="false"
              :picker-date="pickerDate"
              @click:date="dateClick"
            ></v-date-picker>
          </div>
        </v-card>
      </v-menu>
      <div class="folio-number-filter d-inline-flex search-input-with-btn">
        <v-text-field
          dense
          filled
          single-line
          hide-details
          height="43"
          class="folio-number-field"
          label="Folio #"
          prepend-inner-icon="mdi-magnify"
          v-model="folioNumberSearch"
        ></v-text-field>
        <v-btn
          color="primary"
          class="folio-number-apply-btn"
          depressed
          large
          :disabled="!folioNumberSearch"
          @click="applyFolioFilter"
        >Apply</v-btn>
      </div>
      <v-spacer></v-spacer>
      <v-btn
        large
        color="primary"
        class="font-weight-bold"
        @click="exportCSV"
      >Export CSV</v-btn>
    </div>
    <div class="filter-results" :class="{ 'active' : filterArray.length }">
      <div class="d-flex align-center mb-8">
        <div class="filter-results-label py-2 mr-7" v-if="filterArray.length">{{totalTransactionsCount}} {{totalTransactionsCount === 1 ? 'record' : 'records'}} found</div>
        <v-chip close label color="info"
          class="mr-2 filter-chip"
          close-icon="mdi-window-close"
          height="36"
          v-for="filter in filterArray"
          :key="filter.type"
          @click:close="clearFilter(filter)"
        >
          {{filter.displayText}}
        </v-chip>
        <v-btn outlined color="primary" class="px-2"
          v-if="filterArray.length"
          @click="clearFilter('', true)"
        >
          Clear all filters
        </v-btn>
      </div>
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
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { TransactionFilterParams, TransactionTableList } from '@/models/transaction'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
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
export default class Transactions extends Mixins(AccountChangeMixin) {
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
  private dateFilterSelectedIndex: number = null
  private dateFilterSelected: any = {}
  private dateFilterProp: any = {}
  private folioFilterProp: string = ''
  private updateTransactionTableCounter: number = 0
  private folioNumberSearch: string = ''
  private filterArray = []
  private totalTransactionsCount: number = 0
  private pickerDate: string = ''

  private async mounted () {
    this.setAccountChangedHandler(this.initFilter)
    this.initFilter()
  }

  private initFilter () {
    this.initDatePicker()
    this.dateFilterProp = {}
    this.dateFilterSelectedIndex = null
    this.dateRangeSelected = []
    this.folioNumberSearch = this.folioFilterProp = ''
    this.filterArray = []
    this.updateTransactionTableCounter++
  }

  private get showDateRangeSelected () {
    let dateText = ''
    if ((this.dateFilterSelected?.code === DATEFILTER_CODES.TODAY) || (this.dateFilterSelected?.code === DATEFILTER_CODES.YESTERDAY)) {
      dateText = `<strong>${this.dateFilterSelected?.label}:</strong> ${CommonUtils.formatDisplayDate(this.dateRangeSelected[0], 'MMM DD, YYYY')}`
    } else {
      dateText = `<strong>${this.dateFilterSelected?.label}:</strong> 
      ${CommonUtils.formatDisplayDate(this.dateRangeSelected[0], 'MMM DD, YYYY')} 
      - ${CommonUtils.formatDisplayDate(this.dateRangeSelected[1], 'MMM DD, YYYY')}`
    }
    return (this.dateFilterSelected?.code) ? dateText : '<strong>No dates selected</strong>'
  }

  // apply filter button enable only if the date ranges are selected and start date <= end date
  private get isApplyFilterBtnValid () {
    if (this.dateRangeSelected?.length === 2 && this.dateRangeSelected[0] > this.dateRangeSelected[1]) {
      this.dateRangeSelected = [this.dateRangeSelected[1], this.dateRangeSelected[0]]
    }
    return this.dateRangeSelected[0] && this.dateRangeSelected[1] && (this.dateRangeSelected[0] <= this.dateRangeSelected[1])
  }

  private initDatePicker () {
    this.dateFilterSelected = (this.dateFilterSelectedIndex) ? this.dateFilterRanges[this.dateFilterSelectedIndex] : {}
  }

  openDateFilter () {
    this.initDatePicker()
    this.showDateFilter = true
  }

  dateFilterChange (val) {
    if (val > -1) {
      this.dateFilterSelected = this.dateFilterRanges[val]
      switch (this.dateFilterSelected?.code) {
        case DATEFILTER_CODES.TODAY:
          const today = this.formatDatePickerDate(moment())
          this.dateRangeSelected = [today, today]
          this.pickerDate = today.slice(0, -3)
          break
        case DATEFILTER_CODES.YESTERDAY:
          const yesterday = this.formatDatePickerDate(moment().subtract(1, 'days'))
          this.dateRangeSelected = [yesterday, yesterday]
          this.pickerDate = yesterday.slice(0, -3)
          break
        case DATEFILTER_CODES.LASTWEEK:
          // Week should start from  Monday and Ends on Sunday
          const weekStart = this.formatDatePickerDate(moment().subtract(1, 'weeks').startOf('isoWeek'))
          const weekEnd = this.formatDatePickerDate(moment().subtract(1, 'weeks').endOf('isoWeek'))
          this.dateRangeSelected = [weekStart, weekEnd]
          this.pickerDate = weekStart.slice(0, -3)
          break
        case DATEFILTER_CODES.LASTMONTH:
          const monthStart = this.formatDatePickerDate(moment().subtract(1, 'months').startOf('month'))
          const monthEnd = this.formatDatePickerDate(moment().subtract(1, 'months').endOf('month'))
          this.dateRangeSelected = [monthStart, monthEnd]
          this.pickerDate = monthStart.slice(0, -3)
          break
        case DATEFILTER_CODES.CUSTOMRANGE:
          this.pickerDate = ''
      }
    }
  }

  private dateClick (date) {
    this.pickerDate = ''
    // ideally it should find using DATEFILTER_CODES.CUSTOMRANGE, but since its static and date click is often, better give the index as it is
    this.dateFilterSelectedIndex = 4 // 4 = Custom Range
    this.dateFilterSelected = this.dateFilterRanges[this.dateFilterSelectedIndex]
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
      this.initFilter()
    } else {
      switch (filter.type) {
        case 'DATE':
          this.dateFilterProp = {}
          this.dateFilterSelectedIndex = null
          this.dateRangeSelected = []
          break
        case 'FOLIO':
          this.folioNumberSearch = this.folioFilterProp = ''
          break
      }
      const index = this.filterArray.findIndex((elem) => elem.type === filter.type)
      if (index > -1) {
        this.filterArray.splice(index, 1)
      }
      this.updateTransactionTableCounter++
    }
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
    CommonUtils.fileDownload(downloadData, `bcregistry-transactions-${moment().format('MM-DD-YYYY')}.csv`, 'text/csv')
  }
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
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

    .v-text-field__slot input {
      font-size: 0.875rem;
    }

    .v-label {
      font-size: 0.875rem !important;
      top: 12px !important;
    }

    .v-input__prepend-inner {
      margin-top: 10px !important;
      margin-right: 5px !important;
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
