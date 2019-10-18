<template>
  <div class="entity-list-component">
    <!-- No Results Message -->
    <v-card
      class="no-results text-center"
      v-if="affiliatedEntities.length === 0"
      @click="addBusiness()"
    >
      <v-card-title class="pt-6 pb-0">{{ $t('businessListEmptyMessage')}}</v-card-title>
      <v-card-text class="pb-8">{{ $t('businessListActionMessage')}}</v-card-text>
    </v-card>

    <ul class="org-details" v-if="affiliatedEntities.length > 0">
      <li class="list-item" v-for="org in organizations" v-bind:key="org.id">
        <ul class="entity-details">
          <li
            class="list-item"
            v-for="entity in org.affiliatedEntities"
            v-bind:key="entity.businessIdentifier"
          >
            <v-card class="mb-3">
              <v-card-title class="list-item_entity-number">
                <a @click="redirectToNext(entity.businessIdentifier)">{{entity.name}}</a>
                <v-icon @click="removeBusiness(org.id, entity.businessIdentifier)">close</v-icon>
              </v-card-title>
              <v-card-text class="card-layout">
                <dl class="meta-container">
                  <dt>Business No:</dt>
                  <dd class="list-item_business-number">{{ entity.businessNumber }}</dd>
                  <dt>Incorporation No:</dt>
                  <dd class="list-item_incorp-number">{{ entity.businessIdentifier }}</dd>
                </dl>
              </v-card-text>
            </v-card>
          </li>
        </ul>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import { AffiliatedEntity, Organization, RemoveBusinessPayload } from '@/models/Organization'
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
import OrgModule from '@/store/modules/org'
import { SessionStorageKeys } from '@/util/constants'
import configHelper from '@/util/config-helper'
import { getModule } from 'vuex-module-decorators'

@Component({
  computed: {
    ...mapState('org', ['organizations'])
  },
  methods: {
    ...mapActions('org', ['syncOrganizations'])
  }
})
export default class AffiliatedEntityList extends Vue {
  private VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private orgStore = getModule(OrgModule, this.$store)
  readonly organizations!: Organization[]
  readonly syncOrganizations!: () => Organization[]

  get affiliatedEntities () {
    let affiliatedEntities: AffiliatedEntity[] = []
    this.organizations.forEach(organization => {
      if (organization.affiliatedEntities) {
        organization.affiliatedEntities.forEach(entity => {
          affiliatedEntities.push(entity)
        })
      }
    })
    return affiliatedEntities
  }

  created () {
    this.syncOrganizations()
  }

  @Emit()
  addBusiness () { }

  @Emit()
  removeBusiness (orgId: number, incorporationNumber: string): RemoveBusinessPayload {
    return {
      orgIdentifier: orgId,
      incorporationNumber: incorporationNumber
    }
  }

  redirectToNext (incorporationNumber: string) {
    configHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, incorporationNumber)
    const redirectURL = configHelper.getCoopsURL() + 'dashboard'
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
