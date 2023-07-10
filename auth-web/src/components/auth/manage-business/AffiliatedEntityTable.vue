<template>
  <div id="affiliated-entity-section">
    <v-card flat>
      <div class="table-header">
        <label><strong>My List </strong>({{ entityCount }})</label>
      </div>
      <base-v-data-table
        id="affiliated-entity-table"
        :clearFiltersTrigger="clearFiltersTrigger"
        itemKey="businessIdentifier"
        loadingText="Loading Affiliation Records..."
        noDataText="No Affiliation Records"
        :loading="affiliations.loading"
        :setHeaders="headers"
        :setItems="affiliations.results"
        :totalItems="affiliations.totalResults"
        :filters="affiliations.filters"
        :updateFilter="updateFilter"
        :height="entityCount > 5 ? '32rem' : null"
        :pageHide="true"
        :fixedHeader="true"
        :highlight-index="highlightIndex"
        highlight-class='base-table__item-row-green'
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
        <b v-else class="col-wide gray-9 font-weight-bold">{{ name(item) }}</b>
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
        <EntityDetails v-if="isExpired(item) ||
                      isFrozed(item) ||
                      isBadstanding(item) ||
                      isDissolution(item) "
                      icon="mdi-alert"
                      :showAlertHeader="true"
                      :details="getDetails(item)"/>
        <EntityDetails v-if="isProcessing(status(item))" icon="mdi-information-outline" :details="[EntityAlertTypes.PROCESSING]"/>
      </template>

      <!-- Actions -->
      <template v-slot:item-slot-Actions="{ item, index }">
        <div class="actions mx-auto" :id="`action-menu-${index}`">
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
            <!-- More Actions Menu -->
            <span class="more-actions">
              <v-menu
                :attach="`#action-menu-${index}`"
                v-model="dropdown[index]"
              >
                <template v-slot:activator="{ on }">
                  <v-btn
                    small
                    color="primary"
                    min-height="2rem"
                    class="more-actions-btn"
                    v-on="on"
                  >
                    <v-icon>{{dropdown[index] ? 'mdi-menu-up' : 'mdi-menu-down'}}</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item
                    v-if="canUseNameRequest(item)"
                    class="actions-dropdown_item my-1"
                    data-test="use-name-request-button"
                    @click="useNameRequest(item)"
                  >
                    <v-list-item-subtitle>
                      <v-icon small>mdi-file-certificate-outline</v-icon>
                      <span class="pl-1">Use this Name Request Now</span>
                    </v-list-item-subtitle>
                  </v-list-item>
                  <v-list-item
                    class="actions-dropdown_item my-1"
                    data-test="remove-button"
                    v-can:REMOVE_BUSINESS.disable
                    @click="removeBusiness(item)"
                  >
                    <v-list-item-subtitle v-if="isTemporaryBusiness(item)">
                      <v-icon small>mdi-delete-forever</v-icon>
                      <span class="pl-1">Delete {{tempDescription(item)}}</span>
                    </v-list-item-subtitle>
                    <v-list-item-subtitle v-else>
                      <v-icon small>mdi-delete</v-icon>
                      <span class="pl-1">Remove From Table</span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-menu>
            </span>
          </span>
        </div>
      </template>
      </base-v-data-table>
    </v-card>
  </div>
</template>

<script lang='ts'>
import {
  AffiliationTypes,
  CorpTypes,
  EntityAlertTypes,
  FilingTypes,
  NrDisplayStates,
  NrState,
  NrTargetTypes,
  SessionStorageKeys
} from '@/util/constants'
import { Business, NameRequest, Names } from '@/models/business'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { SetupContext, computed, defineComponent, ref, watch } from '@vue/composition-api'
import { BaseVDataTable } from '@/components'
import ConfigHelper from '@/util/config-helper'
import DateMixin from '@/components/auth/mixins/DateMixin.vue'
import { Emit } from 'vue-property-decorator'
import EntityDetails from './EntityDetails.vue'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'
import { useAffiliations } from '@/composables'
import { useStore } from 'vuex-composition-helpers'

