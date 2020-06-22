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
      <div class="btn-inline">
        <v-btn
          :data-test="getIndexedTag('reset-password-button', item.id)"
          depressed
          outlined
          color="primary"
          class="mr-2 font-weight-bold"
          small
          @click="view(item)"
        >View</v-btn
        >
      </div>
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
      text: 'Contact Email',
      align: 'left',
      sortable: true,
      value: 'email'
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
      width: '80'
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
@import '$assets/scss/theme.scss';

.v-list--dense {
  .v-list-item .v-list-item__title {
    margin-bottom: 0.25rem;
    font-weight: 700;
  }
}
</style>
