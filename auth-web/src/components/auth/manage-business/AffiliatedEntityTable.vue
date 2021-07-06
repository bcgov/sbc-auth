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
          fixed-header
          height="30rem"
          hide-default-footer
      >
        <template v-slot:item="{ item, index }">
          <tr>
            <td class="copy-normal">{{item.name}}</td>
            <td v-if="showCol(headers[1].text)" class="copy-normal">{{item.number}}</td>
            <td v-if="showCol(headers[2].text)" class="copy-normal">{{item.type}}</td>
            <td v-if="showCol(headers[3].text)" class="copy-normal">{{item.status}}</td>
            <td v-if="showCol(headers[4].text) && isPremiumAccount" class="copy-normal">{{item.folio}}</td>
            <td v-if="showCol(headers[5].text)" class="copy-normal">{{item.lastModified}}</td>
            <td v-if="showCol(headers[6].text)" class="copy-normal">{{item.modifiedBy}}</td>
            <td class="copy-normal action-cell">
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
                      <v-list-item class="actions-dropdown_item">
                        <v-list-item-subtitle @click="open(item)">
                          <v-icon small>mdi-file-certificate-outline</v-icon>
                          <span class="pl-1">Incorporate Now</span>
                        </v-list-item-subtitle>
                      </v-list-item>
                      <v-list-item class="actions-dropdown_item">
                        <v-list-item-subtitle @click="removeBusiness(item)">
                          <v-icon small>mdi-delete</v-icon>
                          <span class="pl-1">Remove</span>
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
import { Business, BusinessRequest } from '@/models/business'
import { Component, Emit, Prop, Watch } from 'vue-property-decorator'
import { CorpType, FilingTypes, LegalTypes, SessionStorageKeys } from '@/util/constants'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
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
  @Prop({ default: () => [] })
  readonly affiliatedEntities: Array<any>

  @Prop({ default: [] })
  readonly selectedColumns: Array<string>

  // Local Properties
  private readonly businesses!: Business[]
  private readonly currentOrganization!: Organization
  private readonly createNamedBusiness!: (filingBody: BusinessRequest) => any
  private headers: Array<any> = []
  private readonly isPremiumAccount!: boolean
  private isLoading: boolean = false

  /** V-model for dropdown menus. */
  private dropdown: Array<boolean> = []

  /** The number of affiliated entities or name requests. **/
  private get entityCount (): number {
    return this.businesses.length
  }

  /** Filter the headers we want to show. */
  private get getHeaders (): Array<any> {
    return this.headers.filter(x => x.show)
  }

  /** Open the businesses dashboard.
   * @param business The business information
   * */
  async open (business: Business): Promise<void> {
    // FUTURE STATE: The potential actions here will diverge dependant on STATUS and TYPE of the business or NR.
    let businessIdentifier = business.businessIdentifier
    // 3806 : Create new IA if the selected item is Name Request
    // If the business is NR, indicates there is no temporary business. Create a new IA for this NR and navigate.
    if (business.corpType.code === CorpType.NAME_REQUEST) {
      this.isLoading = true
      const filingBody: BusinessRequest = {
        filing: {
          header: {
            name: FilingTypes.INCORPORATION_APPLICATION,
            accountId: this.currentOrganization.id
          },
          business: {
            legalType: LegalTypes.BCOMP
          },
          incorporationApplication: {
            nameRequest: {
              legalType: LegalTypes.BCOMP,
              nrNumber: business.businessIdentifier
            }
          }
        }
      }
      const filingResponse = await this.createNamedBusiness(filingBody)
      this.isLoading = false
      // Find business with name as the NR number and use it for redirection
      businessIdentifier = filingResponse.data.filing.business.identifier
    }
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
    let redirectURL = `${ConfigHelper.getBusinessURL()}${businessIdentifier}`

    window.location.href = decodeURIComponent(redirectURL)
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
      { text: 'Number', value: 'number', sortable: false, show: this.showCol('Number') },
      { text: 'Type', value: 'type', sortable: false, show: this.showCol('Type') },
      { text: 'Status', value: 'status', sortable: false, show: this.showCol('Status') },
      { text: 'Folio', value: 'folio', sortable: false, show: this.showCol('Folio') && this.isPremiumAccount },
      { text: 'Last Modified', value: 'lastModified', sortable: false, show: this.showCol('Last Modified') },
      { text: 'Modified By', value: 'modifiedBy', sortable: false, show: this.showCol('Modified By') },
      { text: 'Actions', align: 'end', value: 'action', sortable: false, show: true }
    ]
  }

  /** Is true when the selected columns includes the column argument. */
  private showCol = (col): boolean => {
    return this.selectedColumns.includes(col)
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

  tbody {
    tr {
      vertical-align: top;

      &:hover {
        cursor: pointer;
        background-color: $app-lt-blue !important;
      }

      td {
        padding: 1rem .875rem;
        line-height: 1.125rem;
      }

      td:not(:first-child):not(:last-child) {
        max-width: 5rem;
      }
    }
  }

  .action-cell {
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

::v-deep .theme--light.v-data-table thead tr:last-child th:last-child span {
  padding-right: 85px;
}

::v-deep .theme--light.v-list-item .v-list-item__action-text, .theme--light.v-list-item .v-list-item__subtitle {
  color: #1669BB;
  .v-icon.v-icon {
    color: #1669BB;
  }
}
</style>
