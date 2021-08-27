<template>
  <div id="affiliated-entity-section">
    <v-card flat>
      <div class="table-header">
        <label><strong>My List ({{ entityCount }})</strong></label>
      </div>
      <v-data-table
        id="affiliated-entity-table"
        :headers="getHeaders"
        :items="businesses"
        :items-per-page="1000"
        :height="getMaxHeight"
        fixed-header
        hide-default-footer
      >
        <template v-slot:item="{ item, index }">
          <tr>
            <td class="header" v-if="isNameRequest(item.corpType.code)">
              <div v-for="(name, i) in item.nameRequest.names" :key="`nrName: ${i}`" class="pb-1 names-block">
                <v-icon v-if="isRejectedName(name)" color="red" class="names-text pr-1">mdi-close</v-icon>
                <v-icon v-if="isApprovedName(name)" color="green" class="names-text pr-1">mdi-check</v-icon>
                <strong class="names-text">{{ name.name }}</strong><br>
              </div>
            </td>
            <td class="header" v-else>
              <strong>{{ name(item) }}</strong>
            </td>
            <td v-if="showCol(headers[1].text)">{{ number(item) }}</td>
            <td v-if="showCol(headers[2].text)" class="type-col">
              <span class="header"><strong>{{ type(item) }}</strong></span><br>
              <span v-if="isNameRequest(item.corpType.code)">{{ typeDescription(item.nameRequest.legalType) }}</span>
            </td>
            <td v-if="showCol(headers[3].text)">{{ status(item) }}</td>
            <td v-if="showCol(headers[4].text) && isPremiumAccount">{{ folio(item) }}</td>
            <td v-if="showCol(headers[5].text)">{{ lastModified(item) }}</td>
            <td v-if="showCol(headers[6].text)">{{ modifiedBy(item) }}</td>
            <td class="action-cell">
              <div class="actions">
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
                    offset-y left nudge-bottom="4"
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
                        v-if="isApprovedForIA(item)"
                        class="actions-dropdown_item"
                        data-test="use-name-request-button"
                        @click="createDraft(item)"
                      >
                        <v-list-item-subtitle>
                          <v-icon>mdi-file-certificate-outline</v-icon>
                          <span class="pl-1">Use this Name Request</span>
                        </v-list-item-subtitle>
                      </v-list-item>
                      <v-list-item
                        class="actions-dropdown_item"
                        data-test="remove-button"
                        v-can:REMOVE_BUSINESS.disable
                        @click="removeBusiness(item)"
                      >
                        <v-list-item-subtitle>
                          <v-icon>mdi-delete</v-icon>
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
        <span>Add an existing company, cooperative or society to manage it or<br> add a Name Request to complete your
          incorporation or registration.</span>
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
  NrState,
  SessionStorageKeys
} from '@/util/constants'
import { Business, BusinessRequest, NameRequest, Names } from '@/models/business'
import { Component, Emit, Prop, Watch } from 'vue-property-decorator'
import { CorpTypeCd, GetCorpFullDescription } from '@bcrs-shared-components/corp-type-module'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import Vue from 'vue'

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', ['currentOrganization']),
    ...mapGetters('org', ['isPremiumAccount'])
  },
  methods: {
    ...mapMutations('business', ['setCurrentBusiness']),
    ...mapActions('business', ['createNamedBusiness'])
  }
})
export default class AffiliatedEntityTable extends Vue {
  @Prop({ default: [] })
  readonly selectedColumns: Array<string>

  // Local Properties
  private readonly businesses!: Business[]
  private readonly currentOrganization!: Organization
  private readonly createNamedBusiness!: (filingBody: BusinessRequest) => any
  private readonly isPremiumAccount!: boolean
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

  /** The set height when affiliation count exceeds 5 */
  private get getMaxHeight (): string {
    return this.entityCount > 5 ? '30rem' : null
  }

  /** Returns true if the affiliation is a Name Request */
  private isNameRequest (corpType: string): boolean {
    return corpType === CorpType.NAME_REQUEST
  }

  /** Returns true if the affiliation is a Temp Registration */
  private isTemporaryBusinessRegistration (corpType: string): boolean {
    return corpType === CorpType.NEW_BUSINESS
  }

  /** Returns true if the affiliation is a Numbered Company */
  private isNumberedIncorporationApplication (item: Business): boolean {
    return item.corpType.code === CorpType.NEW_BUSINESS && item.name === item.businessIdentifier
  }

