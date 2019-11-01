<template>
  <div class="entity-list-component">
    <!-- Loading status -->
    <v-progress-circular
      :indeterminate=true
      v-if="isLoading"
    />

    <!-- No Results Message -->
    <v-card
      class="no-results text-center"
      v-if="basicAffiliations.length === 0 && !isLoading"
      @click="addBusiness()"
    >
      <v-card-title class="pt-6 pb-0">{{ $t('businessListEmptyMessage')}}</v-card-title>
      <v-card-text class="pb-8">{{ $t('businessListActionMessage')}}</v-card-text>
    </v-card>

    <div v-if="!isLoading" class="entity-details">
      <v-row
        v-for="business in basicAffiliations"
        v-bind:key="business.businessIdentifier"
        class="mb-3"
      >
        <v-card width="100%">
          <v-card-title class="list-item_entity-number">
            <a @click="redirectToNext(business.businessIdentifier)">{{business.name}}</a>
            <span>
              <v-btn outlined small class="mr-2" @click="editContact(business.businessIdentifier)">
                Edit
              </v-btn>
              <v-btn outlined small color="red" @click="removeBusiness(business.businessIdentifier)">
                Remove
              </v-btn>
            </span>
          </v-card-title>
          <v-card-text class="card-layout">
            <dl class="meta-container">
              <dt>Business No:</dt>
              <dd class="list-item_business-number">{{ business.businessNumber }}</dd>
              <dt>Incorporation No:</dt>
              <dd class="list-item_incorp-number">{{ business.businessIdentifier }}</dd>
            </dl>
          </v-card-text>
        </v-card>
      </v-row>
    </div>
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
import _ from 'lodash'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['organizations'])
  },
  methods: {
    ...mapMutations('business', ['setCurrentBusiness']),
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

  private get implicitOrgs () {
    return this.organizations.filter(org => org.orgType === 'IMPLICIT')
  }

  private get basicAffiliations () {
    return _.uniqWith(
      _.flatten(this.implicitOrgs.map(org => org.affiliatedEntities)),
      (businessA: Business, businessB: Business) => businessA.businessIdentifier === businessB.businessIdentifier
    )
  }

  private get businessById () {
    return (businessIdentifier: string) => {
      return this.basicAffiliations.find(business => business.businessIdentifier === businessIdentifier)
    }
  }

  async created () {
    this.isLoading = true
    await this.syncOrganizations()
    this.isLoading = false
  }

  @Emit()
  addBusiness () { }

  @Emit()
  removeBusiness (businessIdentifier: string, orgId?: number): RemoveBusinessPayload {
    // If no orgId was supplied, remove affiliations between all implicit orgs and the specified business
    // Otherwise remove affiliation for the specific org
    if (!orgId) {
      return {
        orgIdentifiers: this.implicitOrgs
          .filter(org => org.affiliatedEntities && org.affiliatedEntities
            .some(business => business.businessIdentifier === businessIdentifier))
          .map(org => org.id),
        businessIdentifier
      }
    } else {
      return {
        orgIdentifiers: [orgId],
        businessIdentifier
      }
    }
  }

  editContact (businessidentifier: string) {
    this.setCurrentBusiness(this.businessById(businessidentifier))
    this.$router.push({ path: '/businessprofile', query: { redirect: '/main' } })
  }

  redirectToNext (incorporationNumber: string) {
    ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, incorporationNumber)
    const redirectURL = ConfigHelper.getCoopsURL() + 'dashboard'
    window.location.href = decodeURIComponent(redirectURL)
  }
}
</script>

<style lang="scss" scoped>
@import "../../assets/scss/theme.scss";

.org-details {
  padding: 0;
  list-style-type: none;
  margin-right: 1.5rem;
  margin-bottom: 1.5rem;
}

.entity-details {
  padding: 0;
  list-style-type: none;
}

.list-item {
  flex-direction: row;
  align-items: center;
  background: #ffffff;
}

.card-layout {
  padding: 1.5rem;
}

h2 {
  margin-bottom: 1.5rem;
}

p {
  text-align: center;
}

.business-list-empty-message {
  font-weight: 500;
}

.list-item_entity-number {
  font-weight: 500;
  display: flex;
  justify-content: space-between;
  padding-bottom: 0px !important;
}

a {
  color: black;
}

.meta-container {
  overflow: hidden;
  color: $gray6;
  font-size: 0.875rem;
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
  justify-content: center;
  font-size: 0.9375rem;
  font-weight: 700;
}

.no-results .v-card__text {
  font-size: 0.9375rem;
}
</style>
