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
          <v-btn :disabled="!canChangeRole(item)" small depressed v-on="on">
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
              :disabled="!isRoleEnabled(role)"
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
      <v-btn :disabled="!canRemove(item)" v-show="!canLeave(item)" depressed small @click="confirmRemoveMember(item)">Remove</v-btn>
      <v-btn v-show="canLeave(item)" depressed small @click="confirmLeaveTeam(item)">Leave</v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, RoleInfo } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
import moment from 'moment'

export interface ChangeRolePayload {
  member: Member;
  targetRole: string;
}

@Component({
  computed: {
    ...mapState('org', ['activeOrgMembers']),
    ...mapGetters('org', ['myOrgMembership'])
  },
  methods: {
    ...mapActions('org', ['syncActiveOrgMembers'])
  }
})
export default class MemberDataTable extends Vue {
  private readonly activeOrgMembers!: Member[]
  private readonly myOrgMembership!: Member
  private readonly syncActiveOrgMembers!: () => Member[]

  private readonly availableRoles: RoleInfo[] = [
    {
      icon: 'mdi-account',
      name: 'Member',
      desc: 'Can add businesses, and file for a business.'
    },
    {
      icon: 'mdi-settings',
      name: 'Admin',
      desc: 'Can add/remove team members, add businesses, and file for a business.'
    },
    {
      icon: 'mdi-shield-key',
      name: 'Owner',
      desc: 'Can add/remove team members and businesses, and file for a business.'
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

  private isRoleEnabled (role: RoleInfo): boolean {
    if (role.name !== 'Owner') {
      return true
    }

    if (this.myOrgMembership.membershipTypeCode === MembershipType.Owner) {
      return true
    }

    return false
  }

  private canChangeRole (memberBeingChanged: Member): boolean {
    // Can't change own role
    if (this.myOrgMembership.user.username === memberBeingChanged.user.username) {
      return false
    }

    // If member, can't change any roles
    if (this.myOrgMembership.membershipTypeCode === MembershipType.Member) {
      return false
    }

    // If not an active member, can't change
    if (this.myOrgMembership.membershipStatus !== MembershipStatus.Active) {
      return false
    }

    // Only owners can change owner roles
    if (memberBeingChanged.membershipTypeCode === MembershipType.Owner &&
        this.myOrgMembership.membershipTypeCode !== MembershipType.Owner) {
      return false
    }

    return true
  }

  private canRemove (memberToRemove: Member): boolean {
    // Can't remove yourself
    if (this.myOrgMembership.user.username === memberToRemove.user.username) {
      return false
    }

    // Can't remove unless Admin/Owner
    if (this.myOrgMembership.membershipTypeCode === MembershipType.Member) {
      return false
    }

    // Can't remove Owners unless an Owner
    if (memberToRemove.membershipTypeCode === MembershipType.Owner &&
        this.myOrgMembership.membershipTypeCode !== MembershipType.Owner) {
      return false
    }

    return true
  }

  private canLeave (member: Member): boolean {
    if (this.myOrgMembership.user.username !== member.user.username) {
      return false
    }
    return true
  }

  private ownerCount (): number {
    return this.activeOrgMembers.filter(member => member.membershipTypeCode === MembershipType.Owner).length
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

  private confirmLeaveTeam (member: Member) {
    if (member.membershipTypeCode === MembershipType.Owner && this.ownerCount() === 1) {
      this.$emit('single-owner-error')
    } else {
      this.$emit('confirm-leave-team')
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
      background: $BCgovBlue0;
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
