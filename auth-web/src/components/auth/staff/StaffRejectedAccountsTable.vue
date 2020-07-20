<template>
  <v-data-table
    class="user-list"
    :headers="headerAccounts"
    :items="rejectedStaffOrgs"
    :items-per-page="5"
    :hide-default-footer="rejectedStaffOrgs.length <= 5"
    :custom-sort="columnSort"
    :no-data-text="$t('noActiveAccountsLabel')"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:item.action="{ item }">
        <v-btn
          outlined
          color="primary"
          class="action-btn"
          :data-test="getIndexedTag('reset-password-button', item.id)"
          @click="view(item)"
        >
          View
        </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { AccessType, Account } from '@/util/constants'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import { Organization } from '@/models/Organization'

@Component({
  computed: {
    ...mapState('staff', [
      'rejectedStaffOrgs'
    ])
  }
})
export default class StaffRejectedAccountsTable extends Vue {
  private readonly rejectedStaffOrgs!: Organization[]

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
      text: 'Rejected By',
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

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private view (item) {
    this.$router.push(`/review-account/${item.id}`)
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
