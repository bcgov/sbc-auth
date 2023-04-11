<template>
  <v-data-table
    class="user-list"
    :headers="headerPendingMembers"
    :items="indexedPendingMembers"
    :items-per-page="5"
    :calculate-widths="true"
    :hide-default-footer="indexedPendingMembers.length <= 5"
    :custom-sort="customSortPending"
    :no-data-text="$t('noPendingApprovalLabel')"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:[`item.name`]="{ item }">
      <div
        class="user-name font-weight-bold"
        :data-test="getIndexedTag('pending-user-name', item.index)"
      >
        {{ item.user.firstname }} {{ item.user.lastname }}
      </div>
      <div
        :data-test="getIndexedTag('pending-email', item.index)"
        v-if="item.user.contacts && item.user.contacts.length > 0"
      >
        {{ item.user.contacts[0].email }}
      </div>
    </template>
    <template v-slot:[`item.action`]="{ item }">
      <v-btn
        icon
        class="mr-1"
        aria-label="Approve user access to this account"
        title="Approve user access to this account"
        :data-test="getIndexedTag('approve-button', item.index)"
        @click="confirmApproveMember(item)"
      >
        <v-icon>mdi-check-circle-outline</v-icon>
      </v-btn>
      <v-btn
        icon
        aria-label="Deny access to this account"
        title="Deny access to this account"
        :data-test="getIndexedTag('deny-button', item.index)"
        @click="confirmDenyMember(item)"
      >
        <v-icon>mdi-close-circle-outline</v-icon>
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Member } from '@/models/Organization'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapState } from 'vuex'

@Component({
  computed: {
    ...mapState('org', ['pendingOrgMembers'])
  }
})
export default class PendingMemberDataTable extends Vue {
  @Prop({ default: '' }) private userNamefilterText: string
  private readonly pendingOrgMembers!: Member[]
  private readonly headerPendingMembers = [
    {
      text: 'Team Member',
      align: 'left',
      sortable: true,
      value: 'name'
    },
    {
      text: 'Actions',
      align: 'right',
      value: 'action',
      sortable: false
    }
  ]

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private get indexedPendingMembers () {
    let pendingMembers = []
    if (this.userNamefilterText) {
      // filter if the filter by username prop is available
      pendingMembers = this.pendingOrgMembers.filter((element) => {
        const username = `${element.user?.firstname || ''} ${element.user?.lastname || ''}`.trim()
        const found = username.match(new RegExp(this.userNamefilterText, 'i'))
        if (found?.length) {
          return element
        }
      })
      this.filteredMembersCount(pendingMembers.length)
    } else {
      pendingMembers = this.pendingOrgMembers
    }
    // map org members list with custom index and role mapping
    return pendingMembers.map((item, index) => ({
      index,
      ...item
    }))
  }

  @Emit()
  private filteredMembersCount (count: number) {
    return count
  }

  private customSortPending (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    items.sort((a, b) => {
      if (isDesc) {
        return a.user.firstname < b.user.firstname ? -1 : 1
      } else {
        return b.user.firstname < a.user.firstname ? -1 : 1
      }
    })
    return items
  }

  @Emit()
  private confirmApproveMember (member: Member) {}

  @Emit()
  private confirmDenyMember (member: Member) {}
}
</script>

<style lang="scss" scoped>
::v-deep {
  td {
    padding-top: 1rem !important;
    padding-bottom: 1rem !important;
    height: auto;
  }
}

.v-list--dense {
  .v-list-item .v-list-item__title {
    margin-bottom: 0.25rem;
    font-weight: 700;
  }
}

.user-role-desc {
  white-space: normal !important;
}
</style>
