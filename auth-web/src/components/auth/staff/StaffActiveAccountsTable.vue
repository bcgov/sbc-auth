<template>
  <v-data-table
    class="account-list"
    :headers="headerAccounts"
    :items="activeOrgs"
    :server-items-length="totalAccountsCount"
    :no-data-text="$t('noActiveAccountsLabel')"
    :options.sync="tableDataOptions"
    :disable-sort="true"
    :footer-props="{
      itemsPerPageOptions: getPaginationOptions
    }"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:item.orgType="{ item }">
        {{formatType(item)}}
    </template>
    <template v-slot:item.decisionMadeBy="{ item }">
        {{item.decisionMadeBy ? item.decisionMadeBy : 'N/A'}}
    </template>

    <template v-slot:item.action="{ item }">
      <v-btn
        outlined
        color="primary"
        class="action-btn"
        :data-test="getIndexedTag('view-account-button', item.id)"
        @click="view(item)"
      >
        View
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { AccessType, Account, AccountStatus, SessionStorageKeys } from '@/util/constants'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Member, OrgFilterParams, OrgList, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import OrgModule from '@/store/modules/org'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapActions('org', ['syncOrganization', 'addOrgSettings', 'syncMembership']),
    ...mapActions('staff', ['searchOrgs'])
  }
})
export default class StaffActiveAccountsTable extends Vue {
  private orgStore = getModule(OrgModule, this.$store)

  private activeOrgs: Organization[] = []
  private readonly syncOrganization!: (currentAccount: number) => Promise<Organization>
  private readonly addOrgSettings!: (org: Organization) => Promise<UserSettings>
  private readonly syncMembership!: (orgId: number) => Promise<Member>
  private readonly searchOrgs!: (filterParams: OrgFilterParams) => OrgList

  @Prop({ default: undefined }) private columnSort: any;

  private readonly headerAccounts = [
    {
      text: 'Name',
      align: 'left',
      sortable: true,
      value: 'name'
    },
    {
      text: 'Type',
      align: 'left',
      sortable: true,
      value: 'orgType'
    },
    {
      text: 'Approved By',
      align: 'left',
      sortable: true,
      value: 'decisionMadeBy'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '105'
    }
  ]

  private formatDate = CommonUtils.formatDisplayDate

  private readonly ITEMS_PER_PAGE = 10
  private readonly PAGINATION_COUNTER_STEP = 4
  private totalAccountsCount = 0
  private tableDataOptions: any = {}
  private orgFilter: OrgFilterParams

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private get getPaginationOptions () {
    return [...Array(this.PAGINATION_COUNTER_STEP)].map((value, index) => this.ITEMS_PER_PAGE * (index + 1))
  }

  @Watch('tableDataOptions', { deep: true })
  async getAccounts (val, oldVal) {
    this.orgFilter = {
      status: AccountStatus.ACTIVE,
      pageNumber: val?.page || 1,
      pageLimit: val?.itemsPerPage || this.ITEMS_PER_PAGE
    }
    const activeAccountsResp = await this.searchOrgs(this.orgFilter)
    this.activeOrgs = activeAccountsResp.orgs
    this.totalAccountsCount = activeAccountsResp?.total || 0
  }

  private async view (org: Organization) {
    let orgId:number = org.id
    await this.syncOrganization(orgId)
    await this.addOrgSettings(org)
    await this.syncMembership(orgId)
    this.$router.push(`/account/${orgId}/settings`)
  }

  private formatType (org:Organization):string {
    let orgTypeDisplay = org.orgType === Account.BASIC ? 'Basic' : 'Premium'
    if (org.accessType === AccessType.ANONYMOUS) {
      return 'Director Search'
    }
    if (org.accessType === AccessType.EXTRA_PROVINCIAL) {
      return orgTypeDisplay + '(out-of-province)'
    }
    return orgTypeDisplay
  }
}
</script>

<style lang="scss" scoped>
::v-deep {
  table {
    table-layout: fixed;

    td {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }
  }
}

.action-btn {
  width: 5rem;
}
</style>
