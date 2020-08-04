<template>
  <v-data-table
    v-if="roleInfos"
    :mobile-breakpoint="1024"
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

    <!-- Name Column Template -->
    <template v-slot:item.name="{ item }">
      <div
        class="user-name font-weight-bold"
        :data-test="getIndexedTag('user-name', item.index)"
        >
          {{ item.user.firstname }} {{ item.user.lastname }}
      </div>
      <div
        :data-test="getIndexedTag('business-id', item.index)"
        v-if="item.user.contacts && item.user.contacts.length > 0"
        >
          {{ item.user.contacts[0].email }}
      </div>
    </template>

    <!-- Role Column Template -->
    <template v-slot:item.role="{ item }">
      <v-menu>
        <template v-slot:activator="{ on }">
          <v-btn
            text
            class="ml-n4 pr-2"
            v-on="on"
            :disabled="!canChangeRole(item)"
            :data-test="getIndexedTag('role-selector', item.index)"
          >
            {{ item.roleDisplayName }}
            <v-icon depressed>mdi-menu-down</v-icon>
          </v-btn>
        </template>
        <v-list dense class="role-list">
          <v-item-group>
            <v-list-item
              class="py-1"
              v-for="(role, index) in roleInfos"
              :key="index"
              @click="
                item.membershipTypeCode.toUpperCase() !==
                role.name.toUpperCase()
                  ? confirmChangeRole(item, role.name)
                  : ''
              "
              :disabled="!isRoleEnabled(role, item)"
              v-bind:class="{
                'primary--text v-item--active v-list-item--active':
                  item.membershipTypeCode.toUpperCase() ===
                  role.name.toUpperCase()
              }"
            >
              <v-list-item-icon>
                <v-icon v-text="role.icon" />
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title
                  class="user-role-name"
                  v-text="role.displayName"
                >
                </v-list-item-title>
                <v-list-item-subtitle
                  class="user-role-desc"
                  v-text="role.label"
                >
                </v-list-item-subtitle>
                <v-divider></v-divider>
              </v-list-item-content>
            </v-list-item>
          </v-item-group>
        </v-list>
      </v-menu>
    </template>

    <!-- Date Column Template -->
    <template
      v-slot:item.lastActive="{ item }"
      :data-test="getIndexedTag('last-active', item.index)"
    >
      {{ formatDate(item.user.modified) }}
    </template>

    <!-- Actions Column Template -->
    <template v-slot:item.action="{ item }">
      <div class="btn-inline">
        <v-btn
          outlined
          color="primary"
          class="mr-1"
          :data-test="getIndexedTag('reset-password-button', item.index)"
          v-can:RESET_PASSWORD.hide
          v-show="anonAccount"
          @click="resetPassword(item)"
        >
          Reset Password
        </v-btn>
        <v-btn
          outlined
          color="primary"
          :data-test="getIndexedTag('remove-user-button', item.index)"
          v-show="canRemove(item)"
          @click="confirmRemoveMember(item)"
        >
          Remove
        </v-btn>
        <v-btn
          outlined
          color="primary"
          :data-test="getIndexedTag('leave-team-button', item.index)"
          v-show="canLeave(item)"
          @click="confirmLeaveTeam(item)"
        >
          <span v-if="!canDissolve()">Leave</span>
          <span v-if="canDissolve()">Dissolve</span>
        </v-btn>
      </div>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { AccessType, Account, LoginSource } from '@/util/constants'
import { Component, Emit, Vue } from 'vue-property-decorator'
import {
  Member,
  MembershipStatus,
  MembershipType,
  Organization,
  RoleInfo
} from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import { Business } from '@/models/business'
import CommonUtils from '@/util/common-util'

export interface ChangeRolePayload {
  member: Member
  targetRole: string
}

