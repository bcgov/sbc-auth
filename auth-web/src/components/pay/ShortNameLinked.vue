<template>
  <BaseVDataTable
    id="linked-bank-short-names"
    class="transaction-list"
    :clearFiltersTrigger="clearFiltersTrigger"
    itemKey="id"
    :loading="false"
    loadingText="Loading Transaction Records..."
    noDataText="No Transaction Records"
    :setItems="linkedBankShortNames.results"
    :setHeaders="headers"
    :setTableDataOptions="tableDataOptions"
    title="Linked Bank Short Names"
    :totalItems="linkedBankShortNames.totalResults"
    @update-table-options="tableDataOptions = $event"
  >
    <template #header-filter-slot-actions>
      <v-btn
        v-if="linkedBankShortNames.filters.isActive"
        class="clear-btn mx-auto mt-auto"
        color="primary"
        outlined
        @click="clearFilters()"
      >
        Clear Filters
        <v-icon class="ml-1 mt-1">
          mdi-close
        </v-icon>
      </v-btn>
    </template>
    <!-- header title slots -->
    <template #header-title-slot-statusCode="{ header }">
      {{ header.value }}
      <icon-tooltip icon="mdi-information-outline">
        <div v-html="hello" />
      </icon-tooltip>
    </template>
    <!-- header filter slots -->
    <template #header-filter-slot-createdOn>
      <div>
        <v-text-field
          class="base-table__header__filter__textbox date-filter"
          :append-icon="'mdi-calendar'"
          clearable
          dense
          filled
          hide-details
          :placeholder="'Date'"
          :value="dateRangeSelected ? 'Custom' : ''"
        />
      </div>
    </template>
    <!-- item slots -->
    <template #item-slot-lineItemsAndDetails="{ item }">
      <b
        v-for="lineItem, i in item.lineItems"
        :key="lineItem.description + i"
        class="dark-text"
      >
        {{ lineItem.description }}
      </b><br>
      <span
        v-for="detail, i in item.details"
        :key="detail.label + i"
      >
        {{ detail.label }} {{ detail.value }}
      </span><br>
    </template>
    <template #item-slot-statusCode="{ item }">
      <v-row no-gutters>
        <v-col cols="auto">
          <b>{{ invoiceStatusDisplay[item.statusCode] }}</b>
          <br>
          <span
            v-if="item.updatedOn"
            v-html="item.updatedOn"
          />
        </v-col>
      </v-row>
    </template>
  </BaseVDataTable>
</template>
<script lang="ts">

import { Ref, defineComponent, ref } from '@vue/composition-api'
import { BaseVDataTable } from '..'
import { DEFAULT_DATA_OPTIONS } from '../datatable/resources'
import { DataOptions } from 'vuetify'
import _ from 'lodash'

export default defineComponent({
  name: 'ShortNameLinked',
  components: { BaseVDataTable },
  setup () {
    const headers = [
      {
        col: 'bankShortName',
        customFilter: {
          clearable: true,
          label: 'Bank Short Name',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Bank Short Name'
      },
      {
        col: 'accountName',
        customFilter: {
          clearable: true,
          label: 'Account Name',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Account Name'
      },
      {
        col: 'branchName',
        customFilter: {
          clearable: true,
          label: 'Branch Name',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Branch Name'
      },
      {
        col: 'accountNumber',
        customFilter: {
          clearable: true,
          label: 'Account Number',
          type: 'text',
          value: ''
        },
        hasFilter: true,
        minWidth: '125px',
        value: 'Account Number'
      },
      {
        col: 'actions',
        hasFilter: false,
        minWidth: '164px',
        value: 'Actions',
        width: '164px'
      }
    ]

    const extended = ref(true)

    const clearFilters = () => {
      console.log('clear')
    }

    const linkedBankShortNames = ref({
      results: [
        {
          accountName: 'Test Account',
          accountNumber: 'Test Account Number',
          bankShortName: 'Test Bank Short Name',
          branchName: 'Test Branch Name',
          id: 1
        }
      ],
      totalResults: 0,
      filters: {
        isActive: false
      }
    })

    const tableDataOptions: Ref<DataOptions> = ref(_.cloneDeep(DEFAULT_DATA_OPTIONS) as DataOptions)

    const clearFiltersTrigger = ref(0)

    return {
      clearFilters,
      clearFiltersTrigger,
      headers,
      extended,
      tableDataOptions,
      linkedBankShortNames
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

#linked-bank-short-names {
  border: 1px solid #e9ecef
}
</style>
