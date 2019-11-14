<template>
  <v-data-table
    class="user-list__active"
    :headers="headerPendingMembers"
    :items="pendingOrgMembers"
    :items-per-page="5"
    :calculate-widths="true"
    :hide-default-footer="pendingOrgMembers.length <= 5"
    :custom-sort="customSortPending"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:item.name="{ item }">
      <v-list-item-title class="user-name">{{ item.user.firstname }} {{ item.user.lastname }}</v-list-item-title>
      <v-list-item-subtitle v-if="item.user.contacts && item.user.contacts.length > 0">{{ item.user.contacts[0].email }}</v-list-item-subtitle>
    </template>
    <template v-slot:item.action="{ item }">
      <v-btn depressed small @click="confirmApproveMember(item)">Approve</v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
import { Member } from '@/models/Organization'
import moment from 'moment'

@Component({
  computed: {
    ...mapState('org', ['pendingOrgMembers']),
    ...mapGetters('org', ['myOrg'])
  },
  methods: {
    ...mapActions('org', ['syncPendingOrgMembers'])
  }
})
export default class PendingMemberDataTable extends Vue {
  private readonly pendingOrgMembers!: Member[]
  private readonly syncPendingOrgMembers!: () => Member[]
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
      width: '95'
    }
  ]

  private async mounted () {
    await this.syncPendingOrgMembers()
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
}
</script>

<style lang="scss" scoped>

</style>
