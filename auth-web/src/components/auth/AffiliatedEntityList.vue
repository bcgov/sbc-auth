<template>
  <div>
    <div class="empty-business-panel" v-if="affiliatedEntities.length === 0">
      <v-card>
        <v-card-text>
          <p class="business-list-empty-message">{{ $t('businessListEmptyMessage')}}</p>
          <p><a @click="addBusiness()">{{ $t('businessListActionMessage')}}</a></p>
        </v-card-text>
      </v-card>
    </div>
    <ul class="org-details" v-if="affiliatedEntities.length > 0">
      <li
        class="list-item"
        v-for="entity in affiliatedEntities"
        v-bind:key="entity.businessIdentifier">
        <v-card>
          <v-card-text class="card-layout">
            <div class="list-item_entity-number">
              <a @click="redirectToNext(entity.businessIdentifier)">{{entity.name}}</a>
            </div>
            <dl class="meta-container">
              <dt>Business No:</dt>
              <dd class="list-item_business-number">{{ entity.businessNumber}}</dd>
              <dt>Incorporation No:</dt>
              <dd class="list-item_incorp-number">{{ entity.businessIdentifier}}</dd>
            </dl>
          </v-card-text>
        </v-card>
      </li>
    </ul>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Emit } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import UserModule from '../../store/modules/user'
import configHelper from '../../util/config-helper'
import { AffiliatedEntity } from '../../models/Organization'

@Component
export default class AffiliatedEntityList extends Vue {
  private VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private userStore = getModule(UserModule, this.$store)

  mounted () {
    this.userStore.getOrganizations()
  }

  get affiliatedEntities () {
    let affiliatedEntities:AffiliatedEntity[] = []
    this.userStore.organizations.forEach(organization => {
      if (organization.affiliatedEntities) {
        organization.affiliatedEntities.forEach(entity => {
          affiliatedEntities.push(entity)
        })
      }
    })
    return affiliatedEntities
  }

  @Emit()
  addBusiness () {
  }

  redirectToNext (incorporationNumber: String) {
    if (this.VUE_APP_COPS_REDIRECT_URL) {
      // Temporary code: Must change once the solution is finalized.
      const redirectURL = this.VUE_APP_COPS_REDIRECT_URL + '/dashboard?corp=' + incorporationNumber
      window.location.href = decodeURIComponent(redirectURL)
    }
  }
}
</script>

<style lang="stylus" scoped>
.org-details {
  padding: 0
  list-style-type: none
  margin-right: 1.5rem
  margin-bottom: 1.5rem
}

.list-item {
  flex-direction: row
  align-items: center
  background: #ffffff
}

.card-layout {
  padding: 1.5rem
}

h2 {
  margin-bottom: 1.5rem
}

p {
  text-align: center
}

.business-list-empty-message {
  font-weight: 500
}

.list-item_entity-number {
  font-weight: 500
}

a {
  color: black
}

.meta-container {
  overflow: hidden
  color: $gray6
  font-size: 0.875rem
}

dd, dt {
  float: left
}

dt {
  position: relative
}

dd {
  margin-left: 0.5rem

  + dt {
    &:before {
      content: '•'
      display: inline-block
      margin-right: 0.75rem
      margin-left: 0.75rem
    }
  }
}

.empty-business-panel {
  margin-right: 1.5rem
}
</style>
