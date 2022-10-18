<template>
  <div id="affiliated-entity-section">
    <v-card flat>
      <div class="table-header">
        <label><strong>My List </strong>({{ entityCount }})</label>
      </div>
      <v-data-table
        id="affiliated-entity-table"
        :class="{ 'header-high-layer': dropdown.includes(true) }"
        :headers="getHeaders"
        :items="businesses"
        :custom-sort="customSort"
        fixed-header
        disable-pagination
        hide-default-footer
      >
        <template v-slot:item="{ item, index }">
          <tr>
            <td
              v-if="isNameRequest(item.corpType.code) && item.nameRequest"
              class="header"
              :class="{ 'col-wide': getHeaders.length < 7 }"
            >
              <div v-for="(name, i) in item.nameRequest.names" :key="`nrName: ${i}`" class="pb-1 names-block">
                <v-icon v-if="isRejectedName(name)" color="red" class="names-text pr-1" small>mdi-close</v-icon>
                <v-icon v-if="isApprovedName(name)" color="green" class="names-text pr-1" small>mdi-check</v-icon>
                <strong class="names-text">{{ name.name }}</strong><br>
              </div>
            </td>
            <td v-else class="header" :class="{ 'col-wide': getHeaders.length < 7 }">
              <strong>{{ name(item) }}</strong>
            </td>
            <td v-if="showCol(headers[1].text)">{{ number(item) }}</td>
            <td v-if="showCol(headers[2].text)" class="type-col">
              <span class="header"><strong>{{ type(item) }}</strong></span><br>
              <span v-if="isNameRequest(item.corpType.code) && item.nameRequest">
                {{ typeDescription(item.nameRequest.legalType) }}
              </span>
            </td>
            <td v-if="showCol(headers[3].text)" class="status">{{ status(item) }}</td>
            <td v-if="showCol(headers[4].text)">{{ folio(item) }}</td>
            <td v-if="showCol(headers[5].text)">{{ lastModified(item) }}</td>
            <td v-if="showCol(headers[6].text)">{{ modifiedBy(item) }}</td>
            <td class="action-cell">
              <div class="actions" :id="`action-menu-${index}`">
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

                <!-- More Actions Menu -->
                <span class="more-actions mr-4">
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
                        <v-list-item-subtitle v-if="isTemporaryBusinessRegistration(item.corpType.code)">
                          <v-icon small>mdi-delete-forever</v-icon>
                          <span class="pl-1">Delete {{tempDescription(item.corpType.code)}}</span>
                        </v-list-item-subtitle>
                        <v-list-item-subtitle v-else>
                          <v-icon small>mdi-delete</v-icon>
                          <span class="pl-1">Remove From Table</span>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </v-menu>
                </span>
              </div>
            </td>
          </tr>
        </template>
        <template v-slot:no-data>
          <span v-if="loading">Loading...</span>
          <div v-else>
            Add an existing company, cooperative or society to manage it or
            <br>
            add a Name Request to complete your incorporation or registration.
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script lang='ts'>
import {
  AffiliationTypes,
  BusinessState,
  CorpType,
  FilingTypes,
  LDFlags,
  LegalTypes,
  NrDisplayStates,
  NrEntityType,
  NrState,
  NrTargetTypes,
  SessionStorageKeys
} from '@/util/constants'
import { Business, BusinessRequest, NameRequest, Names } from '@/models/business'
import { Component, Emit, Mixins, Prop, Watch } from 'vue-property-decorator'
import { CorpTypeCd, GetCorpFullDescription } from '@bcrs-shared-components/corp-type-module'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import DateMixin from '@/components/auth/mixins/DateMixin.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', ['currentOrganization'])
  },
  methods: {
    ...mapActions('business', ['createNamedBusiness'])
  }
})
export default class AffiliatedEntityTable extends Mixins(DateMixin) {
  @Prop({ default: [] }) readonly selectedColumns: Array<string>
  @Prop({ default: false }) readonly loading: boolean

  // Local Properties
  private readonly businesses!: Business[]
  private readonly currentOrganization!: Organization
  private readonly createNamedBusiness!: (filingBody: BusinessRequest, nrNumber: string) => Promise<any>
  private headers: Array<any> = []
  private isLoading: boolean = false

  /** V-model for dropdown menus. */
  private dropdown: Array<boolean> = []

  /** The number of affiliated entities or name requests. */
  private get entityCount (): number {
    return this.businesses.length
  }

