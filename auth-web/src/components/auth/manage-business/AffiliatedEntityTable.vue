<!-- eslint-disable vue/no-template-shadow -->
<template>
  <div id="affiliated-entity-section">
    <v-card flat>
      <div class="table-header">
        <v-row
          no-gutters
          class="mb-n8"
        >
          <v-col class="pt-3 pl-1">
            <label><strong>My List </strong>({{ entityCount }})</label>
          </v-col>
          <v-col class="column-actions">
            <v-select
              v-model="selectedColumns"
              dense
              multiple
              class="column-selector pb-2 pr-2"
              background-color="white"
              label="Columns to Show"
              :items="columns"
              :menu-props="{ bottom: true, offsetY: true }"
              @change="getHeaders($event)"
            >
              <template #selection />
            </v-select>
          </v-col>
        </v-row>
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
        highlight-class="base-table__item-row-green"
      >
        <template #header-filter-slot-Actions>
          <v-btn
            v-if="affiliations.filters.isActive"
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
        <!-- Name Request Name(s) / Business Name -->
        <template #item-slot-Name="{ item }">
          <span class="d-block">
            <b
              v-if="isNameRequest(item)"
              class="col-wide gray-9"
            >
              <b
                v-for="(name, i) in item.nameRequest.names"
                :key="`nrName: ${i}`"
                class="pb-1 names-block"
              >
                <v-icon
                  v-if="isRejectedName(name)"
                  color="red"
                  class="names-text pr-1"
                  small
                >mdi-close</v-icon>
                <v-icon
                  v-if="isApprovedName(name)"
                  color="green"
                  class="names-text pr-1"
                  small
                >mdi-check</v-icon>
                <div class="names-text font-weight-bold">{{ name.name }}</div>
              </b>
            </b>
            <b
              v-else
              class="col-wide gray-9 font-weight-bold"
            >{{ name(item) }}</b>
          </span>

          <span
            v-if="!!item.affiliationInvites"
            id="affiliationInvitesStatus"
            class="d-flex align-start"
          >
            <v-icon
              class="pr-1 status-icon"
              style="margin-top: 2px;"
              small
              :color="getAffiliationInvitationStatus(item.affiliationInvites) === AffiliationInvitationStatus.Expired
                ? 'red' : 'primary'"
            >
              {{ getAffiliationInvitationStatus(item.affiliationInvites) === AffiliationInvitationStatus.Expired
                ? 'mdi-alert' : 'mdi-account-cog' }}
            </v-icon>
            <p style="font-size: 12px">
              <span v-sanitize="getRequestForAuthorizationStatusText(item.affiliationInvites)" />
            </p>
          </span>
        </template>

        <!-- Number -->
        <template #item-slot-Number="{ item }">
          <span>{{ number(item) }}</span>
        </template>

        <!-- Type -->
        <template #item-slot-Type="{ item }">
          <div class="gray-9 font-weight-bold d-inline-block">
            {{ type(item) }}
          </div>
          <!-- Need to keep the NR type separate or else the table filter treats each distinctly. See PR 2389 -->
          <div
            v-if="enableNameRequestType && isNameRequest(item)"
            class="gray-9 font-weight-bold d-inline-block ml-1"
          >
            {{ nameRequestType(item) }}
          </div>
          <div>{{ typeDescription(item) }}</div>
        </template>

        <!-- Status -->
        <template #item-slot-Status="{ item }">
          <span>{{ status(item) }}</span>
          <EntityDetails
            v-if="isExpired(item) ||
              isFrozed(item) ||
              isBadstanding(item) ||
              isDissolution(item) "
            icon="mdi-alert"
            :showAlertHeader="true"
            :details="getDetails(item)"
          />
          <EntityDetails
            v-if="isProcessing(status(item))"
            icon="mdi-information-outline"
            :details="[EntityAlertTypes.PROCESSING]"
          />
        </template>
        <!-- Actions -->
        <template #item-slot-Actions="{ item, index }">
          <AffiliationAction
            :item="item"
            :index="index"
            @unknown-error="$emit('unknown-error', $event)"
            @remove-affiliation-invitation="$emit('remove-affiliation-invitation', $event)"
            @remove-business="$emit('remove-business', $event)"
            @business-unavailable-error="$emit('business-unavailable-error', $event)"
            @resend-affiliation-invitation="$emit('resend-affiliation-invitation', $event)"
            @popup-manage-business-dialog="$emit('popup-manage-business-dialog', $event)"
          />
        </template>
      </base-v-data-table>
    </v-card>
  </div>
</template>

<script lang='ts'>
import {
  AffiliationInvitationStatus,
  AffiliationTypes,
  EntityAlertTypes,
  LDFlags,
  NrDisplayStates,
  NrState
} from '@/util/constants'
import { Business, Names } from '@/models/business'
import { defineComponent, ref } from '@vue/composition-api'
import AffiliationAction from '@/components/auth/manage-business/AffiliationAction.vue'
import { AffiliationInviteInfo } from '@/models/affiliation'
import { BaseVDataTable } from '@/components'
import CommonUtils from '@/util/common-util'
import EntityDetails from './EntityDetails.vue'

