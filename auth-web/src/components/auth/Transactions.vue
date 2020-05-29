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
                  v-model="dateFilterSelected"
                  color="primary"
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
                >
                  Apply
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  outlined
                >
                  Cancel
                </v-btn>
              </div>
            </v-col>
            <v-col>
              <v-date-picker
                color="primary"
                v-model="dateRangeSelected"
                range
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
          clearable
          hide-details
          height="44"
          class="search-text-field"
        ></v-text-field>
        <v-btn
          color="primary"
          class="font-weight-bold search-button"
          depressed
          large
        >Apply</v-btn>
      </div>
      <v-spacer></v-spacer>
      <v-btn
        color="primary"
        class="font-weight-bold"
        depressed
        large
      >Export</v-btn>
    </div>
    <TransactionsDataTable></TransactionsDataTable>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import TransactionsDataTable from '@/components/auth/TransactionsDataTable.vue'

@Component({
  components: {
    TransactionsDataTable
  }
})
export default class Transactions extends Vue {
  @Prop({ default: '' }) private orgId: string;
  private showDateFilter: boolean = true
  private dateFilterSelected: any = null
  private dateRangeSelected: any = ['2019-07-23', '2019-09-20']

  private readonly dateFilterRanges = [
    {
      label: 'Today',
      code: 'TODAY'
    },
    {
      label: 'Yesterday',
      code: 'YESTERDAY'
    },
    {
      label: 'Last Week',
      code: 'LASTWEEK'
    },
    {
      label: 'Last Month',
      code: 'LASTMONTH'
    },
    {
      label: 'Custom Range',
      code: 'CUSTOMRANGE'
    }
  ]

  openDateFilter () {
    this.showDateFilter = true
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
</style>
