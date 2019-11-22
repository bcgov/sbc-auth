<template>
  <v-data-table
    class="user-list"
    :headers="headerMembers"
    :items="activeOrgMembers"
    :items-per-page="5"
    :calculate-widths="true"
    :hide-default-footer="activeOrgMembers.length <= 5"
    :custom-sort="customSortActive"
    :no-data-text="$t('noActiveUsersLabel')"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:item.name="{ item }">
      <v-list-item-title class="user-name">{{ item.user.firstname }} {{ item.user.lastname }}</v-list-item-title>
      <v-list-item-subtitle v-if="item.user.contacts && item.user.contacts.length > 0">{{ item.user.contacts[0].email }}</v-list-item-subtitle>
    </template>
    <template v-slot:item.role="{ item }">
      <v-menu>
        <template v-slot:activator="{ on }">
          <v-btn small depressed v-on="on">
            {{ item.membershipTypeCode }}
            <v-icon small depressed class="ml-1">mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-item-group
            class="role-list">
            <v-list-item
              v-for="(role, index) in availableRoles"
              :key="index"
              @click="confirmChangeRole(item, role.name)"
              v-bind:class="{ active: item.membershipTypeCode.toUpperCase() === role.name.toUpperCase() }">
              <v-list-item-icon>
                <v-icon v-text="role.icon" />
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title
                  v-text="role.name"
                >
                </v-list-item-title>
                <v-list-item-subtitle
                  v-text="role.desc"
                >
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-item-group>
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
    {
      icon: 'mdi-shield-key',
      name: 'Owner',
      desc: 'Can add/remove team members and businesses, and file for a business.'
    },
    {
      icon: 'mdi-settings',
      name: 'Admin',
      desc: 'Can add/remove team members, add businesses, and file for a business.'
    },
    {
      icon: 'mdi-account',
      name: 'Member',
      desc: 'Can add businesses, and file for a business.'
    }
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
      width: '77'
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
  @import "$assets/scss/theme.scss";

  .v-list {
    padding-top: 0px;
    padding-bottom: 0px;
  }

  .role-list {
    max-width: 26rem;

    .v-list-item.active {
      background: $BCgovBlue2;
    }

    .v-list-item__title {
      letter-spacing: -0.02rem;
      font-size: 0.875rem;
      font-weight: 700;
    }

    .v-list-item__subtitle {
      white-space: normal;
      overflow: visible;
      line-height: 1.5;
      font-size: 0.875rem;
    }
  }
</style>
