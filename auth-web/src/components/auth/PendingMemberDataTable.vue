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
    <template v-slot:item.name="{ item }">
      <v-list-item-title class="user-name" :data-test="getIndexedTag('pending-user-name', item.index)">{{ item.user.firstname }} {{ item.user.lastname }}</v-list-item-title>
      <v-list-item-subtitle :data-test="getIndexedTag('pending-email', item.index)" v-if="item.user.contacts && item.user.contacts.length > 0">{{ item.user.contacts[0].email }}</v-list-item-subtitle>
    </template>
    <template v-slot:item.action="{ item }">
      <v-btn :data-test="getIndexedTag('approve-button', item.index)" small color="primary" class="mr-2" @click="confirmApproveMember(item)">Approve</v-btn>
      <v-btn :data-test="getIndexedTag('deny-button', item.index)" depressed small @click="confirmDenyMember(item)">Deny</v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapState } from 'vuex'
import { Member } from '@/models/Organization'
import moment from 'moment'

@Component({
  computed: {
    ...mapState('org', ['pendingOrgMembers'])
  }
})
export default class PendingMemberDataTable extends Vue {
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
      align: 'left',
      value: 'action',
      sortable: false,
      width: '195'
    }
  ]

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private get indexedPendingMembers () {
    return this.pendingOrgMembers.map((item, index) => ({
      index,
      ...item
    }))
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

.role-list {
  width: 20rem;
}

.user-role-desc {
  white-space: normal !important;
}
</style>
