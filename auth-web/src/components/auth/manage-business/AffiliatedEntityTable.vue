<template>
  <div id="affiliated-entity-section">
    <v-card flat>
      <div class="table-header">
        <label><strong>My List </strong>{{ entityCount }}</label>
      </div>
      <base-v-data-table
        id="affiliated-entity-table"
        :clearFiltersTrigger="clearFiltersTrigger"
        itemKey="id"
        loadingText="Loading Affiliation Records..."
        noDataText="No Affiliation Records"
        :loading="affiliations.loading"
        :setHeaders="headers"
        :setItems="affiliations.results"
        :totalItems="affiliations.totalResults"
        @update-table-options="tableDataOptions = $event"
        :pageHide="true"
        :filters="affiliations.filters"
        :updateFilter="updateFilter"
      >
      <template v-slot:header-filter-slot-Actions>
        <v-btn
          v-if="affiliations.filters.isActive"
          class="clear-btn mx-auto mt-auto"
          color="primary"
          outlined
          @click="clearFilters()"
        >
          Clear Filters
          <v-icon class="ml-1 mt-1">mdi-close</v-icon>
        </v-btn>
      </template>
      <!-- Name Request Name(s) / Business Name -->
      <template v-slot:item-slot-Name="{ item }">
        <b v-if="isNameRequest(item)" class="col-wide gray-9">
          <b v-for="(name, i) in item.nameRequest.names" :key="`nrName: ${i}`" class="pb-1 names-block">
            <v-icon v-if="isRejectedName(name)" color="red" class="names-text pr-1" small>mdi-close</v-icon>
            <v-icon v-if="isApprovedName(name)" color="green" class="names-text pr-1" small>mdi-check</v-icon>
            <div class="names-text font-weight-bold">{{ name.name }}</div>
          </b>
        </b>
        <b v-else>{{ name(item) }}</b>
      </template>

      <!-- Number -->
      <template v-slot:item-slot-Number="{ item }">
        <span>{{ number(item) }}</span>
      </template>

      <!-- Type -->
      <template v-slot:item-slot-Type="{ item }">
        <div class="gray-9 font-weight-bold">{{ type(item) }}</div>
        <div>{{ typeDescription(item) }}</div>
      </template>

      <!-- Status -->
      <template v-slot:item-slot-Status="{ item }">
        <span>{{ status(item) }}</span>
        <!-- this is mocked here until the backend to get org details in auth is completed -->
        <EntityDetails v-if="name(item) == 'RITVICK 26SEPT'" icon="mdi-alert" showAlertHeader='true' :details="['FROZEN']"/>
        <!-- this works currently -->
        <EntityDetails v-if="isProcessing(status(item))" icon="mdi-information-outline" :details="['PROCESSING']"/>
      </template>

      <!-- Actions -->
      <template v-slot:item-slot-Actions="{ item }">
        <span class="open-action">
          <v-btn
            small
            color="primary"
            min-width="5rem"
            min-height="2rem"
            class="open-action-btn"
            @click="open(item)"
          >
            Open
          </v-btn>
        </span>
      </template>
      </base-v-data-table>
    </v-card>
  </div>
</template>

<script lang='ts'>
import {
  AffiliationTypes,
  BusinessState,
  CorpTypes,
  FilingTypes,
  LDFlags,
  NrDisplayStates,
  NrState,
  NrTargetTypes,
  SessionStorageKeys
} from '@/util/constants'
import { Business, NameRequest, Names } from '@/models/business'
import { Component, Emit, Mixins, Prop, Watch } from 'vue-property-decorator'

import {
  CorpTypeCd,
  GetCorpFullDescription,
  GetCorpNumberedDescription
} from '@bcrs-shared-components/corp-type-module'

import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { Ref, computed, defineComponent, onBeforeMount, onMounted, reactive, ref, watch } from '@vue/composition-api'

import { BaseTableHeaderI } from '@/components/datatable/interfaces'

import BaseVDataTable from '@/components/datatable/BaseVDataTable.vue'

import ConfigHelper from '@/util/config-helper'

import { DEFAULT_DATA_OPTIONS } from '@/components/datatable/resources'
import { DataOptions } from 'vuetify'

import DateMixin from '@/components/auth/mixins/DateMixin.vue'

import EntityDetails from './EntityDetails.vue'

import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import _ from 'lodash'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

import { getAffiliationTableHeaders } from '@/resources/table-headers'
import setup from '@/util/interceptors'