@Component({
  computed: {
    ...mapState('business', ['businesses']),
    ...mapState('org', [
      'activeOrgMembers',
      'currentMembership',
      'currentOrganization'
    ]),
    ...mapState('user', ['roleInfos'])
  },
  methods: {
    ...mapActions('user', ['getRoleInfo'])
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
      text: 'Role',
      align: 'left',
      sortable: true,
      value: 'role'
    },
    {
      text: 'Last Activity',
      align: 'left',
      sortable: true,
      value: 'lastActive'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '120'
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
      element.roleDisplayName = self.roleInfos.find(
        role => role.name === element.membershipTypeCode
      ).displayName
    })
    return this.activeOrgMembers.map((item, index) => ({
      index,
      ...item
    }))
  }

  private isRoleEnabled (role: RoleInfo, member: Member): boolean {
    // BCeID delegates cannot be upgraded to admins
    if ((member?.user?.loginSource === LoginSource.BCEID) && (role.name === MembershipType.Admin)) {
      return false
    }
    switch (this.currentMembership.membershipTypeCode) {
      case MembershipType.Admin:
        return true
      case MembershipType.Coordinator:
        // coordinator cant upgrade/change themselves to admin
        if (role.name !== MembershipType.Admin) {
          return true
        }
        return false
      default:
        return false
    }
  }

  get anonAccount (): boolean {
    return this.currentOrganization?.accessType === AccessType.ANONYMOUS
  }

  private canChangeRole (memberBeingChanged: Member): boolean {
    if (this.currentMembership.membershipStatus !== MembershipStatus.Active) {
      return false
    }

    switch (this.currentMembership.membershipTypeCode) {
      case MembershipType.Admin:
        // Owners can change roles of other users who are not owners
        if (
          !this.isOwnMembership(memberBeingChanged) &&
          memberBeingChanged.membershipTypeCode !== MembershipType.Admin
        ) {
          return true
        }
        // And they can downgrade their own role if there is another owner on the team
        if (this.isOwnMembership(memberBeingChanged) && this.ownerCount() > 1) {
          return true
        }
        return false
      case MembershipType.Coordinator:
        // Admins can change roles of their own and users as well
        return (
          this.isOwnMembership(memberBeingChanged) ||
          memberBeingChanged.membershipTypeCode === MembershipType.User
        )
      default:
        return false
    }
  }

  private canRemove (memberToRemove: Member): boolean {
    // Can't remove yourself
    if (this.currentMembership.user?.username === memberToRemove.user.username) {
      return false
    }

    // Can't remove unless Admin/Coordinator
    if (this.currentMembership.membershipTypeCode === MembershipType.User) {
      return false
    }

    // Can't remove Coordinator unless Admin
    if (
      this.currentMembership.membershipTypeCode === MembershipType.Coordinator &&
      memberToRemove.membershipTypeCode === MembershipType.Coordinator
    ) {
      return false
    }

    // No one can change an OWNER's status, only option is OWNER to leave the team. #2319
    if (memberToRemove.membershipTypeCode === MembershipType.Admin) {
      return false
    }

    return true
  }

  private canLeave (member: Member): boolean {
    if (this.currentMembership.user?.username !== member.user.username) {
      return false
    }
    return true
  }

  private ownerCount (): number {
    return this.activeOrgMembers.filter(
      member => member.membershipTypeCode === MembershipType.Admin
    ).length
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
    if (
      this.activeOrgMembers.length === 1 &&
      this.businesses.length === 0 &&
      !this.isAnonymousAccount()
    ) {
      return true
    }
    return false
  }

  private isAnonymousAccount (): boolean {
    return (
      this.currentOrganization &&
      this.currentOrganization.accessType === AccessType.ANONYMOUS
    )
  }

  @Emit()
  private confirmRemoveMember (member: Member) {}

  @Emit()
  private resetPassword (member: Member) {
    return member.user
  }

  @Emit()
  private confirmChangeRole (
    member: Member,
    targetRole: string
  ): ChangeRolePayload {
    return {
      member,
      targetRole
    }
  }

  private confirmLeaveTeam (member: Member) {
    if (
      member.membershipTypeCode === MembershipType.Admin &&
      this.ownerCount() === 1 &&
      !this.canDissolve()
    ) {
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
    return (
      this.currentMembership?.user?.username === member.user.username || false
    )
  }
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
