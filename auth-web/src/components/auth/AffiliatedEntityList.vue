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
              <v-list-item-subtitle v-if="!isNameRequest(item.corpType)">Incorporation Number: {{ item.businessIdentifier }}</v-list-item-subtitle>
              <v-list-item-subtitle v-if="isNameRequest(item.corpType)">Name Request Number: {{ item.businessIdentifier }}</v-list-item-subtitle>
            </div>
          </template>
          <template v-slot:item.action="{ item }">
            <div class="actions">
              <v-btn small color="primary" @click="goToDashboard(item)" title="Go to Business Dashboard" data-test="goto-dashboard-button">Dashboard</v-btn>
              <v-btn small depressed @click="editContact(item)" title="Edit Business Profile" data-test="edit-contact-button">Edit</v-btn>
              <v-btn :disabled="!canRemove()" small depressed @click="removeBusiness(item.businessIdentifier)" title="Remove Business" data-test="remove-button">Remove</v-btn>
            </div>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapMutations, mapState } from 'vuex'
import { Business } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'
import { SessionStorageKeys } from '@/util/constants'
import UserManagement from '@/components/auth/UserManagement.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', ['currentOrganization', 'currentMembership'])
  },
  methods: {
    ...mapMutations('business', ['setCurrentBusiness'])
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

  private canRemove (): boolean {
    return this.currentMembership &&
            this.currentMembership.membershipStatus === MembershipStatus.Active &&
            this.currentMembership.membershipTypeCode === MembershipType.Owner
  }

  private isNameRequest (corpType: string): boolean {
    return corpType === 'NR'
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
  removeBusiness (businessIdentifier: string): RemoveBusinessPayload {
    return {
      orgIdentifiers: [this.currentOrganization.id],
      businessIdentifier
    }
  }

  editContact (business: Business) {
    this.setCurrentBusiness(business)
    this.$router.push({ path: '/businessprofile', query: { redirect: `/account/${this.currentOrganization.id}` } })
  }

  goToDashboard (business: Business) {
    let redirectURL
    if (this.isNameRequest(business.corpType)) {
      ConfigHelper.addToSession(SessionStorageKeys.NamesRequestNumberKey, business.businessIdentifier)
      redirectURL = ConfigHelper.getNewBusinessURL() + 'create?nrNumber=' + business.businessIdentifier
    } else {
      ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, business.businessIdentifier)
      redirectURL = `${ConfigHelper.getCoopsURL()}dashboard/${business.businessIdentifier}`
    }
    window.location.href = decodeURIComponent(redirectURL)
  }

  private manageTeam (business: Business) {
    this.setCurrentBusiness(business)
    // Not ideal, as this makes the component less reusable
    // TODO: Come up with a better solution: global event bus?
    this.$parent.$emit('change-to', UserManagement)
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
