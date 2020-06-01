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
          <template v-slot:item.info="{ item }">
            <div class="meta">
              <v-list-item-title>{{ item.name }}</v-list-item-title>
              <v-list-item-subtitle v-if="!isNameRequest(item.corpType.code)">Incorporation Number: {{ item.businessIdentifier }}</v-list-item-subtitle>
              <v-list-item-subtitle v-if="isNameRequest(item.corpType.code)">{{ item.corpType.desc }}: {{ item.businessIdentifier }}</v-list-item-subtitle>
            </div>
          </template>
          <template v-slot:item.action="{ item }">
            <div class="actions">
              <v-btn small color="primary" @click="goToDashboard(item)" title="Go to Business Dashboard" data-test="goto-dashboard-button">Open</v-btn>
              <!-- <v-btn small depressed @click="editContact(item)" title="Edit Business Profile" data-test="edit-contact-button">Edit</v-btn> -->
              <v-btn v-can:REMOVE_BUSINESS.disable small depressed @click="removeBusiness(item)" title="Remove Business" data-test="remove-button">Remove</v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import { Business, NamedBusinessRequest } from '@/models/business'
import { Component, Emit, Vue } from 'vue-property-decorator'
import { CorpType, FilingTypes, LegalTypes, SessionStorageKeys } from '@/util/constants'
import { Member, MembershipStatus, MembershipType, Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'
import TeamManagement from '@/components/auth/TeamManagement.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', ['currentOrganization', 'currentMembership'])
  },
  methods: {
    ...mapMutations('business', ['setCurrentBusiness']),
    ...mapActions('business', ['createNamedBusiness', 'syncBusinesses'])

  }
})
export default class AffiliatedEntityList extends Vue {
  private VUE_APP_COPS_REDIRECT_URL = ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private orgStore = getModule(OrgModule, this.$store)
  private isLoading = true
  private readonly businesses!: Business[]
  private readonly currentOrganization!: Organization
  private readonly currentMembership!: Member
  private readonly setCurrentBusiness!: (business: Business) => void
  private readonly createNamedBusiness!: (filingBody: NamedBusinessRequest) => any
  private readonly syncBusinesses!: () => Promise<Business[]>

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

  private isNameRequest (corpType: string): boolean {
    return corpType === CorpType.NAME_REQUEST || corpType === CorpType.NEW_BUSINESS
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

  async goToDashboard (business: Business) {
    let businessIdentifier = business.businessIdentifier
    // 3806 : Create new IA if the selected item is Name Request
    // If the business is NR, indicates there is no temporary business. Create a new IA for this NR and navigate.
    if (business.corpType.code === CorpType.NAME_REQUEST) {
      const namedBusinessRequest: NamedBusinessRequest = {
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
              nrNumber: business.businessIdentifier
            }
          }
        }
      }
      const filingResponse = await this.createNamedBusiness(namedBusinessRequest)
      // Sync businesses to update the store
      await this.syncBusinesses()
      // Find business with name as the NR number and use it for redirection
      businessIdentifier = this.businesses.find(bus => bus.name === business.businessIdentifier).businessIdentifier
    }
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, businessIdentifier)
    let redirectURL = `${ConfigHelper.getCoopsURL()}${businessIdentifier}`

    window.location.href = decodeURIComponent(redirectURL)
  }

  private manageTeam (business: Business) {
    this.setCurrentBusiness(business)
    // Not ideal, as this makes the component less reusable
    // TODO: Come up with a better solution: global event bus?
    this.$parent.$emit('change-to', TeamManagement)
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
  .v-btn + .v-btn {
    margin-left: 0.4rem;
  }
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
</style>
