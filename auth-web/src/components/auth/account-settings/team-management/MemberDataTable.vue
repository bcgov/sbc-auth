<template>
  <div>
    <v-data-table
      v-if="roleInfos"
      :headers="headerMembers"
      :items="indexedOrgMembers"
      :items-per-page="5"
      :hide-default-footer="indexedOrgMembers.length <= 5"
      :custom-sort="customSortActive"
      class="member-data-table"
      :no-data-text="$t('noActiveUsersLabel')"
    >
      <template #loading>
        Loading...
      </template>

      <!-- Name Column Template -->
      <template #[`item.name`]="{ item }">
        <div
          class="user-name font-weight-bold"
          :data-test="getIndexedTag('user-name', item.index)"
        >
          {{ item.user.firstname }} {{ item.user.lastname }}
        </div>
        <div
          v-if="item.user.contacts && item.user.contacts.length > 0"
          :data-test="getIndexedTag('business-id', item.index)"
          class="contact-email"
        >
          {{ item.user.contacts[0].email }}
        </div>
      </template>

      <!-- Authentication Column Template .Show it only for BCSC/BCEID -->
      <template
        v-if="isRegularAccount()"
        #[`item.authentication`]="{ item }"
      >
        <div :data-test="getIndexedTag('last-active', item.index)">
          <div v-if="item.user.loginSource ===loginSourceEnum.BCEID ">
            {{ item.user.username }}
          </div>
          <div v-if="item.user.loginSource ===loginSourceEnum.BCSC ">
            BCServicesCard
          </div>
          <div v-else />
        </div>
      </template>

      <!-- Role Column Template -->
      <template #[`item.role`]="{ item }">
        <v-menu
          transition="slide-y-transition"
        >
          <template #activator="{ on }">
            <v-btn
              text
              class="ml-n4 pr-2"
              aria-label="Select User Role"
              :disabled="!canChangeRole(item)"
              :data-test="getIndexedTag('role-selector', item.index)"
              v-on="on"
            >
              {{ item.roleDisplayName }}
              <v-icon depressed>
                mdi-menu-down
              </v-icon>
            </v-btn>
          </template>
          <v-list
            dense
            class="role-list"
            role="user role list"
          >
            <v-item-group>
              <v-list-item
                v-for="(role, index) in roleInfos"
                :key="index"
                class="py-1"
                :disabled="!isRoleEnabled(role, item)"
                :class="{
                  'primary--text v-item--active v-list-item--active':
                    item.membershipTypeCode.toUpperCase() ===
                    role.name.toUpperCase()
                }"
                @click="
                  item.membershipTypeCode.toUpperCase() !==
                    role.name.toUpperCase()
                    ? confirmChangeRole(item, role.name)
                    : ''
                "
              >
                <v-list-item-icon>
                  <v-icon v-text="role.icon" />
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title
                    class="user-role-name"
                    v-text="role.displayName"
                  />
                  <v-list-item-subtitle
                    class="user-role-desc"
                    v-text="role.label"
                  />
                  <v-divider />
                </v-list-item-content>
              </v-list-item>
            </v-item-group>
          </v-list>
        </v-menu>
      </template>

      <!-- Date Column Template -->
      <template
        #[`item.lastActive`]="{ item }"
      >
        <div :data-test="getIndexedTag('last-active', item.index)">
          {{ formatDate(item.user.modified, 'MMMM DD, YYYY') }}
        </div>
      </template>

      <!-- Actions Column Template -->
      <template #[`item.action`]="{ item }">
        <!-- Reset Authenticator -->
        <v-btn
          v-show="canResetAuthenticator(item)"
          v-can:RESET_OTP.hide
          icon
          class="mr-1"
          aria-label="Reset Authenticator"
          title="Reset Authenticator"
          @click="showResetAuthenticatorDialog(item)"
        >
          <v-icon>mdi-lock-reset</v-icon>
        </v-btn>

        <!-- Reset Password -->
        <v-btn
          v-show="anonAccount"
          v-can:RESET_PASSWORD.hide
          icon
          class="mr-1"
          aria-label="Reset User Password"
          title="Reset User Password"
          :data-test="getIndexedTag('reset-password-button', item.index)"
          @click="resetPassword(item)"
        >
          <v-icon>mdi-lock-reset</v-icon>
        </v-btn>

        <!-- Remove User -->
        <v-btn
          v-show="canRemove(item)"
          icon
          aria-label="Remove Team Member"
          title="Remove Team Member"
          :data-test="getIndexedTag('remove-user-button', item.index)"
          @click="confirmRemoveMember(item)"
        >
          <v-icon>mdi-trash-can-outline</v-icon>
        </v-btn>

        <!-- Leave Account -->
        <v-btn
          v-show="canLeave(item)"
          icon
          aria-label="Leave Account"
          title="Leave Account"
          :data-test="getIndexedTag('leave-team-button', item.index)"
          @click="confirmLeaveTeam(item)"
        >
          <v-icon>mdi-trash-can-outline</v-icon>
        </v-btn>
      </template>
    </v-data-table>

    <v-snackbar
      v-model="showResetSnackBar"
      bottom
      color="primary"
      class="mb-6"
      :timeout="SNACKBAR_TIMEOUT"
    >
      Authenticator reset for {{ selectedUsername() }}
      <v-btn
        icon
        dark
        aria-label="Close Notification"
        title="Close Notification"
        @click="showResetSnackBar = false"
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-snackbar>

    <ModalDialog
      ref="resetAuthenticatorDialog"
      icon="mdi-check"
      title="Reset Authenticator"
      text="Resetting this team members authenticator will require them to log in and enter a new one-time password in their authenticator app."
      dialog-class="notify-dialog"
      max-width="600"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="error"
          class="font-weight-bold"
          @click="resetAuthenticator()"
        >
          Reset
        </v-btn>
        <v-btn
          large
          depressed
          @click="closeResetAuthDialog()"
        >
          Cancel
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { AccessType, LoginSource, Permission } from '@/util/constants'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization, RoleInfo } from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import { Business } from '@/models/business'
import CommonUtils from '@/util/common-util'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { useBusinessStore } from '@/stores/business'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export interface ChangeRolePayload {
  member: Member
  targetRole: string
}

