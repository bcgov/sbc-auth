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
              @click="action.event"
              >
                <v-list-item-icon>
                  <v-icon v-text="action.icon"></v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title v-text="action.title"></v-list-item-title>
                </v-list-item-content>
              </v-list-item>
          </v-list>
        </v-menu>
        <GeneratePasscodeView
        ref="generatePasscodeDialog"
        >
        </GeneratePasscodeView>
      </template>
    </v-data-table>
</template>

<script lang="ts">
import { AccessType, Account } from '@/util/constants'
import { Business, BusinessSearchResultDto } from '@/models/business'
import { Component, Vue } from 'vue-property-decorator'
import ConfigHelper from '@/util/config-helper'
import GeneratePasscodeView from '@/views/auth/staff/GeneratePasscodeView.vue'
import { Organization } from '@/models/Organization'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const BusinessModule = namespace('business')

@Component({
  components: {
    GeneratePasscodeView
  }
})
export default class IncorporationSearchResultView extends Vue {
  @OrgModule.State('currentOrganization') private currentOrganization!: Organization
  @OrgModule.Action('addOrgSettings') private addOrgSettings!: (currentOrganization: Organization) => Promise<UserSettings>

  @BusinessModule.State('currentBusiness') private currentBusiness!: Business

  $refs: {
    generatePasscodeDialog: GeneratePasscodeView
  }

  private get actions (): object[] {
    if (this.currentOrganization?.name) {
      return [
        { title: 'Entity Dashboard',
          icon: 'mdi-view-dashboard',
          event: this.entityDashboardEvent
        },
        { title: 'Manage Account',
          icon: 'mdi-domain',
          event: this.manageAccountEvent
        }
      ]
    } else {
      return [
        { title: 'Entity Dashboard',
          icon: 'mdi-view-dashboard',
          event: this.entityDashboardEvent
        },
        { title: 'Generate Passcode',
          icon: 'mdi-lock-outline',
          event: this.generatePasscodeEvent
        }
      ]
    }
  }

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

  private async entityDashboardEvent () {
    window.location.href = `${ConfigHelper.getCoopsURL()}${this.currentBusiness.businessNumber}`
  }

  private async manageAccountEvent () {
    try {
      await this.addOrgSettings(this.currentOrganization)
      this.$router.push('/business')
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('Error during entity dashboard click event!')
    }
  }

  private generatePasscodeEvent () {
    this.$refs.generatePasscodeDialog.open()
  }
}
</script>
