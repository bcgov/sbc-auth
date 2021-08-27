<template>
  <div class="entity-list-component">

    <!-- No Results Message -->
    <v-card flat
      class="no-results text-center"
      v-if="businesses.length === 0 && !isLoading"
      @click="addBusiness()"
      data-test="no-businesses-message"
    >
      <v-card-title class="pt-6 pb-0">{{ $t('businessListEmptyMessage')}}</v-card-title>
      <v-card-text class="pb-8">{{ $t('businessListActionMessage')}}</v-card-text>
    </v-card>

    <!-- Business Data Table -->
    <v-card flat v-if="businesses.length > 0 || isLoading">
      <v-card-text class="p-1">
        <v-data-table
          :loading="isLoading"
          loading-text="Loading... Please wait"
          :headers="tableHeaders"
          :items="businesses"
          :items-per-page="5"
          :hide-default-footer="businesses.length <= 5"
          :custom-sort="customSort"
          :calculate-widths="true"
        >
          <template v-slot:[`item.info`]="{ item }">
            <div class="meta">
              <v-list-item-title v-if="isNumberedIncorporationApplication(item)">Numbered Benefit Company</v-list-item-title>
              <v-list-item-title v-if="!isNumberedIncorporationApplication(item)">{{ item.name }}</v-list-item-title>
              <v-list-item-title v-if="!item.name && isNameRequest(item.corpType.code)">{{ getApprovedName(item) }}</v-list-item-title>
              <v-list-item-subtitle v-if="isIncorporationNumber(item.corpType.code)">Incorporation Number: {{ item.businessIdentifier }}</v-list-item-subtitle>
              <v-list-item-subtitle v-if="isNameRequest(item.corpType.code)">Name Request ({{ item.businessIdentifier }})</v-list-item-subtitle>
              <v-list-item-subtitle v-if="isTemporaryBusinessRegistration(item.corpType.code)">Incorporation Application</v-list-item-subtitle>
            </div>
          </template>

          <!-- Actions -->
          <template v-slot:[`item.action`]="{ item, index }">
            <div class="actions">
              <span class="open-action">
                <v-btn
                    small
                    color="primary"
                    min-width="5rem"
                    min-height="2rem"
                    class="open-action-btn"
                    data-test="open-action-button"
                    @click="open(item)"
                >
                  Open
                </v-btn>
              </span>

              <!-- More Actions Menu -->
              <span class="more-actions mr-4">
                <v-menu
                    offset-y left nudge-bottom="4"
                    v-model="index"
                >
                  <template v-slot:activator="{ on }">
                    <v-btn
                        small
                        color="primary"
                        min-height="2rem"
                        class="more-actions-btn"
                        v-on="on"
                    >
                      <v-icon>{{index ? 'mdi-menu-up' : 'mdi-menu-down'}}</v-icon>
                    </v-btn>
                  </template>
                  <v-list>
                    <v-list-item
                        v-if="isApprovedForIA(item)"
                        class="actions-dropdown_item"
                        data-test="use-name-request-button"
                        @click="createDraftGoToDashboard(item)"
                    >
                      <v-list-item-subtitle>
                        <v-icon small>mdi-file-certificate-outline</v-icon>
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
                        <v-icon small>mdi-delete</v-icon>
                        <span class="pl-1">Remove</span>
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </span>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import { Business, BusinessRequest, NameRequest } from '@/models/business'
import { Component, Emit, Vue } from 'vue-property-decorator'
import { CorpType, FilingTypes, LDFlags, LegalTypes, NrState, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus, MembershipType, Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import OrgModule from '@/store/modules/org'
import TeamManagement from '@/components/auth/account-settings/team-management/TeamManagement.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', ['currentOrganization', 'currentMembership'])
  },
  methods: {
    ...mapMutations('business', ['setCurrentBusiness']),
    ...mapActions('business', ['createNamedBusiness'])

  }
})
export default class AffiliatedEntityList extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private isLoading = true
  private readonly businesses!: Business[]
  private readonly currentOrganization!: Organization
  private readonly currentMembership!: Member
  private readonly setCurrentBusiness!: (business: Business) => void
  private readonly createNamedBusiness!: (filingBody: BusinessRequest) => any

  private get tableHeaders () {
    return [
      {
        text: 'Name',
        align: 'left',
        sortable: true,
        value: 'info'
      },
      {
        text: 'Actions',
        align: 'left',
        sortable: false,
        value: 'action',
        width: '270'
      }
    ]
  }

  /*
  private canRemove (): boolean {
    return this.currentMembership &&
            this.currentMembership.membershipStatus === MembershipStatus.Active &&
            this.currentMembership.membershipTypeCode === MembershipType.Admin
  }
   */

  private isIncorporationNumber (corpType: string): boolean {
    return corpType !== CorpType.NAME_REQUEST && corpType !== CorpType.NEW_BUSINESS
  }

  private isNameRequest (corpType: string): boolean {
    return corpType === CorpType.NAME_REQUEST
  }

  private isApprovedForIA (business: Business): boolean {
    // Split string tokens into an array to avoid false string matching
    const supportedEntityFlags = LaunchDarklyService.getFlag(LDFlags.IaSupportedEntities)?.split(' ') || []

    return this.isNameRequest(business.corpType.code) &&
      business.nameRequest?.enableIncorporation &&
      (business.nameRequest?.state === NrState.APPROVED || business.nameRequest?.state === NrState.CONDITIONAL) &&
      supportedEntityFlags?.includes(business.nameRequest?.legalType)
  }

  private isTemporaryBusinessRegistration (corpType: string): boolean {
    return corpType === CorpType.NEW_BUSINESS
  }

  private isNumberedIncorporationApplication (item: Business): boolean {
    return item.corpType.code === CorpType.NEW_BUSINESS && item.name === item.businessIdentifier
  }

  private getApprovedName (item: Business): any {
    const approvedName = item => {
      for (const nameItem of item.nameRequest?.names) {
        if (nameItem.state === NrState.APPROVED) {
          return nameItem.name
        }
      }
    }
    return approvedName(item) || item.nameRequest.names[0].name // Return first name if DRAFT (None Approved)
  }

  private customSort (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    if (index[0] === 'info') {
      items.sort((a, b) => {
        if (isDesc) {
          return a.name < b.name ? -1 : 1
        } else {
          return b.name < a.name ? -1 : 1
        }
      })
    }
    return items
  }

  async mounted () {
    this.isLoading = false
  }

  @Emit()
  addBusiness () { }

  @Emit()
  removeBusiness (business: Business): RemoveBusinessPayload {
    return {
      orgIdentifier: this.currentOrganization.id,
      business
    }
  }

  editContact (business: Business) {
    this.setCurrentBusiness(business)
    this.$router.push({ path: '/businessprofile', query: { redirect: `/account/${this.currentOrganization.id}` } })
  }

  private open (business: Business): void {
    if (business.corpType.code === CorpType.NAME_REQUEST) {
      this.goToNameRequest(business.nameRequest)
    } else {
      this.goToDashboard(business.businessIdentifier)
    }
  }

  private manageTeam (business: Business) {
    this.setCurrentBusiness(business)
    // Not ideal, as this makes the component less reusable
    // TODO: Come up with a better solution: global event bus?
    this.$parent.$emit('change-to', TeamManagement)
  }

  async createDraftGoToDashboard (business: Business) {
    let businessIdentifier = business.businessIdentifier
    // 3806 : Create new IA if the selected item is Name Request
    // If the business is NR, indicates there is no temporary business. Create a new IA for this NR and navigate.
    if (business.corpType.code === CorpType.NAME_REQUEST && business.nameRequest.state === NrState.APPROVED) {
      this.isLoading = true
      // Find business with name as the NR number and use it for redirection
      businessIdentifier = await this.createBusinessRecord(business)
      this.isLoading = false
    }
    this.goToDashboard(businessIdentifier)
  }

  private goToDashboard (businessIdentifier: string): void {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
    let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`

    window.location.href = decodeURIComponent(redirectURL)
  }

  private goToNameRequest (nameRequest: NameRequest): void {
    ConfigHelper.setNrCredentials(nameRequest)
    window.location.href = `${ConfigHelper.getNameRequestUrl()}nr/${nameRequest.id}`
  }

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
    } else {
      return filingResponse.data.filing.business.identifier
    }
  }
}
</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

.meta-container {
  overflow: hidden;
  color: $gray6;
}

.meta {
  .v-list-item__title {
    letter-spacing: -0.01rem;
    font-weight: 700;
  }

  .v-list-item__subtitle {
    color: $gray7;
  }
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

.actions-dropdown_item:hover {
  background-color: $app-background-blue;
}

dd,
dt {
  float: left;
}

dt {
  position: relative;
}

dd {
  margin-left: 0.5rem;

  + dt {
    &:before {
      content: "•";
      display: inline-block;
      margin-right: 0.75rem;
      margin-left: 0.75rem;
    }
  }
}

// No Results
// TODO: Move somewhere we can access globally
.no-results .v-card__title {
  font-size: 1rem;
  font-weight: 700;
}

.no-results .v-card__title,
.no-results .v-card__text {
  justify-content: center;
}

::v-deep {
  .v-data-table.user-list__active td {
    height: 4rem;
    vertical-align: top;
  }
  .v-data-table td {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
  }
}

// Vuetify Overrides
::v-deep .v-list-item {
  min-height: 2rem !important;

  :hover {
    cursor: pointer;
  }
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