@Component({
  components: {
    ModalDialog
  },
  computed: {
    ...mapState(useBusinessStore, ['businesses']),
    ...mapState(useOrgStore, [
      'activeOrgMembers',
      'currentMembership',
      'currentOrganization',
      'permissions'
    ]),
    ...mapState(useUserStore, [
      'roleInfos'
    ])
  },
  methods: {
    ...mapActions(useUserStore, [
      'getRoleInfo',
      'resetOTPAuthenticator'
    ])
  }
})
export default class MemberDataTable extends Vue {
  @Prop({ default: '' }) private userNamefilterText: string
  private readonly businesses!: Business[]
  private activeOrgMembers!: Member[]
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly getRoleInfo!: () => Promise<RoleInfo[]>
  private readonly resetOTPAuthenticator!: (username: string) => any
  private readonly roleInfos!: RoleInfo[]
  private readonly SNACKBAR_TIMEOUT: number = 3000 // milliseconds
  private confirmResetAuthDialog = false
  private showResetSnackBar = false
  private selectedUserForReset = undefined
  private readonly loginSource:LoginSource
  private readonly permissions!: string[]

  private formatDate = CommonUtils.formatDisplayDate

  $refs: {
    resetAuthenticatorDialog: InstanceType<typeof ModalDialog>
  }

  private get loginSourceEnum ():typeof LoginSource {
    return LoginSource
  }