export default defineComponent({
  name: 'AffiliatedEntityTable',
  components: { EntityDetails, BaseVDataTable },
  props: {
    selectedColumns: { default: [] as string[] },
    loading: { default: false },
    highlightIndex: { default: -1 }
  },
  emits: ['add-unknown-error'],
  mixins: [DateMixin],
  setup (props, context: SetupContext) {
    const isloading = false
    const store = useStore()
    const { loadAffiliations, affiliations, entityCount, clearAllFilters,
      getHeaders, headers, type, status, updateFilter, typeDescription,
      isNameRequest, number, name, canUseNameRequest, tempDescription,
      isTemporaryBusiness } = useAffiliations()
    const currentOrganization = computed(() => store.state.org.currentOrganization as Organization)

    const createNamedBusiness = ({ filingType, business }: { filingType: FilingTypes, business: Business}) => {
      return store.dispatch('business/createNamedBusiness', { filingType, business })
    }

    /** V-model for dropdown menus. */
    const dropdown: Array<boolean> = []

    /** Returns true if the name is rejected. */
    const isRejectedName = (name: Names): boolean => {
      return (name.state === NrState.REJECTED)
    }

    /** Returns true if the name is approved. */
    const isApprovedName = (name: Names): boolean => {
      return (name.state === NrState.APPROVED)
    }

    const isDraft = (state: string): boolean => {
      return NrState.DRAFT === state.toUpperCase()
    }

    const isIA = (type: string): boolean => {
      return (type === AffiliationTypes.INCORPORATION_APPLICATION || type === AffiliationTypes.REGISTRATION)
    }

    const isProcessing = (state: string): boolean => {
      return NrDisplayStates.PROCESSING === state
    }

    /** Draft IA with Expired NR */
    const isExpired = (item: Business): boolean => {
      return isDraft(status(item)) && (item.nameRequest && (item.nameRequest.expirationDate !== null) &&
        (new Date(item.nameRequest.expirationDate) < new Date())) && isIA(type(item))
    }

    const isFrozed = (item: Business): boolean => {
      return item.adminFreeze
    }
    const isBadstanding = (item: Business) => {
      return !item.goodStanding
    }

    /** Returns true if the business is dissolved. */
    const isDissolution = (item: Business) => {
      return item.dissolved
    }

    const getDetails = (item: Business): EntityAlertTypes[] => {
      const details = []
      if (isExpired(item)) {
        details.push(EntityAlertTypes.EXPIRED)
      }
      if (isFrozed(item)) {
        details.push(EntityAlertTypes.FROZEN)
      }
      if (isBadstanding(item)) {
        details.push(EntityAlertTypes.BADSTANDING)
      }
      if (isDissolution(item)) {
        details.push(EntityAlertTypes.DISSOLUTION)
      }
      return details
    }

    /** Create a business record in LEAR. */
    const createBusinessRecord = async (business: Business): Promise<string> => {
      const regTypes = [CorpTypes.SOLE_PROP, CorpTypes.PARTNERSHIP]
      const iaTypes = [CorpTypes.BENEFIT_COMPANY, CorpTypes.COOP, CorpTypes.BC_CCC, CorpTypes.BC_COMPANY,
        CorpTypes.BC_ULC_COMPANY]

      let filingResponse = null

      if (regTypes.includes(business.nameRequest?.legalType)) {
        filingResponse = await createNamedBusiness({ filingType: FilingTypes.REGISTRATION, business })
      } else if (iaTypes.includes(business.nameRequest?.legalType)) {
        filingResponse = await createNamedBusiness({ filingType: FilingTypes.INCORPORATION_APPLICATION, business })
      }

      if (filingResponse?.errorMsg) {
        context.emit('add-unknown-error')
        return ''
      }
      return filingResponse.data.filing.business.identifier
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

    /** Navigation handler for OneStop application */
    const goToOneStop = (): void => {
      window.location.href = appendAccountId(ConfigHelper.getOneStopUrl())
    }

    /** Navigation handler for Corporate Online application */
    const goToCorpOnline = (): void => {
      window.location.href = appendAccountId(ConfigHelper.getCorporateOnlineUrl())
    }

    /** Handler for draft IA creation and navigation */
    const useNameRequest = async (item: Business) => {
      switch (item.nameRequest.target) {
        case NrTargetTypes.LEAR:
        // Create new IA if the selected item is Name Request
          let businessIdentifier = item.businessIdentifier
          if (item.corpType.code === CorpTypes.NAME_REQUEST) {
            businessIdentifier = await createBusinessRecord(item)
          }
          goToDashboard(businessIdentifier)
          break
        case NrTargetTypes.ONESTOP:
          goToOneStop()
          break
        case NrTargetTypes.COLIN:
          goToCorpOnline()
          break
      }
    }

    /** Emit business/nr information to be unaffiliated. */
    const removeBusiness = (business: Business): RemoveBusinessPayload => {
      const payload = {
        orgIdentifier: currentOrganization.value.id,
        business
      }

      context.emit('remove-business', payload)
      return payload
    }

    // clear filters
    const clearFiltersTrigger = ref(0)
    const clearFilters = () => {
      // clear values in table
      clearFiltersTrigger.value++
      // clear affiliation state filters and trigger search
      clearAllFilters()
    }

    watch(() => props.selectedColumns, (newCol: string[]) => {
      getHeaders(newCol)
    })

    watch(() => affiliations.results, () => {
      clearFilters()
      getHeaders(props.selectedColumns)
    })

    return {
      clearFiltersTrigger,
      clearFilters,
      isloading,
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
      isDraft,
      typeDescription,
      loadAffiliations,
      updateFilter,
      dropdown,
      canUseNameRequest,
      useNameRequest,
      removeBusiness,
      isTemporaryBusiness,
      tempDescription,
      EntityAlertTypes,
      isExpired,
      getDetails,
      isFrozed,
      isBadstanding,
      isDissolution
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
      margin-right: 1px;
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
