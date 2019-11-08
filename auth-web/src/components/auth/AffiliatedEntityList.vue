<template>
  <div class="entity-list-component">

    <!-- No Results Message -->
    <v-card
      class="no-results text-center"
      v-if="myBusinesses.length === 0 && !isLoading"
      @click="addBusiness()"
    >
      <v-card-title class="pt-6 pb-0">{{ $t('businessListEmptyMessage')}}</v-card-title>
      <v-card-text class="pb-8">{{ $t('businessListActionMessage')}}</v-card-text>
    </v-card>

    <!-- Business Data Table -->
    <v-card v-if="myBusinesses.length > 0 && !isLoading">
      <v-data-table
        :loading="isLoading"
        loading-text="Loading... Please wait"
        :headers="tableHeaders"
        :items="myBusinesses"
        :items-per-page="5"
        :calculate-widths="true"
        :hide-default-footer="myBusinesses.length <= 5"
        :custom-sort="customSort"
      >
        <template v-slot:item.info="{ item }">
          <div class="meta">
            <v-list-item-title>{{ item.name }}</v-list-item-title>
            <v-list-item-subtitle>Incorporation Number: {{ item.businessIdentifier }}</v-list-item-subtitle>
          </div>
        </template>
        <template v-slot:item.action="{ item }">
          <div class="actions">
            <v-btn depressed small @click="goToDashboard(item.businessIdentifier)" title="Go to Business Dashboard">Dashboard</v-btn>
            <v-btn depressed small @click="editContact(item)" title="Edit Business Profile">Edit</v-btn>
            <v-btn depressed small @click="removeBusiness(item.businessIdentifier)" title="Remove Business">Remove</v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import { Business } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'
import { SessionStorageKeys } from '@/util/constants'
import UserManagement from '@/views/management/UserManagement.vue'
import _ from 'lodash'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['organizations'])
  },
  methods: {
    ...mapMutations('business', ['setCurrentBusiness']),
    ...mapMutations('org', ['setCurrentOrg']),
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class AffiliatedEntityList extends Vue {
  private VUE_APP_COPS_REDIRECT_URL = ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private orgStore = getModule(OrgModule, this.$store)
  private isLoading = true
  private readonly organizations!: Organization[]
  private readonly setCurrentBusiness!: (business: Business) => void
  private readonly syncOrganizations!: () => Organization[]
  private readonly setCurrentOrg!: (org: Organization) => void

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
        value: 'action',
        sortable: false,
        width: '300'
      }
    ]
  }

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
        value: 'action',
        sortable: false,
        width: '280'
      }
    ]
  }

  private get myOrg (): Organization {
    if (this.organizations && this.organizations.length > 0) {
      return this.organizations[0]
    }
    return undefined
  }

  private get myBusinesses () {
    return this.myOrg.affiliatedEntities
  }

  private get businessById () {
    return (businessIdentifier: string) => {
      return this.myBusinesses.find(business => business.businessIdentifier === businessIdentifier)
    }
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
      orgIdentifiers: [this.myOrg.id],
      businessIdentifier
    }
  }

  editContact (business: Business) {
    this.setCurrentBusiness(business)
    this.$router.push({ path: '/businessprofile', query: { redirect: '/main' } })
  }

  goToDashboard (incorporationNumber: string) {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, incorporationNumber)
    const redirectURL = ConfigHelper.getCoopsURL() + 'dashboard'
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

::v-deep .v-data-table td {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

::v-deep .v-data-table.user-list__active td {
  height: 4rem;
  vertical-align: top;
}

::v-deep .v-data-table td {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

::v-deep .v-data-table.user-list__active td {
  height: 4rem;
  vertical-align: top;
}
</style>
