<template>
      <v-data-table
      class="incorporation-search-results"
      :headers="headersSearchResult"
      :items="searchResult"
      hide-default-footer
    >
      <template v-slot:loading>
        Loading...
      </template>
      <template v-slot:[`item.orgType`]="{ item }">
          {{formatType(item)}}
      </template>
      <template v-slot:[`item.action`]>
        <v-menu
        bottom
        left>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
            icon
            v-bind="attrs"
            v-on="on"
            >
              <v-icon>mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list
          dense
          >
              <v-list-item
              v-for="(action, i) in actions"
              :key="i"
              >
                <v-list-item-icon>
                  <v-icon v-text="action.icon"></v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title v-text="action.title"></v-list-item-title>
                </v-list-item-content>
                <v-list-item-action>
                </v-list-item-action>
              </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-data-table>
</template>

<script lang="ts">
import { AccessType, Account } from '@/util/constants'
import { Business, BusinessSearchResultDto } from '@/models/business'
import { Component, Vue } from 'vue-property-decorator'
import { Organization } from '@/models/Organization'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const BusinessModule = namespace('business')

@Component({
  data () {
    return {
      actions: [
        { title: 'Entity Dashboard',
          icon: 'mdi-view-dashboard'
        },
        { title: 'Manage Account',
          icon: 'mdi-domain'
        }
      ]
    }
  }
})
export default class IncorporationSearchResultView extends Vue {
  @OrgModule.State('currentOrganization') private currentOrganization!: Organization
  @BusinessModule.State('currentBusiness') private currentBusiness!: Business

  private get searchResult (): BusinessSearchResultDto[] {
    return [{
      name: this.currentBusiness?.name,
      orgType: this.currentOrganization?.orgType || 'N/A',
      account: this.currentOrganization?.name || 'No Affiliation',
      businessIdentifier: this.currentBusiness?.businessIdentifier,
      businessNumber: this.currentBusiness?.businessNumber,
      accessType: this.currentOrganization?.accessType,
      statusCode: this.currentOrganization?.statusCode
    }]
  }
  private readonly headersSearchResult = [
    {
      text: 'Name',
      align: 'left',
      value: 'name',
      width: '40%'
    },
    {
      text: 'Type',
      align: 'left',
      value: 'orgType',
      width: '15%'
    },
    {
      text: 'Account',
      value: 'account',
      width: '30%'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      width: '15%'
    }
  ]

  private formatType (org:BusinessSearchResultDto): string {
    let orgTypeDisplay = org?.orgType === Account.BASIC ? 'Basic' : 'Premium'
    if (org?.accessType === AccessType.ANONYMOUS) {
      return 'Director Search'
    }
    if (org?.accessType === AccessType.EXTRA_PROVINCIAL) {
      return orgTypeDisplay + ' (out-of-province)'
    }
    return orgTypeDisplay
  }
}
</script>

<style lang="scss" scoped>

</style>
