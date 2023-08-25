<template>
  <div>
    <div class="filter-bar mx-n1">
      <div
        v-for="filter in filterParams"
        :key="filter.id"
        class="filter-item mb-3 px-1"
      >
        <template v-if="isDateRange(filter)">
          <DateRangeFilter
            :dateFilterProp="filter.appliedFilterValue"
            @emit-date-filter="applyDateFilter($event, filter)"
          />
        </template>
        <v-text-field
          v-else
          v-model="filter.filterInput"
          dense
          filled
          hide-details
          class="filter-input"
          :label="filter.placeholder"
          @keydown.enter="applyFilter"
        />
      </div>
      <v-btn
        large
        color="primary"
        aria-label="Apply Filter"
        title="Apply Filter"
        class="apply-filter-btn mx-1 mb-3"
        :disabled="!isApplyFilterEnabled"
        @click="applyFilter"
      >
        Apply Filter
      </v-btn>
    </div>
    <div
      class="filter-results"
      :class="{ 'active' : (showFilteredChips && isDataFetchCompleted) }"
    >
      <div class="filter-results-inner pt-4 pt-md-3">
        <div class="filter-results-label mb-1 mb-md-0 mr-4">
          {{ filteredRecordsCount }} {{ filteredRecordsCount === 1 ? 'record' : 'records' }} found
        </div>
        <div class="filter-results-chips mx-n1">
          <div
            v-for="filter in filterParams"
            :key="filter.id"
          >
            <v-chip
              v-if="filter.appliedFilterValue"
              label
              close
              close-icon="mdi-window-close"
              class="ma-1"
              color="primary"
              aria-label="Clear Filter"
              :title="`Clear ${filter.placeholder} filter`"
              @click:close="clearAppliedFilter(filter)"
            >
              <template v-if="filter.labelKey">
                <span class="mr-1">{{ filter.labelKey }}:</span>
              </template>
              <template v-if="isDateRange(filter)">
                {{ getDateFilterLabel(filter.appliedFilterValue) }}
              </template>
              <template v-else>
                {{ filter.appliedFilterValue }}
              </template>
            </v-chip>
          </div>
          <v-btn
            small
            outlined
            color="primary"
            class="ma-1 px-2"
            height="32"
            aria-label="Clear all filters"
            title="Clear all filters"
            @click="clearAllFilters"
          >
            Clear all filters
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import DateRangeFilter from '@/components/auth/common/DateRangeFilter.vue'
import { SearchFilterCodes } from '@/util/constants'
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

  applyFilter () {
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
  filterTexts () {
    return this.filterParams
  }

  clearAppliedFilter (filter) {
    filter.appliedFilterValue = ''
    this.filterTexts()
  }

  clearAllFilters () {
    this.filterParams.forEach((filter) => {
      filter.appliedFilterValue = ''
    })
    this.filterTexts()
  }

  get isApplyFilterEnabled () {
    // checks whether any filter input has value
    return this.filterParams.some((filter) => !!(filter.filterInput))
  }

  get showFilteredChips () {
    // checks whether any filter search has been applied
    return this.filterParams.some((filter) => !!(filter.appliedFilterValue))
  }

  get colCount () {
    return (this.filterParams.length * 2) + 4
  }

  applyDateFilter (dateRangeObj, filter) {
    filter.appliedFilterValue = dateRangeObj
    this.filterTexts()
  }

  isDateRange (filter) {
    return (filter.id === SearchFilterCodes.DATERANGE)
  }

  getDateFilterLabel (appliedFilterValue) {
    return (appliedFilterValue?.startDate === appliedFilterValue?.endDate)
      ? CommonUtils.formatDisplayDate(appliedFilterValue?.startDate)
      : `${CommonUtils.formatDisplayDate(appliedFilterValue?.startDate)} - ${CommonUtils.formatDisplayDate(appliedFilterValue?.endDate)}`
  }
}
</script>

<style lang="scss" scoped>
  // Custom Styling for reduced height inputs
  ::v-deep {
    .v-text-field--filled .v-label {
      font-size: 0.875rem;
    }

    .v-input__control,
    .v-input__slot {
      height: 44px !important;
      min-height: 44px !important;
    }

    .v-text-field--filled {
      &.v-input--dense {
        .v-label {
          top: 13px;
        }
        .v-label--active {
          transform: translateY(-8px) scale(0.75);
        }
      }

      &:not(.v-text-field--single-line) {
        input {
          margin-top: 14px;
        }
      }
    }
  }

  // Filter Bar
  .filter-bar {
    align-items: center;
  }

  .filter-item {
    flex: 1 1 auto;
  }

  @media (min-width: 1024px) {
    .filter-bar {
      display: flex;
      flex-direction: row;
    }

    .filter-item {
      max-width: 12rem;
      flex: 0 0 auto;
    }
  }

  // Filter Results
  .filter-results {
    opacity: 0;
    overflow: hidden;
    max-height: 0;
    transition: all ease-out 0.25s;
    visibility: hidden;
  }

  .filter-results.active {
    opacity: 1;
    max-height: 12rem;
    visibility: visible;
  }

  .filter-results-label {
    font-weight: 700;
  }

  .filter-results-chips {
    div {
      display: inline-block;
    }
  }

  @media (min-width: 1024px) {
    .filter-results-inner {
      display: flex;
      flex-direction: row;
      align-items: center;
    }
  }
</style>
