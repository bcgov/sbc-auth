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
            <!-- Name Request Name(s) / Business Name -->
            <td v-if="isNameRequest(item)" class="col-wide gray-9">
              <div v-for="(name, i) in item.nameRequest.names" :key="`nrName: ${i}`" class="pb-1 names-block">
                <v-icon v-if="isRejectedName(name)" color="red" class="names-text pr-1" small>mdi-close</v-icon>
                <v-icon v-if="isApprovedName(name)" color="green" class="names-text pr-1" small>mdi-check</v-icon>
                <div class="names-text font-weight-bold">{{ name.name }}</div>
              </div>
            </td>
            <td v-else class="col-wide gray-9 font-weight-bold">{{ name(item) }}</td>

            <!-- Number -->
            <td v-if="showCol(headers[1].text)">{{ number(item) }}</td>

            <!-- Type -->
            <td v-if="showCol(headers[2].text)" class="type-column">
              <div class="gray-9 font-weight-bold">{{ type(item) }}</div>
              <div>{{ typeDescription(item) }}</div>
            </td>

            <!-- Status -->
            <td v-if="showCol(headers[3].text)" class="text-capitalize">{{ status(item) }}</td>

            <!-- Actions -->
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
  @Prop({ default: [] }) readonly selectedColumns!: Array<string>
  @Prop({ default: false }) readonly loading!: boolean

  // State/Action Properties
  private readonly businesses!: Business[]
  private readonly currentOrganization!: Organization
  private readonly createNamedBusiness!: ({ filingType, business }) => Promise<any>

  // Local Properties
  private headers: any[] = []
  private isLoading: boolean = false
  private filteredItems: Business[] = []
  private filterActive = { name: false, number: false, status: false, type: false }
  private filterParams = { name: null, number: null, status: null, type: null }

  /** V-model for dropdown menus. */
  private dropdown: Array<boolean> = []

  /** The number of affiliated entities and name requests. */
  get entityCount (): number {
    return this.businesses.length
  }

  /** The headers we want to show. */
  get getHeaders (): Array<any> {
    return this.headers?.filter(x => x.show)
  }

  /** The set height when affiliation count exceeds 5 */
  get getMaxHeight (): string {
    return this.entityCount > 5 ? '32rem' : null
  }

  get showClearFilters (): boolean {
    return Object.values(this.filterActive).includes(true)
  }

  protected clearFilters (): void {
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

  /** Returns true if the affiliation is a Name Request. */
  protected isNameRequest (business: Business): boolean {
    return (business.corpType.code === CorpTypes.NAME_REQUEST && !!business.nameRequest)
  }

  /** Returns true if the affiliation is a temporary business. */
  protected isTemporaryBusiness (business: Business): boolean {
    return (
      business.corpType.code === CorpTypes.INCORPORATION_APPLICATION ||
      business.corpType.code === CorpTypes.REGISTRATION
    )
  }

  /** Returns true if the affiliation is a numbered IA. */
  private isNumberedIncorporationApplication (item: Business): boolean {
    return (
      item.corpType.code === CorpTypes.INCORPORATION_APPLICATION &&
      item.name === item.businessIdentifier
    )
  }

  /** Returns true if the affiliation is approved to start an IA or Registration. */
  protected canUseNameRequest (business: Business): boolean {
    // Split string tokens into an array to avoid false string matching
    const supportedEntityFlags = LaunchDarklyService.getFlag(LDFlags.IaSupportedEntities)?.split(' ') || []

    return (
      this.isNameRequest(business) && // Is this a Name Request
      business.nameRequest.enableIncorporation && // Is the Nr state approved (conditionally) or registration
      supportedEntityFlags.includes(business.nameRequest.legalType) // Feature flagged Nr types
    )
  }

  /** Returns the name of the affiliation. */
  protected name (item: Business): string {
    if (this.isNumberedIncorporationApplication(item)) {
      const legalType: unknown = item.corpType.legalType
      // *** TODO: remove fallback once Auth API returns legal type (#14183)
      return GetCorpNumberedDescription(legalType as CorpTypeCd) || 'Numbered Benefit Company'
    }
    return item.name
  }

  private parseName (business: Business): string {
    if (this.isNameRequest(business)) {
      return business.nameRequest.names.map(name => name.name).join('\n')
    } else {
      return this.name(business)
    }
  }

  /** Returns true if the name is approved. */
  protected isApprovedName (name: Names): boolean {
    return (name.state === NrState.APPROVED)
  }

  /** Returns true if the name is rejected. */
  protected isRejectedName (name: Names): boolean {
    return (name.state === NrState.REJECTED)
  }

  /** Returns the identifier of the affiliation. */
  protected number (business: Business): string {
    if (this.isNumberedIncorporationApplication(business)) {
      return 'Pending'
    }
    if (this.isTemporaryBusiness(business)) {
      return business.nrNumber
    }
    if (this.isNameRequest(business)) {
      return business.nameRequest.nrNumber
    }
    return business.businessIdentifier
  }

  /** Returns the type of the affiliation. */
  protected type (business: Business): string {
    if (this.isNameRequest(business)) {
      return AffiliationTypes.NAME_REQUEST
    }
    if (this.isTemporaryBusiness(business)) {
      return this.tempDescription(business)
    }
    return GetCorpFullDescription(business.corpType.code as CorpTypeCd)
  }

  /** Returns the temp business description. */
  protected tempDescription (business: Business): string {
    switch (business.corpType.code as CorpTypes) {
      case CorpTypes.INCORPORATION_APPLICATION:
        return AffiliationTypes.INCORPORATION_APPLICATION
      case CorpTypes.REGISTRATION:
        return AffiliationTypes.REGISTRATION
      default:
        return '' // should never happen
    }
  }

  /** Returns the type description. */
  protected typeDescription (business: Business): string {
    // if this is a name request then show legal type
    if (this.isNameRequest(business)) {
      const legalType: unknown = business.nameRequest.legalType
      return GetCorpFullDescription(legalType as CorpTypeCd)
    }
    // if this is an IA or registration then show legal type
    if (this.isTemporaryBusiness(business)) {
      const legalType: unknown = business.corpType.legalType
      return GetCorpFullDescription(legalType as CorpTypeCd)
    }
    // else show nothing
    return ''
  }

  /** Returns the status of the affiliation. */
  protected status (business: Business): string {
    if (this.isNameRequest(business)) {
      // Format name request state value
      const state = NrState[business.nameRequest.state]
      if (!state) return 'Unknown'
      else return NrDisplayStates[state] || 'Unknown'
    }
    if (this.isTemporaryBusiness(business)) {
      return BusinessState.DRAFT
    }
    if (business.status) {
      return business.status.charAt(0)?.toUpperCase() + business.status?.slice(1)?.toLowerCase()
    }
    return BusinessState.ACTIVE
  }

  /** Returns the last modified date string or a default message. */
  // NOT USED AT THE MOMENT
  // protected lastModified (item: Business): string {
  //   if (item.lastModified) {
  //     return this.dateToPacificDate(new Date(item.lastModified))
  //   }
  //   if (item.modified) {
  //     return this.dateToPacificDate(new Date(item.modified))
  //   }
  //   return this.$t('notAvailable').toString()
  // }

  /** Returns the modified by value or a default message. */
  // NOT USED AT THE MOMENT
  // protected modifiedBy (item: Business): string {
  //   if (item.modifiedBy === 'None None' || !item.modifiedBy) {
  //     return this.$t('notAvailable').toString()
  //   }
  //   return item.modifiedBy || this.$t('notAvailable').toString()
  // }

  /** Handler for open action */
  protected open (item: Business): void {
    if (item.corpType.code === CorpTypes.NAME_REQUEST) {
      this.goToNameRequest(item.nameRequest)
    } else {
      this.goToDashboard(item.businessIdentifier)
    }
  }

  /** Handler for draft IA creation and navigation */
  protected async useNameRequest (item: Business) {
    switch (item.nameRequest.target) {
      case NrTargetTypes.LEAR:
        // Create new IA if the selected item is Name Request
        let businessIdentifier = item.businessIdentifier
        if (item.corpType.code === CorpTypes.NAME_REQUEST) {
          this.isLoading = true
          businessIdentifier = await this.createBusinessRecord(item)
          this.isLoading = false
        }
        this.goToDashboard(businessIdentifier)
        break
      case NrTargetTypes.ONESTOP:
        this.goToOneStop()
        break
      case NrTargetTypes.COLIN:
        this.goToCorpOnline()
        break
    }
  }

  /** Navigation handler for entities dashboard */
  private goToDashboard (businessIdentifier: string): void {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
    let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`
    window.location.href = appendAccountId(decodeURIComponent(redirectURL))
  }

  /** Navigation handler for Name Request application */
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

  /** Create a business record in LEAR. */
  private async createBusinessRecord (business: Business): Promise<string> {
    const regTypes = [CorpTypes.SOLE_PROP, CorpTypes.PARTNERSHIP]
    const iaTypes = [CorpTypes.BENEFIT_COMPANY, CorpTypes.COOP, CorpTypes.BC_CCC, CorpTypes.BC_COMPANY,
      CorpTypes.BC_ULC_COMPANY]

    let filingResponse = null

    if (regTypes.includes(business.nameRequest?.legalType as CorpTypes)) {
      filingResponse =
        await this.createNamedBusiness({ filingType: FilingTypes.REGISTRATION, business })
    } else if (iaTypes.includes(business.nameRequest?.legalType as CorpTypes)) {
      filingResponse =
        await this.createNamedBusiness({ filingType: FilingTypes.INCORPORATION_APPLICATION, business })
    }

    if (filingResponse?.errorMsg) {
      this.$emit('add-unknown-error')
      return ''
    }

    return filingResponse.data.filing.business.identifier
  }

  /** Returns true when the selected columns includes the column argument. */
  protected showCol (col): boolean {
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

  private selectFilter (itemVal: string, filterVal: string): boolean {
    return !filterVal || itemVal.toUpperCase() === filterVal.toUpperCase()
  }

  private textFilter (itemVal: string, filterVal: string): boolean {
    return !filterVal || itemVal.toUpperCase().includes(filterVal.toUpperCase())
  }

  /** Emit business/nr information to be unaffiliated. */
  @Emit()
  protected removeBusiness (business: Business): RemoveBusinessPayload {
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
  private handleFilterChange (): void {
    this.filteredItems = this.filter(this.businesses)
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