import launchdarklyServices from 'sbc-common-components/src/services/launchdarkly.services'
import { useAffiliations } from '@/composables'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AffiliatedEntityTable',
  components: { AffiliationAction, EntityDetails, BaseVDataTable },
  props: {
    loading: { default: false },
    highlightIndex: { default: -1 }
  },
  emits: ['unknown-error', 'remove-affiliation-invitation', 'remove-business',
    'business-unavailable-error', 'resend-affiliation-invitation', 'popup-manage-business-dialog'],
  setup () {
    const isloading = false
    const { loadAffiliations, affiliations, entityCount, clearAllFilters,
      getHeaders, headers, type, status, updateFilter, typeDescription,
      isNameRequest, nameRequestType, number, name, canUseNameRequest,
      isTemporaryBusiness } = useAffiliations()

    const orgStore = useOrgStore()

    const selectedColumns = ['Number', 'Type', 'Status']
    const columns = ['Number', 'Type', 'Status']

    const isRejectedName = (name: Names): boolean => {
      return (name.state === NrState.REJECTED)
    }

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
      // Currently affiliation invitations don't return good standing etc.
      return item?.goodStanding === false
    }

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

    const clearFiltersTrigger = ref(0)
    const clearFilters = () => {
      clearFiltersTrigger.value++
      // clear affiliation state filters and trigger search
      clearAllFilters()
    }

    const isCurrentOrganization = (orgId: number) => {
      return orgId === orgStore.currentOrganization.id
    }

    const getRequestForAuthorizationStatusText = (affiliationInviteInfos: AffiliationInviteInfo[]) => {
      const affiliationWithSmallestId = CommonUtils.getElementWithSmallestId<AffiliationInviteInfo>(affiliationInviteInfos)
      if (isCurrentOrganization(affiliationWithSmallestId.toOrg?.id)) {
        // incoming request for access
        const andOtherAccounts = affiliationInviteInfos.length > 1 ? ` and ${affiliationInviteInfos.length - 1} other account(s)` : ''
        return `Request for Authorization to manage from: ${affiliationWithSmallestId.fromOrg.name}${andOtherAccounts}`
      } else {
        let statusText = ''
        // outgoing request for access
        switch (affiliationWithSmallestId.status) {
          case AffiliationInvitationStatus.Pending:
            statusText = 'Confirmation email sent, pending authorization.'
            break
          case AffiliationInvitationStatus.Accepted:
            statusText = '<strong>Authorized</strong> - you can now manage this business.'
            break
          case AffiliationInvitationStatus.Failed:
            statusText = '<strong>Not Authorized</strong>. Your request to manage this business has been declined.'
            break
          case AffiliationInvitationStatus.Expired:
            statusText = 'Not authorized. The <strong>confirmation email has expired.</strong>'
            break
          default:
            break
        }
        return `Authorization to manage: ${statusText}`
      }
    }

    const enableNameRequestType = (): boolean => {
      return launchdarklyServices.getFlag(LDFlags.EnableNameRequestType) || false
    }

    const getAffiliationInvitationStatus = (affiliationInviteInfos: AffiliationInviteInfo[]): string => {
      return affiliationInviteInfos.length > 0 && affiliationInviteInfos[0].status
    }

    return {
      selectedColumns,
      columns,
      isCurrentOrganization,
      getRequestForAuthorizationStatusText,
      clearFiltersTrigger,
      clearFilters,
      isloading,
      headers,
      affiliations,
      entityCount,
      enableNameRequestType,
      getHeaders,
      isNameRequest,
      isRejectedName,
      isApprovedName,
      nameRequestType,
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
      canUseNameRequest,
      isTemporaryBusiness,
      EntityAlertTypes,
      isExpired,
      getDetails,
      isFrozed,
      isBadstanding,
      isDissolution,
      getAffiliationInvitationStatus,
      AffiliationInvitationStatus
    }
  }
})

</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

#affiliated-entity-section {
  .column-selector {
    float: right;
    width: 200px;
    border-radius: 4px;
  }
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
}

.status-icon {
  margin-top: 2px;
}

.text-input-style-above {
  label {
    font-size: 0.875rem !important;
    color: $gray7 !important;
    padding-left: 6px;
  }
  span {
    padding-left: 6px;
    font-size: 14px;
    color: $gray7;
  }
}

#table-title {
  font-size: 1rem;
}

.column-selector {
  width: 200px;
  height: 10% !important;
  z-index: 1;
}

// Vuetify Overrides
::v-deep {
  .column-actions {
    .v-input__slot {
      height: 42px !important;
      min-height: 42px !important;
    }
    .v-input .v-label {
      transform: translateX(10px) translateY(-25px) scale(1);
      top: 30px;
      color: $gray7;
      font-size: .875rem;
    }
  }
}
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