import { useAffiliations } from '@/composables'
import { useStore } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'AffiliatedEntityTable',
  mixins: [DateMixin],
  components: { EntityDetails, BaseVDataTable },
  props: {
    selectedColumns: { default: [] as string[] },
    loading: { default: false }
  },
  setup (props) {
    const isloading = false
    const store = useStore()
    const { loadAffiliations, affiliations, entityCount, clearAllFilters, getHeaders, headers, type, status, updateFilter } = useAffiliations()
    const getSelectedColumns = computed(() => props.selectedColumns)

    /** V-model for dropdown menus. */
    const dropdown = ref([])
    // use reactive to make the dropdown array reactive
    const state = reactive({
      dropdown
    })

    /** Returns true if the affiliation is a numbered IA. */
    const isNumberedIncorporationApplication = (item: Business): boolean => {
      return (
        (item.corpType?.code) === CorpTypes.INCORPORATION_APPLICATION
      )
    }

    /** Returns the name of the affiliation. */
    const name = (item: Business): string => {
      if (isNumberedIncorporationApplication(item)) {
        const legalType: unknown = item.corpSubType?.code
        // provide fallback for old numbered IAs without corpSubType
        return GetCorpNumberedDescription(legalType as CorpTypeCd) || 'Numbered Company'
      }
      return item.name
    }

    /** Returns true if the affiliation is a Name Request. */
    const isNameRequest = (business: Business): boolean => {
      return (!!business.nameRequest)
    }

    /** Returns true if the affiliation is a temporary business. */
    const isTemporaryBusiness = (business: Business): boolean => {
      return (
        (business.corpType?.code || business.corpType) === CorpTypes.INCORPORATION_APPLICATION ||
        (business.corpType?.code || business.corpType) === CorpTypes.REGISTRATION
      )
    }

    /** Returns the identifier of the affiliation. */
    const number = (business: Business): string => {
      if (isNumberedIncorporationApplication(business)) {
        return 'Pending'
      }
      if (isTemporaryBusiness(business)) {
        return business.nrNumber
      }
      if (isNameRequest(business)) {
        return business.nameRequest.nrNumber
      }
      return business.businessIdentifier
    }

    /** Returns true if the name is rejected. */
    const isRejectedName = (name: Names): boolean => {
      return (name.state === NrState.REJECTED)
    }

    /** Returns true if the name is approved. */
    const isApprovedName = (name: Names): boolean => {
      return (name.state === NrState.APPROVED)
    }

    /** Returns the temp business description. */
    const tempDescription = (business: Business): string => {
      switch ((business.corpType?.code || business.corpType) as CorpTypes) {
        case CorpTypes.INCORPORATION_APPLICATION:
          return AffiliationTypes.INCORPORATION_APPLICATION
        case CorpTypes.REGISTRATION:
          return AffiliationTypes.REGISTRATION
        default:
          return '' // should never happen
      }
    }

    /** Returns the type description. */
    const typeDescription = (business: Business): string => {
      // if this is a name request then show legal type
      if (isNameRequest(business)) {
        const legalType: unknown = business.nameRequest.legalType
        return GetCorpFullDescription(legalType as CorpTypeCd)
      }
      // if this is an IA or registration then show legal type
      if (isTemporaryBusiness(business)) {
        const legalType: unknown = (business.corpSubType?.code || business.corpSubType)
        return GetCorpFullDescription(legalType as CorpTypeCd) // may return ''
      }
      // else show nothing
      return ''
    }

    const isProcessing = (state: string): boolean => {
      return NrDisplayStates.PROCESSING === state
    }

    /** Navigation handler for entities dashboard. */
    const goToDashboard = (businessIdentifier: string): void => {
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
      let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`
      window.location.href = appendAccountId(decodeURIComponent(redirectURL))
    }

    /** Navigation handler for Name Request application. */
    const goToNameRequest = (nameRequest: NameRequest): void => {
      ConfigHelper.setNrCredentials(nameRequest)
      window.location.href = appendAccountId(`${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`)
    }

    /** Handler for open action */
    const open = (item: Business): void => {
      if ((item.corpType?.code || item.corpType) === CorpTypes.NAME_REQUEST) {
        goToNameRequest(item.nameRequest)
      } else {
        goToDashboard(item.businessIdentifier)
      }
    }

    // clear filters
    const clearFiltersTrigger = ref(0)
    const clearFilters = () => {
      // clear values in table
      clearFiltersTrigger.value++
      // clear transactions state filters and trigger search
      clearAllFilters()
    }

    /** Apply data table headers dynamically to account for computed properties. */
    // watch(selectedColumns, () => {
    //   headers.value = [
    //     { text: 'Business Name', value: 'name', show: true, filterType: 'text', filterFn: this.parseName, filterLabel: 'Name', width: '30%' },
    //     { text: 'Number', value: 'number', show: this.showCol('Number'), filterType: 'text', filterFn: this.number, filterLabel: 'Number', width: '17%' },
    //     { text: 'Type', value: 'type', show: this.showCol('Type'), filterType: 'select', filterSelections: this.getSelections(this.type), filterFn: this.type, filterLabel: 'Type', width: '25%' },
    //     { text: 'Status', value: 'status', show: this.showCol('Status'), filterType: 'select', filterSelections: this.getSelections(this.status), filterFn: this.status, filterLabel: 'Status', width: '25%' },
    //     { text: 'Actions', value: 'action', show: true, width: '3%' }
    //   ]
    // }, { immediate: true })

    watch(() => props.selectedColumns, (newCol: string[], oldCol: string[]) => {
      getHeaders(newCol)
    })

    onBeforeMount(() => {
      loadAffiliations()
      getHeaders(props.selectedColumns)
    })

    return {
      clearFiltersTrigger,
      clearFilters,
      isloading,
      state,
      headers,
      affiliations,
      entityCount,
      isNameRequest,
      isRejectedName,
      isApprovedName,
      name,
      open,
      number,
      type,
      status,
      isProcessing,
      typeDescription,
      loadAffiliations,
      getSelectedColumns,
      updateFilter
    }
  }
})

</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

#affiliated-entity-section {
  .table-header {
    display: flex;
    background-color: $app-lt-blue;
    padding: .875rem;
  }

  .table-filter {
    color: $gray7;
    font-weight: normal;
    font-size: $px-14;
  }

  .clear-btn {
    width: 130px;
  }

  .names-block {
    display: table;
  }

  .names-text {
    display: table-cell;
    vertical-align: top;
  }

  tbody {
    tr {
      vertical-align: top;

      &:hover {
        background-color: transparent !important;
      }

      td {
        height: 80px !important;
        color: $gray7;
        line-height: 1.125rem;
      }

      td:first-child {
        width: 250px;
      }

      .col-wide {
        width: 325px !important;
      }

      td:not(:first-child):not(:last-child) {
        max-width: 8rem;
      }

      .type-column {
        min-width: 12rem;
      }
    }
  }

  .action-cell {
    max-width: 0;
    max-height: 30px !important;
    text-align: center;
  }

  .actions {
    height:30px;
    width: 140px;

    .open-action {
      border-right: 1px solid $gray1;
    }

    .open-action-btn {
      font-size: .875rem;
      box-shadow: none;
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }

    .more-actions-btn {
      box-shadow: none;
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }

    .v-btn + .v-btn {
      margin-left: 0.5rem;
    }
  }
}

// Vuetify Overrides
::v-deep .theme--light.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled) {
  &:hover {
    background-color: $app-background-blue;
  }
}

::v-deep .v-data-table--fixed-header thead th {
  position: sticky;
  padding-top: 20px;
  padding-bottom: 20px;
  color: $gray9 !important;
  font-size: 0.875rem;
  z-index: 1;
}

::v-deep .theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  .v-icon.v-icon {
    color: $app-blue;
  }
}

::v-deep label {
  font-size: $px-14;
}

// Class binding a vuetify override.
// To handle the sticky elements overlap in the custom scrolling data table.
.header-high-layer {
  ::v-deep {
    th {
      z-index: 2 !important;
    }
  }
}

::v-deep .theme--light.v-data-table .v-data-table__empty-wrapper {
  color: $gray7;
  &:hover {
    background-color: transparent;
  }
}

// Custom Scroll bars
#affiliated-entity-table {
  ::v-deep .v-menu__content {
    margin-left: -5rem;
    margin-right: 1rem;
    text-align: left;
    position: sticky;
    max-width: none;
    z-index: 1 !important;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar {
    width: .625rem;
    overflow-x: hidden
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-track {
    margin-top: 60px;
    box-shadow: inset 0 0 2px rgba(0,0,0,.3);
    overflow: auto;
  }

  ::v-deep .v-data-table__wrapper::-webkit-scrollbar-thumb {
    border-radius: 10px;
    background-color: lightgray;
  }
}
</style>
