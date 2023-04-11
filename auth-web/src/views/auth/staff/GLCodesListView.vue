<template>
  <v-container class="pa-0">
    <header class="view-header mb-8">
      <h2 class="view-header__title">General Ledger Codes</h2>
    </header>
    <!-- The below code is for filter, can be enabled once filter story is available -->
    <div class="filter-bar d-flex mb-8" v-if="false">
      <div class="client-search-filter d-inline-flex search-input-with-btn">
        <v-text-field
          dense
          filled
          single-line
          hide-details
          height="43"
          class="client-search-field"
          label="Client"
          prepend-inner-icon="mdi-magnify"
          v-model="clientSearch"
        ></v-text-field>
        <v-btn
          color="primary"
          class="client-search-apply-btn"
          depressed
          large
          :disabled="!clientSearch"
          @click="applyClientSearchFilter"
        >Apply</v-btn>
      </div>
    </div>
    <div class="filter-results" :class="{ 'active' : clientSearchProp.length }">
      <div class="d-flex align-center mb-8">
        <div class="filter-results-label py-2 mr-7" v-if="clientSearchProp.length">{{totalGLRecordCount}} {{totalGLRecordCount === 1 ? 'record' : 'records'}} found</div>
        <v-chip close label color="info"
          class="mr-2 filter-chip"
          close-icon="mdi-window-close"
          height="36"
          v-for="filter in clientSearchProp"
          :key="filter"
          @click:close="clearFilter(filter)"
        >
          {{filter}}
        </v-chip>
        <v-btn outlined color="primary" class="px-2"
          v-if="clientSearchProp.length"
          @click="clearFilter('', true)"
        >
          Clear all filters
        </v-btn>
      </div>
    </div>
    <GLCodesDataTable
      :clientSearch="clientSearchProp"
      :key="updateGLCodeTableCounter"
    ></GLCodesDataTable>
  </v-container>
</template>

<script lang="ts">
import GLCodesDataTable from '@/components/auth/staff/gl-code/GLCodesDataTable.vue'
import { Component, Vue } from 'vue-property-decorator'

@Component({
  components: {
    GLCodesDataTable
  }
})
export default class GLCodesListView extends Vue {
  private clientSearchProp: string[] = []
  private updateGLCodeTableCounter: number = 0
  private clientSearch: string = ''
  private filterArray = []
  private totalGLRecordCount: number = 0

  private async mounted () {
  }

  private clearFilter (filter, isAll: boolean = false) {
    this.clientSearch = ''
    if (isAll) {
      this.clientSearchProp = []
    } else {
      const index = this.clientSearchProp.findIndex((elem) => elem === filter)
      if (index > -1) {
        this.filterArray.splice(index, 1)
      }
    }
    this.updateGLCodeTableCounter++
  }

  private applyClientSearchFilter () {
    this.clientSearchProp.push(this.clientSearch)
    this.updateGLCodeTableCounter++
    this.clientSearch = ''
  }
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  .client-search-field {
    border-top-right-radius: 0px;
    border-bottom-right-radius: 0px;
    max-width: 180px;
  }

  .client-search-apply-btn {
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
