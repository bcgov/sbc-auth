<template>
  <v-data-table
    class="user-list"
    :headers="headerAccounts"
    :items="rejectedStaffOrgs"
    :items-per-page.sync="tableDataOptions.itemsPerPage"
    :hide-default-footer="rejectedStaffOrgs.length <= tableDataOptions.itemsPerPage"
    :custom-sort="columnSort"
    :no-data-text="$t('noActiveAccountsLabel')"
    :footer-props="{
        itemsPerPageOptions: getPaginationOptions
      }"
    :options.sync="tableDataOptions"
    @update:items-per-page="saveItemsPerPage"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:[`item.action`]="{ item }">
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
import { Component, Mixins, Prop } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { DataOptions } from 'vuetify'
import { Organization } from '@/models/Organization'
import PaginationMixin from '@/components/auth/mixins/PaginationMixin.vue'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('staff', [
      'rejectedStaffOrgs'
    ])
  }
})
export default class StaffRejectedAccountsTable extends Mixins(PaginationMixin) {
  private readonly rejectedStaffOrgs!: Organization[]

  private columnSort = CommonUtils.customSort

  private tableDataOptions: Partial<DataOptions> = {}

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

  mounted () {
    this.tableDataOptions = this.DEFAULT_DATA_OPTIONS
    if (this.hasCachedPageInfo) {
      this.tableDataOptions = this.getAndPruneCachedPageInfo()
    }
  }

  private view (item) {
    this.cachePageInfo(this.tableDataOptions)
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
