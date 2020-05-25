<template>
  <v-data-table
    class="user-list"
    :headers="headerMembers"
    :items="indexedOrgMembers"
    :items-per-page="5"
    :hide-default-footer="indexedOrgMembers.length <= 5"
    :custom-sort="customSortActive"
    :no-data-text="$t('noActiveUsersLabel')"
  >
    <template v-slot:loading>
      Loading...
    </template>
    <template v-slot:item.name="{ item }">
      <v-list-item-title
        class="user-name"
        :data-test="getIndexedTag('user-name', item.index)"
        >{{ item.user.firstname }} {{ item.user.lastname }}</v-list-item-title>
      <v-list-item-subtitle
        :data-test="getIndexedTag('business-id', item.index)"
        v-if="item.user.contacts && item.user.contacts.length > 0"
      >{{ item.user.contacts[0].email }}</v-list-item-subtitle>
    </template>
    <template v-slot:item.role="{ item }">
      <v-menu>
        <template v-slot:activator="{ on }">
          <v-btn
            :disabled="!canChangeRole(item)"
            class="role-selector"
            small
            depressed
            v-on="on"
            :data-test="getIndexedTag('role-selector', item.index)"
          >
            {{ item.roleDisplayName }}
            <v-icon
              small
              depressed
              class="ml-1"
            >mdi-chevron-down</v-icon>
          </v-btn>
        </template>
        <v-list
          dense
          class="role-list"
        >
          <v-item-group>
            <v-list-item
              three-line
              v-for="(role, index) in roleInfos"
              :key="index"
              @click="item.membershipTypeCode.toUpperCase() !== role.name.toUpperCase()? confirmChangeRole(item, role.name): ''"
              :disabled="!isRoleEnabled(role)"
              v-bind:class="{'primary--text v-item--active v-list-item--active': item.membershipTypeCode.toUpperCase() === role.name.toUpperCase()}"
            >
              <v-list-item-icon>
                <v-icon v-text="role.icon" />
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title v-text="role.displayName">
                </v-list-item-title>
                <v-list-item-subtitle v-text="role.label">
                </v-list-item-subtitle>
                <v-divider></v-divider>
              </v-list-item-content>
            </v-list-item>
          </v-item-group>
        </v-list>
      </v-menu>

    </template>
    <template
      v-slot:item.lastActive="{ item }"
      :data-test="getIndexedTag('last-active', item.index)"
    >
      {{ formatDate(item.user.modified) }}
    </template>
    <template v-slot:item.action="{ item }">
      <v-btn
        :data-test="getIndexedTag('remove-user-button', item.index)"
        v-show="canRemove(item)"
        depressed
        small
        @click="confirmRemoveMember(item)"
      >Remove</v-btn>
      <v-btn
        :data-test="getIndexedTag('leave-team-button', item.index)"
        v-show="canLeave(item)"
        depressed
        small
        @click="confirmLeaveTeam(item)"
      >
        <span v-if="!canDissolve()">Leave</span>
        <span v-if="canDissolve()">Dissolve</span>
      </v-btn>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Emit, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization, RoleInfo } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import { Account } from '@/util/constants'
import { Business } from '@/models/business'
import CommonUtils from '@/util/common-util'