  private headerMembers = [
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
      align: 'right',
      value: 'action',
      sortable: false,
      width: '120'
    }
  ]

  private readonly authHeaderMember = {
    text: 'Authentication',
    align: 'left',
    sortable: false,
    value: 'authentication'
  }

  private async mounted () {
    // need not to reload everytime .roles seldom changes
    if (!this.roleInfos) {
      await this.getRoleInfo()
    }
    if (this.isRegularAccount() && this.canViewLoginSource()) {
      this.headerMembers.splice(1, 0, this.authHeaderMember)
    }
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private get indexedOrgMembers () {
    let orgMembers = []
    if (this.userNamefilterText) {
      // filter if the filter by username prop is available
      orgMembers = this.activeOrgMembers.filter((element) => {
        const username = `${element.user?.firstname || ''} ${element.user?.lastname || ''}`.trim()
        const found = username.match(new RegExp(this.userNamefilterText, 'i'))
        if (found?.length) {
          return element
        }
      })
      this.filteredMembersCount(orgMembers.length)
    } else {
      orgMembers = this.activeOrgMembers
    }
    // map org members list with custom index and role mapping
    return orgMembers.map((item, index) => {
      item.roleDisplayName = this.roleInfos.find(
        role => role.name === item.membershipTypeCode
      ).displayName
      return {
        index,
        ...item
      }
    })
  }

  @Emit()
  private filteredMembersCount (count: number) {
    return count
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
          !this.isOwnMembership(memberBeingChanged)
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

    // Coordinators can remove other coordinators.
    if (
      this.currentMembership.membershipTypeCode === MembershipType.Coordinator &&
      memberToRemove.membershipTypeCode === MembershipType.Coordinator
    ) {
      return true
    }

    // Admin can be removed by other admin. #4909
    if (memberToRemove.membershipTypeCode === MembershipType.Admin) {
      if (this.currentMembership.membershipTypeCode === MembershipType.Admin) {
        return true
      } else {
        return false
      }
    }

    return true
  }

  private canLeave (member: Member): boolean {
    if (this.currentMembership.user?.username !== member.user.username) {
      return false
    }
    return true
  }

  private canResetAuthenticator (member: Member): boolean {
    return (member.user.loginSource === LoginSource.BCEID)
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

  private isAnonymousAccount (): boolean {
    return (
      this.currentOrganization &&
      this.currentOrganization.accessType === AccessType.ANONYMOUS
    )
  }

  private isRegularAccount (): boolean {
    return (
      this.currentOrganization &&
      [AccessType.ANONYMOUS.valueOf(), AccessType.GOVM.valueOf()].indexOf(this.currentOrganization.accessType) < 0
    )
  }

  private canViewLoginSource () :boolean {
    return [Permission.VIEW_USER_LOGINSOURCE].some(per => this.permissions?.includes(per))
  }

  @Emit()
  private confirmRemoveMember () {}

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
      this.ownerCount() === 1
    ) {
      this.$emit('single-owner-error')
    } else {
      this.$emit('confirm-leave-team')
    }
  }

  private isOwnMembership (member: Member) {
    return (
      this.currentMembership?.user?.username === member.user.username || false
    )
  }

  private selectedUsername () {
    return `${this.selectedUserForReset?.user?.firstname} ${this.selectedUserForReset?.user?.lastname}`
  }

  private showResetAuthenticatorDialog (item) {
    this.selectedUserForReset = item
    this.$refs.resetAuthenticatorDialog.open()
  }

  private async resetAuthenticator () {
    try {
      await this.resetOTPAuthenticator(this.selectedUserForReset?.user?.username)
      this.showResetSnackBar = true
      this.$refs.resetAuthenticatorDialog.close()
      // wait for the SNACKBAR_TIMEOUT value before unsetting the selectedUserForReset,
      // for rendering the name correctly in the snackbar
      setTimeout(() => {
        this.selectedUserForReset = undefined
      }, this.SNACKBAR_TIMEOUT)
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error(error)
    }
  }

  private closeResetAuthDialog () {
    this.$refs.resetAuthenticatorDialog.close()
    this.selectedUserForReset = undefined
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
