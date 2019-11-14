<template>
  <v-data-table
    class="user-list__active"
    :headers="headerMembers"
    :items="activeOrgMembers"
    :items-per-page="5"
    :calculate-widths="true"
    :hide-default-footer="activeOrgMembers.length <= 5"
    :custom-sort="customSortActive"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:item.name="{ item }">
      <v-list-item-title class="user-name">{{ item.user.firstname }} {{ item.user.lastname }}</v-list-item-title>
      <v-list-item-subtitle v-if="item.user.contacts && item.user.contacts.length > 0">{{ item.user.contacts[0].email }}</v-list-item-subtitle>
    </template>
    <template v-slot:item.role="{ item }">
      <v-menu offset-y>
        <template v-slot:activator="{ on }">
          <v-btn depressed small v-on="on">
            {{ item.membershipTypeCode }}
            <v-icon small class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item
            v-for="(role, index) in availableRoles"
            :key="index"
            @click="confirmChangeRole(item, role)"
          >
            <v-list-item-title>{{ role }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
    <template v-slot:item.lastActive="{ item }">
      {{ formatDate(item.user.modified) }}
    </template>
    <template v-slot:item.action="{ item }">
      <v-btn depressed small @click="confirmRemoveMember(item)">Remove</v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
import { Member } from '@/models/Organization'
import moment from 'moment'

export interface ChangeRolePayload {
  member: Member;
  targetRole: string;
}

@Component({
  computed: {
    ...mapState('org', ['activeOrgMembers']),
    ...mapGetters('org', ['myOrg'])
  },
  methods: {
    ...mapActions('org', ['syncActiveOrgMembers'])
  }
})
export default class MemberDataTable extends Vue {
  private readonly activeOrgMembers!: Member[]
  private readonly syncActiveOrgMembers!: () => Member[]

  private readonly availableRoles = [
    'Member',
    'Admin',
    'Owner'
  ]

  private readonly headerMembers = [
    {
      text: 'Team Member',
      align: 'left',
      sortable: true,
      value: 'name'
    },
    {
      text: 'Roles',
      align: 'left',
      sortable: true,
      value: 'role'
    },
    {
      text: 'Last Active',
      align: 'left',
      sortable: true,
      value: 'lastActive'
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
    await this.syncActiveOrgMembers()
  }

  private formatDate (date: Date) {
    return moment(date).format('DD MMM, YYYY')
  }

  private customSortActive (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    switch (index[0]) {
      case 'name':
        items.sort((a, b) => {
          if (isDesc) {
            return a.user.firstname < b.user.firstname ? -1 : 1
          } else {
            return b.user.firstname < a.user.firstname ? -1 : 1
          }
        })
        break
      case 'role':
        items.sort((a, b) => {
          if (isDesc) {
            return a.membershipTypeCode < b.membershipTypeCode ? -1 : 1
          } else {
            return b.membershipTypeCode < a.membershipTypeCode ? -1 : 1
          }
        })
        break
      case 'lastActive':
        items.sort((a, b) => {
          if (isDesc) {
            return a.user.modified < b.user.modified ? -1 : 1
          } else {
            return b.user.modified < a.user.modified ? -1 : 1
          }
        })
    }
    return items
  }

  @Emit()
  private confirmRemoveMember (member: Member) {}

  @Emit()
  private confirmChangeRole (member: Member, targetRole: string): ChangeRolePayload {
    return {
      member,
      targetRole
    }
  }
}
</script>

<style lang="scss" scoped>

</style>
