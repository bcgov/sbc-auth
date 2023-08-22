<template>
  <v-menu
    v-model="showDateFilter"
    :close-on-content-click="false"
  >
    <template #activator="{ on }">
      <v-btn
        block
        depressed
        large
        class="date-range-btn justify-start px-3"
        color="default"
        v-on="on"
        @click="openDateFilter"
      >
        <v-icon class="mr-2">
          mdi-calendar-range
        </v-icon>
        <span class="flex-grow-1 text-left">Date Range</span>
        <v-icon class="ml-1">
          mdi-menu-down
        </v-icon>
      </v-btn>
    </template>
    <v-card class="date-range-container d-flex">
      <div class="date-range-options d-flex flex-column justify-space-between flex-grow-0 pb-6 pt-3">
        <v-list
          dense
          class="py-0"
        >
          <v-list-item-group
            v-model="dateFilterSelectedIndex"
            color="primary"
            @change="dateFilterChange"
          >
            <v-list-item
              v-for="(filterRange, i) in dateFilterRanges"
              :key="i"
              class="py-2 px-6"
            >
              <v-list-item-content>
                <v-list-item-title
                  class="font-weight-bold px-1"
                  v-text="filterRange.label"
                />
              </v-list-item-content>
            </v-list-item>
          </v-list-item-group>
        </v-list>
        <div class="date-filter-btns px-6 mt-4 d-flex flex-end">
          <v-btn
            large
            color="primary"
            class="font-weight-bold flex-grow-1 apply-btn"
            :disabled="!isApplyFilterBtnValid"
            @click="applyDateFilter"
          >
            Apply
          </v-btn>
          <v-btn
            large
            outlined
            color="primary"
            class="flex-grow-1 ml-2 cancel-btn"
            @click="showDateFilter=false"
          >
            Cancel
          </v-btn>
        </div>
      </div>
      <div class="date-range-calendars pb-6">
        <div
          class="date-range-label py-6 mx-6 mb-3"
          v-html="showDateRangeSelected"
        />
        <v-date-picker
          v-model="dateRangeSelected"
          color="primary"
          width="400"
          class="text-center"
          no-title
          range
          :first-day-of-week="1"
          :show-current="false"
          :picker-date="pickerDate"
          @click:date="dateClick"
        />
      </div>
    </v-card>
  </v-menu>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { DateFilterCodes } from '@/util/constants'
import Vue from 'vue'
import moment from 'moment'

export const DATEFILTER_CODES = DateFilterCodes

@Component({})
export default class DateRangeFilter extends Vue {
  @Prop({ default: () => {} }) dateFilterProp: any

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
  private showDateFilter: boolean = false
  private pickerDate: string = ''

  openDateFilter () {
    this.initDatePicker()
    this.showDateFilter = true
  }

  private initDatePicker () {
    if (!this.dateFilterProp) {
      this.dateFilterSelectedIndex = null
      this.dateRangeSelected = []
    }
    this.dateFilterSelected = (this.dateFilterSelectedIndex) ? this.dateFilterRanges[this.dateFilterSelectedIndex] : {}
  }

  // date formatting required by the date picker
  private formatDatePickerDate (dateObj) {
    return dateObj.format('YYYY-MM-DD')
  }

  // filter date desired for the API payload
  private formatDateFilter (dateStr) {
    if (!dateStr) return null
    const [year, month, day] = dateStr.split('-')
    return `${year}-${month}-${day}`
  }

  dateFilterChange (val) {
    if (val > -1) {
      this.dateFilterSelected = this.dateFilterRanges[val]
      switch (this.dateFilterSelected?.code) {
        case DATEFILTER_CODES.TODAY:
          var today = this.formatDatePickerDate(moment())
          this.dateRangeSelected = [today, today]
          this.pickerDate = today.slice(0, -3)
          break
        case DATEFILTER_CODES.YESTERDAY:
          var yesterday = this.formatDatePickerDate(moment().subtract(1, 'days'))
          this.dateRangeSelected = [yesterday, yesterday]
          this.pickerDate = yesterday.slice(0, -3)
          break
        case DATEFILTER_CODES.LASTWEEK:
          // Week should start from  Monday and Ends on Sunday
          var weekStart = this.formatDatePickerDate(moment().subtract(1, 'weeks').startOf('isoWeek'))
          var weekEnd = this.formatDatePickerDate(moment().subtract(1, 'weeks').endOf('isoWeek'))
          this.dateRangeSelected = [weekStart, weekEnd]
          this.pickerDate = weekStart.slice(0, -3)
          break
        case DATEFILTER_CODES.LASTMONTH:
          var monthStart = this.formatDatePickerDate(moment().subtract(1, 'months').startOf('month'))
          var monthEnd = this.formatDatePickerDate(moment().subtract(1, 'months').endOf('month'))
          this.dateRangeSelected = [monthStart, monthEnd]
          this.pickerDate = monthStart.slice(0, -3)
          break
        case DATEFILTER_CODES.CUSTOMRANGE:
          this.pickerDate = ''
      }
    }
  }

  // apply filter button enable only if the date ranges are selected and start date <= end date
  private get isApplyFilterBtnValid () {
    if (this.dateRangeSelected?.length === 2 && this.dateRangeSelected[0] > this.dateRangeSelected[1]) {
      this.dateRangeSelected = [this.dateRangeSelected[1], this.dateRangeSelected[0]]
    }
    return this.dateRangeSelected[0] && this.dateRangeSelected[1] && (this.dateRangeSelected[0] <= this.dateRangeSelected[1])
  }

  private get showDateRangeSelected () {
    let dateText = ''
    if ((this.dateFilterSelected?.code === DATEFILTER_CODES.TODAY) || (this.dateFilterSelected?.code === DATEFILTER_CODES.YESTERDAY)) {
      dateText = `<strong>${this.dateFilterSelected?.label}:</strong> ${CommonUtils.formatDisplayDate(this.dateRangeSelected[0], 'MM-DD-YYYY')}`
    } else {
      dateText = `<strong>${this.dateFilterSelected?.label}:</strong> 
      ${CommonUtils.formatDisplayDate(this.dateRangeSelected[0], 'MM-DD-YYYY')} 
        - ${CommonUtils.formatDisplayDate(this.dateRangeSelected[1], 'MM-DD-YYYY')}`
    }
    return (this.dateFilterSelected?.code) ? dateText : '<strong>No dates selected</strong>'
  }

  private dateClick () {
    this.pickerDate = ''
    // ideally it should find using DATEFILTER_CODES.CUSTOMRANGE, but since its static and date click is often, better give the index as it is
    this.dateFilterSelectedIndex = 4 // 4 = Custom Range
    this.dateFilterSelected = this.dateFilterRanges[this.dateFilterSelectedIndex]
  }

  private applyDateFilter () {
    this.emitDateFilter()
    this.showDateFilter = false
  }

  @Emit()
  private emitDateFilter () {
    return {
      startDate: this.formatDateFilter(this.dateRangeSelected[0]),
      endDate: this.formatDateFilter(this.dateRangeSelected[1])
    }
  }
}
</script>

<style lang="scss" scoped>

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

  .date-picker-disable {
    .v-date-picker-table {
      pointer-events: none;
    }
  }

  .date-range-label strong {
    margin-right: 0.25rem;
  }

  .date-range-calendars {
    .v-picker.v-card {
      box-shadow: none !important;
    }
  }
</style>