  /** The headers we want to show. */
  private get getHeaders (): Array<any> {
    return this.headers?.filter(x => x.show)
  }

  /** Returns true if the affiliation is a Name Request */
  private isNameRequest (corpType: string): boolean {
    return corpType === CorpType.NAME_REQUEST
  }

  /** Returns true if the affiliation is a Temp Registration */
  private isTemporaryBusinessRegistration (corpType: string): boolean {
    return corpType === CorpType.NEW_BUSINESS || corpType === CorpType.NEW_REGISTRATION
  }

  /** Returns true if the affiliation is a Numbered Company */
  private isNumberedIncorporationApplication (item: Business): boolean {
    return item.corpType.code === CorpType.NEW_BUSINESS && item.name === item.businessIdentifier
  }

  /** Returns true if the affiliation is approved to start an IA or Registration */
  private canUseNameRequest (business: Business): boolean {
    // Split string tokens into an array to avoid false string matching
    const supportedEntityFlags = LaunchDarklyService.getFlag(LDFlags.IaSupportedEntities)?.split(' ') || []

    return this.isNameRequest(business.corpType.code) && // Is this a Name Request
      business.nameRequest?.enableIncorporation && // Is the Nr state approved (conditionally) or registration
      supportedEntityFlags.includes(business.nameRequest?.legalType) // Feature flagged Nr types
  }

  /** Returns the Name value for the affiliation */
  private name (item: Business): string {
    return this.isNumberedIncorporationApplication(item) ? 'Numbered Benefit Company' : item.name
  }

  /** Returns true if the Name Request is approved */
  private isApprovedName (name: Names): boolean {
    return name.state === NrState.APPROVED
  }

  /** Returns true if the Name Request is rejected */
  private isRejectedName (name: Names): boolean {
    return name.state === NrState.REJECTED
  }

  /** Returns the identifier for the affiliation */
  private number (item: Business): string {
    switch (true) {
      case (this.isNumberedIncorporationApplication(item)):
        return 'Pending'
      case (this.isTemporaryBusinessRegistration(item.corpType.code)):
        return item.nrNumber
      case this.isNameRequest(item.corpType.code):
        return item.nameRequest?.nrNumber
      default:
        return item.businessIdentifier
    }
  }

  /** Returns the type of the affiliation */
  private type (item: Business): string {
    switch (true) {
      case (this.isNameRequest(item.corpType.code)):
        return AffiliationTypes.NAME_REQUEST
      case this.isTemporaryBusinessRegistration(item.corpType.code):
        return this.tempDescription(item.corpType.code as CorpType)
      default:
        return this.typeDescription(item.corpType.code as CorpTypeCd)
    }
  }

  /** Returns the temp corp description for display */
  private tempDescription (corpType: CorpType): string {
    switch (corpType) {
      case CorpType.NEW_BUSINESS:
        return AffiliationTypes.INCORPORATION_APPLICATION
      case CorpType.NEW_REGISTRATION:
        return AffiliationTypes.REGISTRATION
    }
  }

  /** Returns the corp full description for display */
  private typeDescription (corpType: CorpTypeCd): string {
    return GetCorpFullDescription(corpType)
  }

  /** Returns the status for the affiliation */
  private status (item: Business): string {
    switch (true) {
      case (this.isNameRequest(item.corpType.code) && !!item.nameRequest):
        // Format name request state value for Display
        return NrDisplayStates[NrState[item.nameRequest.state]]
      case this.isTemporaryBusinessRegistration(item.corpType.code):
        return BusinessState.DRAFT
      case !!item.status:
        return item.status.toLowerCase()
      default:
        return BusinessState.ACTIVE
    }
  }

  /** Returns the folio number or a default message */
  private folio (item: Business): string {
    return item.nameRequest && (item.nameRequest.folioNumber || '')
  }

  /** Returns the last modified date string or a default message */
  private lastModified (item: Business): string {
    switch (true) {
      case (!!item.lastModified):
        return this.dateToPacificDate(new Date(item.lastModified))
      case (!!item.modified):
        return this.dateToPacificDate(new Date(item.modified))
      default: return this.$t('notAvailable').toString()
    }
  }

  /** Returns the modified by value or a default message */
  private modifiedBy (item: Business): string {
    if (item.modifiedBy === 'None None' || !item.modifiedBy) {
      return this.$t('notAvailable').toString()
    } else { return item.modifiedBy || this.$t('notAvailable').toString() }
  }