  /** Returns true if the affiliation is approved to start an IA */
  private isApprovedForIA (business: Business): boolean {
    // Split string tokens into an array to avoid false string matching
    const supportedEntityFlags = LaunchDarklyService.getFlag(LDFlags.IaSupportedEntities)?.split(' ') || []

    return this.isNameRequest(business.corpType.code) &&
      business.nameRequest?.enableIncorporation &&
      supportedEntityFlags.includes(business.nameRequest?.legalType)
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
      // This case is subject to change once the NR Number is available in the Affiliation Response ALWAYS
      case (this.isNumberedIncorporationApplication(item)):
        return 'Pending'
      case (this.isTemporaryBusinessRegistration(item.corpType.code)):
        return 'Pending'
      case this.isNameRequest(item.corpType.code):
        return item.nameRequest.nrNumber
      default:
        return item.businessIdentifier
    }
  }

  /** Returns the type of the affiliation */
  private type (item: Business): AffiliationTypes {
    switch (true) {
      case (this.isNameRequest(item.corpType.code)):
        return AffiliationTypes.NAME_REQUEST
      case this.isTemporaryBusinessRegistration(item.corpType.code):
        return AffiliationTypes.INCORPORATION_APPLICATION
      default:
        return AffiliationTypes.CORPORATION
    }
  }

  /** Returns the corp full description for display */
  private typeDescription (corpType: CorpTypeCd): string {
    return GetCorpFullDescription(corpType)
  }

  /** Returns the status for the affiliation */
  private status (item: Business): string {
    switch (true) {
      case (this.isNameRequest(item.corpType.code)):
        // Format name request state value for Display
        return item.nameRequest.state.charAt(0).toUpperCase() + item.nameRequest.state.slice(1).toLowerCase()
      case this.isTemporaryBusinessRegistration(item.corpType.code):
        return BusinessState.DRAFT
      default:
        return BusinessState.ACTIVE
    }
  }

  /** Returns the folio number or a default message */
  private folio (item: Business): string {
    return item.folioNumber || this.$t('notAvailable').toString()
  }

  /** Returns the last modified date string or a default message */
  private lastModified (item: Business): string {
    return item.lastModified
      ? new Date(item.lastModified).toLocaleDateString('en-CA', {
        timeZone: 'America/Vancouver'
      })
      : this.$t('notAvailable').toString()
  }

  /** Returns the modified by value or a default message */
  private modifiedBy (item: Business): string {
    switch (true) {
      case (item.modifiedBy === 'None None'):
        return this.$t('notAvailable').toString()
      case (!item.modifiedBy):
        return this.$t('notAvailable').toString()
      default:
        return item.modifiedBy
    }
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
  async createDraft (item: Business) {
    let businessIdentifier = item.businessIdentifier
    // 3806 : Create new IA if the selected item is Name Request
    // If the business is NR, indicates there is no temporary business. Create a new IA for this NR and navigate.
    if (item.corpType.code === CorpType.NAME_REQUEST && item.nameRequest.state === NrState.APPROVED) {
      this.isLoading = true
      // Find business with name as the NR number and use it for redirection
      businessIdentifier = await this.createBusinessRecord(item)
      this.isLoading = false
    }
    this.goToDashboard(businessIdentifier)
  }

  /** Navigation handler for entities dashboard */
  private goToDashboard (businessIdentifier: string): void {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
    let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`

    window.location.href = decodeURIComponent(redirectURL)
  }

  /** Navigation handler for name request application */
  private goToNameRequest (nameRequest: NameRequest): void {
    ConfigHelper.setNrCredentials(nameRequest)
    window.location.href = `${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`
  }

  /** Create a business record in Lear */
  private async createBusinessRecord (business: Business): Promise<string> {
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
    const filingResponse = await this.createNamedBusiness(filingBody)

    if (filingResponse?.errorMsg) {
      this.$emit('add-unknown-error')
      return ''
    } else {
      return filingResponse.data.filing.business.identifier
    }
  }

  /** Is true when the selected columns includes the column argument. */
  private showCol = (col): boolean => {
    return this.selectedColumns.includes(col)
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
      { text: 'Business Name', align: 'start', value: 'name', sortable: false, show: true },
      { text: 'Number', value: 'number', sortable: false, show: this.showCol('Number') },
      { text: 'Type', value: 'type', sortable: false, show: this.showCol('Type') },
      { text: 'Status', value: 'status', sortable: false, show: this.showCol('Status') },
      { text: 'Folio', value: 'folio', sortable: false, show: this.showCol('Folio') && this.isPremiumAccount },
      { text: 'Last Modified', value: 'lastModified', sortable: false, show: this.showCol('Last Modified') },
      { text: 'Modified By', value: 'modifiedBy', sortable: false, show: this.showCol('Modified By') },
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

  .names-block {
    display: table;
  }

  .names-text {
    display: table-cell;
    vertical-align: top;
  }

  th {
    font-weight: bold;
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
        color: $gray7;
        padding: 1rem .875rem;
        line-height: 1.125rem;
      }

      td:first-child {
        width: 250px
      }

      td:not(:first-child):not(:last-child) {
        max-width: 5rem;
      }

      .type-col {
        min-width: 12rem;
      }
    }
  }

  .action-cell {
    width: 0;
    text-align: end !important;
    padding-right: 0;
  }

  .actions {
    .open-action {
      border-right: 1px solid $gray1;
    }

    .open-action-btn {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }

    .more-actions-btn {
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }

    .v-btn + .v-btn {
      margin-left: 0.5rem;
    }
  }
}

// Vuetify Overrides
::v-deep .v-list-item {
  min-height: 2rem !important;

  :hover {
    cursor: pointer;
  }
}

::v-deep .v-data-table--fixed-header thead th {
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
</style>