export interface ChangeRolePayload {
  member: Member
  targetRole: string
}

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', ['activeOrgMembers', 'currentMembership', 'currentOrganization']),
    ...mapState('user', ['roleInfos'])
  },
  methods: {
    ...mapActions('user', [
      'getRoleInfo'
    ])
  }
})
export default class MemberDataTable extends Vue {
  private readonly businesses!: Business[]
  private activeOrgMembers!: Member[]
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly getRoleInfo!: () => Promise<RoleInfo[]>
  private readonly roleInfos!: RoleInfo[]

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
      width: '80'
    }
  ]

  private formatDate = CommonUtils.formatDisplayDate

  private async mounted () {
    // need not to reload everytime .roles seldom changes
    if (!this.roleInfos) {
      await this.getRoleInfo()
    }
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private get indexedOrgMembers () {
    // eslint-disable-next-line no-console
    var self = this
    this.activeOrgMembers.forEach(function (element) {
      element.roleDisplayName = self.roleInfos.find(role => role.name === element.membershipTypeCode).displayName
    })
    return this.activeOrgMembers.map((item, index) => ({
      index,
      ...item
    }))
  }

  private isRoleEnabled (role: RoleInfo): boolean {
    switch (this.currentMembership.membershipTypeCode) {
      case MembershipType.Admin:
        return true
      case MembershipType.Coordinator:
        if (role.name !== 'Admin') {
          return true
        }
        return false
      default:
        return false
    }
  }

  private canChangeRole (memberBeingChanged: Member): boolean {
    if (this.currentMembership.membershipStatus !== MembershipStatus.Active) {
      return false
    }

    switch (this.currentMembership.membershipTypeCode) {
      case MembershipType.Admin:
        // Owners can change roles of other users who are not owners
        if (!this.isOwnMembership(memberBeingChanged) && memberBeingChanged.membershipTypeCode !== MembershipType.Admin) {
          return true
        }
        // And they can downgrade their own role if there is another owner on the team
        if (this.isOwnMembership(memberBeingChanged) && this.ownerCount() > 1) {
          return true
        }
        return false
      case MembershipType.Coordinator:
        // Admins can change roles of their own
        return this.isOwnMembership(memberBeingChanged)
      default:
        return false
    }
  }

  private canRemove (memberToRemove: Member): boolean {
    // Can't remove yourself
    if (this.currentMembership.user.username === memberToRemove.user.username) {
      return false
    }

    // Can't remove unless Admin/Owner
    if (this.currentMembership.membershipTypeCode === MembershipType.User) {
      return false
    }

    // Can't remove Admin unless Owner
    if (this.currentMembership.membershipTypeCode === MembershipType.Admin &&
      memberToRemove.membershipTypeCode === MembershipType.Coordinator) {
      return false
    }

    // No one can change an OWNER's status, only option is OWNER to leave the team. #2319
    if (memberToRemove.membershipTypeCode === MembershipType.Admin) {
      return false
    }

    return true
  }

  private canLeave (member: Member): boolean {
    if (this.currentMembership.user.username !== member.user.username) {
      return false
    }
    return true
  }

  private ownerCount (): number {
    return this.activeOrgMembers.filter(member => member.membershipTypeCode === MembershipType.Admin).length
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

  private canDissolve (): boolean {
    if (this.activeOrgMembers.length === 1 && this.businesses.length === 0 && !this.isAnonymousAccount()) {
      return true
    }
    return false
  }

  private isAnonymousAccount (): boolean {
    return this.currentOrganization &&
            this.currentOrganization.accessType === Account.ANONYMOUS
  }

  @Emit()
  private confirmRemoveMember (member: Member) { }

  @Emit()
  private confirmChangeRole (member: Member, targetRole: string): ChangeRolePayload {
    return {
      member,
      targetRole
    }
  }

  private confirmLeaveTeam (member: Member) {
    if (member.membershipTypeCode === MembershipType.Admin &&
      this.ownerCount() === 1 &&
      !this.canDissolve()) {
      this.$emit('single-owner-error')
    } else {
      if (this.canDissolve()) {
        this.$emit('confirm-dissolve-team')
      } else {
        this.$emit('confirm-leave-team')
      }
    }
  }

  private isOwnMembership (member: Member) {
    return this.currentMembership?.user?.username === member.user.username || false
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.v-list--dense {
  .v-list-item {
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }

  .v-list-item .v-list-item__title {
    margin-bottom: 0.25rem;
    font-weight: 700;
  }
}

.role-list {
  width: 20rem;
}
</style>