  /** Redirect handler for Dashboard OPEN action */
  private open (item: Business): void {
    if (item.corpType.code === CorpType.NAME_REQUEST) {
      this.goToNameRequest(item.nameRequest)
    } else {
      this.goToDashboard(item.businessIdentifier)
    }
  }

  /** Handler method for draft IA creation and navigation */
  async useNameRequest (item: Business) {
    switch (item.nameRequest.target) {
      case NrTargetTypes.LEAR:
        // Create new IA if the selected item is Name Request
        let businessIdentifier = item.businessIdentifier
        if (item.corpType.code === CorpType.NAME_REQUEST) {
          this.isLoading = true
          businessIdentifier = await this.createBusinessRecord(item)
          this.isLoading = false
        }
        this.goToDashboard(businessIdentifier)
        break
      case NrTargetTypes.ONESTOP:
        this.goToOneStop() // Navigate to onestop for firms
        break
      case NrTargetTypes.COLIN:
        this.goToCorpOnline() // Navigate to Corporate Online for Corps
        break
    }
  }

  /** Navigation handler for entities dashboard */
  private goToDashboard (businessIdentifier: string): void {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
    let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`

    window.location.href = appendAccountId(decodeURIComponent(redirectURL))
  }

  /** Navigation handler for name request application */
  private goToNameRequest (nameRequest: NameRequest): void {
    ConfigHelper.setNrCredentials(nameRequest)
    window.location.href = appendAccountId(`${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`)
  }

  /** Navigation handler for OneStop application */
  private goToOneStop (): void {
    window.location.href = appendAccountId(ConfigHelper.getOneStopUrl())
  }

  /** Navigation handler for Corporate Online application */
  private goToCorpOnline (): void {
    window.location.href = appendAccountId(ConfigHelper.getCorporateOnlineUrl())
  }

  /** Create a business record in Lear */
  private async createBusinessRecord (business: Business): Promise<string> {
    let filingResponse = null
    if ([LegalTypes.SP, LegalTypes.GP].includes(business.nameRequest?.legalType as LegalTypes)) {
      filingResponse = await this.createBusinessRegistration(business)
    } else {
      filingResponse = await this.createBusinessIA(business)
    }

    if (filingResponse?.errorMsg) {
      this.$emit('add-unknown-error')
      return ''
    } else {
      return filingResponse.data.filing.business.identifier
    }
  }

  private async createBusinessIA (business: Business): Promise<any> {
    const filingBody: BusinessRequest = {
      filing: {
        header: {
          name: FilingTypes.INCORPORATION_APPLICATION,
          accountId: this.currentOrganization.id
        },
        business: {
          legalType: business.nameRequest.legalType
        },
        incorporationApplication: {
          nameRequest: {
            legalType: business.nameRequest.legalType,
            nrNumber: business.businessIdentifier
          }
        }
      }
    }
    return this.createNamedBusiness(filingBody, business.businessIdentifier)
  }

  private async createBusinessRegistration (business: Business): Promise<any> {
    const filingBody: BusinessRequest = {
      filing: {
        header: {
          name: FilingTypes.REGISTRATION,
          accountId: this.currentOrganization.id
        },
        registration: {
          nameRequest: {
            legalType: business.nameRequest.legalType,
            nrNumber: business.businessIdentifier
          },
          business: {
            natureOfBusiness: business.nameRequest.natureOfBusiness
          }
        }
      }
    }
    // businessType is only required for legalType SP to differentiate Sole Proprietor / Sole Proprietor (DBA)
    if (business.nameRequest.legalType === LegalTypes.SP) {
      if (business.nameRequest.entityTypeCd === NrEntityType.FR) {
        filingBody.filing.registration.businessType = 'SP'
      } else if (business.nameRequest.entityTypeCd === NrEntityType.DBA) {
        filingBody.filing.registration.businessType = 'DBA'
      }
    }
    return this.createNamedBusiness(filingBody, business.businessIdentifier)
  }

  /** Is true when the selected columns includes the column argument. */
  private showCol = (col): boolean => {
    return this.selectedColumns.includes(col)
  }

  /** Custom sorting method to handle consolidated Nr and Affiliations data. */
  private customSort (items, index, isDesc): any {
    items.sort((a, b) => {
      switch (index[0]) {
        case 'lastModified':
          let dateA, dateB
          if (a.lastModified) {
            dateA = a.lastModified
          } else {
            dateA = a.modified
          }
          if (b.lastModified) {
            dateB = b.lastModified
          } else {
            dateB = b.modified
          }

          if (!isDesc[0]) {
            return +new Date(dateB) - +new Date(dateA)
          } else {
            return +new Date(dateA) - +new Date(dateB)
          }
        case 'name':
          let nameA, nameB
          if (a.nameRequest) {
            nameA = a.nameRequest?.names[0].name
          } else {
            nameA = this.isNumberedIncorporationApplication(a) ? 'Numbered Benefit Company' : a.name
          }
          if (b.nameRequest) {
            nameB = b.nameRequest?.names[0].name
          } else {
            nameB = this.isNumberedIncorporationApplication(b) ? 'Numbered Benefit Company' : b.name
          }

          if (!isDesc[0]) {
            return nameA.toLowerCase().localeCompare(nameB.toLowerCase())
          } else {
            return nameB.toLowerCase().localeCompare(nameA.toLowerCase())
          }
        case 'number':
          if (!isDesc[0]) {
            return this.number(a).toLowerCase().localeCompare(this.number(b).toLowerCase())
          } else {
            return this.number(b).toLowerCase().localeCompare(this.number(a).toLowerCase())
          }
        case 'type':
          if (!isDesc[0]) {
            return this.type(a).toLowerCase().localeCompare(this.type(b).toLowerCase())
          } else {
            return this.type(b).toLowerCase().localeCompare(this.type(a).toLowerCase())
          }
        case 'status':
          if (!isDesc[0]) {
            return this.status(a).toLowerCase().localeCompare(this.status(b).toLowerCase())
          } else {
            return this.status(b).toLowerCase().localeCompare(this.status(a).toLowerCase())
          }
        case 'modifiedBy':
          if (!isDesc[0]) {
            return this.modifiedBy(a).toLowerCase().localeCompare(this.modifiedBy(b).toLowerCase())
          } else {
            return this.modifiedBy(b).toLowerCase().localeCompare(this.modifiedBy(a).toLowerCase())
          }
      }
    })
    return items
  }

  /** Emit business/nr information to be unaffiliated. */
  @Emit()
  removeBusiness (business: Business): RemoveBusinessPayload {
    return {
      orgIdentifier: this.currentOrganization.id,
      business
    }
  }

  /** Apply data table headers dynamically to account for computed properties. */
  @Watch('selectedColumns', { immediate: true })
  private applyHeaders (): void {
    this.headers = [
      { text: 'Business Name', align: 'start', value: 'name', sortable: true, show: true },
      { text: 'Number', value: 'number', sortable: true, show: this.showCol('Number') },
      { text: 'Type', value: 'type', sortable: true, show: this.showCol('Type') },
      { text: 'Status', value: 'status', sortable: true, show: this.showCol('Status') },
      { text: 'Folio', value: 'folio', sortable: false, show: this.showCol('Folio') },
      { text: 'Last Modified', value: 'lastModified', sortable: true, show: this.showCol('Last Modified') },
      { text: 'Modified By', value: 'modifiedBy', sortable: true, show: this.showCol('Modified By') },
      { text: 'Actions', align: 'end', value: 'action', sortable: false, show: true }
    ]
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

#affiliated-entity-section {
  .table-header {
    display: flex;
    background-color: $app-lt-blue;
    padding: .875rem;
  }

  // size the table according to window height
  ::v-deep .v-data-table__wrapper {
    min-height: 9rem; // height of no-data div
    height: calc(100vh - 31rem); // full height minus footer
    background-color: $gray1; // hide unused space below table

    table {
      background-color: white;
    }
  }

  .names-block {
    display: table;
  }

  .names-text {
    display: table-cell;
    vertical-align: top;
  }

  .v-btn {
    background-color: $app-blue !important;
  }

  tbody {
    tr {
      vertical-align: top;

      &:hover {
        background-color: transparent !important;
      }

      .header {
        color: $gray9;
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

      .type-col {
        min-width: 12rem;
      }

      td:last-child {
        padding-right: 5px;
      }
    }
  }

  .action-cell {
    max-width: 0;
    max-height: 30px !important;
    text-align: end !important;
    padding-right: 0;
  }

  .actions {
    height:30px;

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

::v-deep .theme--light.v-data-table thead tr:last-child th:last-child span {
  padding-right: 85px;
}

::v-deep .theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: $app-blue;
  .v-icon.v-icon {
    color: $app-blue;
  }
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

  .status {
    text-transform: capitalize;
  }
}
</style>
