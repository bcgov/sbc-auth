<template>
  <div>
    <v-row>
      <v-col :cols="colCount" class="d-flex flex-row pt-0 mb-3">
        <div
          v-for="filter in filterParams"
          :key="filter.id"
        >
          <template v-if="isDateRange(filter)">
            <DateRangeFilter
              :dateFilterProp="filter.appliedFilterValue"
              @emit-date-filter="applyDateFilter($event, filter)"
            >
            </DateRangeFilter>
          </template>
          <v-text-field
            v-else
            dense
            filled
            single-line
            hide-details
            height="43"
            class="filter-input mr-2 body-2"
            :placeholder="filter.placeholder"
            v-model="filter.filterInput"
            @keydown.enter="applyFilter"
          ></v-text-field>
        </div>
        <v-btn
          large
          depressed
          color="primary"
          aria-label="Apply Filter"
          title="Apply Filter"
          @click="applyFilter"
          :disabled="!isApplyFilterEnabled"
        >
          Apply Filter
        </v-btn>
      </v-col>
    </v-row>
    <div class="filter-results" :class="{ 'active' : (showFilteredChips && isDataFetchCompleted) }">
      <div class="d-flex align-center mb-8">
        <div class="filter-results-label py-2 mr-4">{{filteredRecordsCount}} {{filteredRecordsCount === 1 ? 'record' : 'records'}} found</div>
        <div
          v-for="filter in filterParams"
          :key="filter.id"
          class="mr-2"
        >
          <v-chip
            close
            label
            color="primary"
            v-if="filter.appliedFilterValue"
            close-icon="mdi-window-close"
            aria-label="Clear Filter"
            :title="`Clear ${filter.placeholder} Filter`"
            @click:close="clearAppliedFilter(filter)"
          >
            <template v-if="filter.labelKey">
              <span class="mr-1">{{filter.labelKey}}:</span>
            </template>
            <template v-if="isDateRange(filter)">
              {{getDateFilterLabel(filter.appliedFilterValue)}}
            </template>
            <template v-else>
              {{filter.appliedFilterValue}}
            </template>
          </v-chip>
        </div>
        <v-btn
          outlined
          color="primary"
          class="px-2"
          aria-label="Clear all filters"
          title="Clear all filters"
          @click="clearAllFilters"
        >
          Clear Filters
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import DateRangeFilter from '@/components/auth/common/DateRangeFilter.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import Vue from 'vue'

@Component({
  components: {
    DateRangeFilter
  }
})
export default class SearchFilterInput extends Vue {
  @Prop({ default: 0 }) filteredRecordsCount: number
  @Prop({ default: [] as SearchFilterParam[] }) filterParams: SearchFilterParam[]
  @Prop({ default: true }) isDataFetchCompleted: boolean

  private filterInput: string = ''
  private appliedFilterValue: string = ''

  private applyFilter () {
    this.filterParams.forEach((filter) => {
      // replace appliedFilterValue only if input is available
      if (filter.filterInput) {
        filter.appliedFilterValue = filter.filterInput
      }
      filter.filterInput = ''
    })
    this.filterTexts()
  }

  @Emit()
  private filterTexts () {
    return this.filterParams
  }

  private clearAppliedFilter (filter) {
    filter.appliedFilterValue = ''
    this.filterTexts()
  }

  private clearAllFilters () {
    this.filterParams.forEach((filter) => {
      filter.appliedFilterValue = ''
    })
    this.filterTexts()
  }

  private get isApplyFilterEnabled () {
    // checks whether any filter input has value
    return this.filterParams.some((filter) => !!(filter.filterInput))
  }

  private get showFilteredChips () {
    // checks whether any filter search has been applied
    return this.filterParams.some((filter) => !!(filter.appliedFilterValue))
  }

  private get colCount () {
    // TODO: may change later once the filter input design finalized
    return (this.filterParams.length * 2) + 4
  }

  private applyDateFilter (dateRangeObj, filter) {
    filter.appliedFilterValue = dateRangeObj
    this.filterTexts()
  }

  private isDateRange (filter) {
    return (filter.id === 'daterange')
  }

  private getDateFilterLabel (appliedFilterValue) {
    return (appliedFilterValue?.startDate === appliedFilterValue?.endDate)
      ? CommonUtils.formatDisplayDate(new Date(appliedFilterValue?.startDate))
      : `${CommonUtils.formatDisplayDate(new Date(appliedFilterValue?.startDate))} - ${CommonUtils.formatDisplayDate(new Date(appliedFilterValue?.endDate))}`
  }
}
</script>

<style lang="scss" scoped>
  .filter-input {
    max-width: 20rem;
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
    height: 36px !important;
  }
</style>
