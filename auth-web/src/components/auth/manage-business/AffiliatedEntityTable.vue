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
        :items="filteredItems"
        :height="getMaxHeight"
        fixed-header
        disable-pagination
        hide-default-footer
        hide-default-header
      >
        <template v-slot:header="{ props }">
          <thead>
            <tr>
              <th v-for="(header, index) in props.headers" :key="header.value + index">
                <div :style="header.value === 'action' ? {'min-width': '140px', 'text-align': 'center'} : ''">
                  <span v-html="header.text" />
                </div>
              </th>
            </tr>
            <tr>
              <th
                v-for="header, i in props.headers"
                :key="header.value + 'filter' + i"
                :style="{'width': header.width}"
              >
                <v-select
                  v-if="header.filterType === 'select'"
                  class="table-filter"
                  clearable
                  dense
                  filled
                  hide-details
                  :items="header.filterSelections"
                  :label="header.filterLabel || ''"
                  :menu-props="{ bottom: true, offsetY: true }"
                  single-line
                  v-model="filterParams[header.value]"
                />
                <v-text-field
                  v-else-if="header.filterType === 'text'"
                  class="table-filter"
                  clearable
                  dense
                  filled
                  hide-details
                  :label="header.filterLabel || ''"
                  single-line
                  type="text"
                  v-model="filterParams[header.value]"
                />
                <v-btn
                  v-else-if="showClearFilters"
                  class="clear-btn mx-auto"
                  color="primary"
                  outlined
                  @click="clearFilters()"
                >
                  Clear Filters
                  <v-icon class="ml-1 mt-1">mdi-close</v-icon>
                </v-btn>
              </th>
            </tr>
          </thead>
        </template>
        <template v-slot:item="{ item, index }">
          <tr>
            <td v-if="isNameRequest(item.corpType.code) && item.nameRequest" class="header col-wide">
              <div v-for="(name, i) in item.nameRequest.names" :key="`nrName: ${i}`" class="pb-1 names-block">
                <v-icon v-if="isRejectedName(name)" color="red" class="names-text pr-1" small>mdi-close</v-icon>
                <v-icon v-if="isApprovedName(name)" color="green" class="names-text pr-1" small>mdi-check</v-icon>
                <strong class="names-text">{{ name.name }}</strong><br>
              </div>
            </td>
            <td v-else class="header col-wide"><strong>{{ name(item) }}</strong></td>
            <td v-if="showCol(headers[1].text)">{{ number(item) }}</td>
            <td v-if="showCol(headers[2].text)" class="type-col">
              <span class="header"><strong>{{ type(item) }}</strong></span><br>
              <span v-if="isNameRequest(item.corpType.code) && item.nameRequest">
                {{ typeDescription(item.nameRequest.legalType) }}
              </span>
            </td>
            <td v-if="showCol(headers[3].text)" class="status">{{ status(item) }}</td>
            <td class="action-cell">
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
                </span>

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
          <span v-else>Add an existing company, cooperative or society to manage it or<br> add a Name Request to
            complete your incorporation or registration.</span>
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
  private headers: any[] = []
  private isLoading: boolean = false

  private filteredItems: Business[] = []
  private filterActive = { name: false, number: false, status: false, type: false }
  private filterParams = { name: null, number: null, status: null, type: null }

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

  /** The set height when affiliation count exceeds 5 */
  private get getMaxHeight (): string {
    return this.entityCount > 5 ? '32rem' : null
  }

  private get showClearFilters (): boolean {
    return Object.values(this.filterActive).includes(true)
  }

  private clearFilters (): void {
    for (const key in this.filterActive) this.filterActive[key] = false
    for (const key in this.filterParams) this.filterParams[key] = null
  }

  private getSelections (selectFn: (item: Business) => string): string[] {
    const items = []
    for (const i in this.businesses) {
      if (!items.includes(selectFn(this.businesses[i]))) {
        items.push(selectFn(this.businesses[i]))
      }
    }
    return items
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

  private parseName (item: Business): string {
    if (this.isNameRequest(item.corpType.code)) {
      return item.nameRequest.names.map(name => name.name).join('\n')
    } else return this.name(item)
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
        if (!NrState[item.nameRequest?.state]) return 'Unknown'
        return NrDisplayStates[NrState[item.nameRequest.state]] || 'Unknown'
      case this.isTemporaryBusinessRegistration(item.corpType.code):
        return BusinessState.DRAFT
      case !!item.status:
        return item.status.charAt(0)?.toUpperCase() + item.status?.slice(1)?.toLowerCase()
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

  private filter (items: Business[]): Business[] {
    let newItems = [...items]
    for (const i in this.getHeaders) {
      const header = this.getHeaders[i]
      if (this.filterParams[header.value]) this.filterActive[header.value] = true
      if (header.filterFn && this.filterActive[header.value]) {
        newItems = newItems.filter((item) => {
          if (header.filterType === 'select') return this.selectFilter(header.filterFn(item), this.filterParams[header.value])
          else return this.textFilter(header.filterFn(item), this.filterParams[header.value])
        })
      }
      if (!this.filterParams[header.value]) this.filterActive[header.value] = false
    }
    return newItems
  }

  private selectFilter = (itemVal: string, filterVal: string) => {
    return !filterVal || itemVal.toUpperCase() === filterVal.toUpperCase()
  }

  private textFilter = (itemVal: string, filterVal: string) => {
    return !filterVal || itemVal.toUpperCase().includes(filterVal.toUpperCase())
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
      { text: 'Business Name', value: 'name', show: true, filterType: 'text', filterFn: this.parseName, filterLabel: 'Name', width: '30%' },
      { text: 'Number', value: 'number', show: this.showCol('Number'), filterType: 'text', filterFn: this.number, filterLabel: 'Number', width: '17%' },
      { text: 'Type', value: 'type', show: this.showCol('Type'), filterType: 'select', filterSelections: this.getSelections(this.type), filterFn: this.type, filterLabel: 'Type', width: '25%' },
      { text: 'Status', value: 'status', show: this.showCol('Status'), filterType: 'select', filterSelections: this.getSelections(this.status), filterFn: this.status, filterLabel: 'Status', width: '25%' },
      { text: 'Actions', value: 'action', show: true, width: '3%' }
    ]
  }

  @Watch('businesses', { immediate: true, deep: true })
  private updateSortedItems (val): void {
    if (val) this.filteredItems = [...val]
    else this.filteredItems = []
    this.clearFilters()
    this.applyHeaders()
  }

  @Watch('filterParams', { deep: true })
  private handleFilterChange () { this.filteredItems = this.filter(this.businesses) }
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

  .status {
    text-transform: capitalize;
  }
}
</style>
