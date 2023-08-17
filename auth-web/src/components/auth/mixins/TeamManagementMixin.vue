// You can declare a mixin as the same style as components.
<script lang="ts">
import { AccessType, LoginSource, SessionStorageKeys } from '@/util/constants'
import { Component, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, Organization, UpdateMemberPayload } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import { ChangeRolePayload } from '@/components/auth/account-settings/team-management/MemberDataTable.vue'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
/* eslint-disable-next-line @typescript-eslint/no-unused-vars */
import OrgModule from '@/store/modules/org'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    ModalDialog
  },
  computed: {
    ...mapState('org', [
      'currentMembership',
      'currentOrganization'
    ]),
    ...mapState('user', [
      'currentUser'
    ])
  },
  methods: {
    ...mapActions('org', [
      'updateMember',
      'leaveTeam',
      'dissolveTeam',
      'deleteUser'
    ])
  }
})
export default class TeamManagementMixin extends Vue {
  private userStore = getModule(UserModule, this.$store)
  protected successTitle: string = ''
  protected successText: string = ''
  protected errorTitle: string = ''
  protected errorText: string = ''
  private memberToBeRemoved: Member
  protected roleChangeToAction: ChangeRolePayload
  protected confirmActionTitle: string = ''
  protected confirmActionText: string = ''
  protected primaryActionText: string = ''
  protected primaryActionType: string = ''
  protected secondaryActionText = 'Cancel'

  protected confirmHandler: (modal: InstanceType<typeof ModalDialog>) => void = undefined

  protected readonly currentMembership!: Member
  protected readonly currentOrganization!: Organization
  protected readonly updateMember!: (updateMemberPayload: UpdateMemberPayload) => void
  protected readonly deleteUser!: (userName: string) => void
  protected readonly leaveTeam!: (memberId: number) => void
  protected readonly dissolveTeam!: () => void
  protected readonly currentUser!: KCUserProfile

  private notifyUser = true
  private modal: InstanceType<typeof ModalDialog>

  protected showConfirmRemoveModal (member: Member, confirmActionDialog: InstanceType<typeof ModalDialog>) {
    this.modal = confirmActionDialog
    if (member.membershipStatus === MembershipStatus.Pending) {
      this.confirmActionTitle = this.$t('confirmDenyMemberTitle').toString()
      this.confirmActionText =
        `Deny account access to <strong>${member?.user?.firstname} ${member?.user?.lastname}</strong>?`
      this.confirmHandler = this.deny
      this.primaryActionText = 'Deny'
      this.primaryActionType = 'error'
    } else {
      this.confirmActionTitle = this.$t('confirmRemoveMemberTitle').toString()
      this.confirmActionText =
        `Remove team member <strong>${member?.user?.firstname} ${member?.user?.lastname}</strong> from this account?`
      this.confirmHandler = this.removeMember
      this.primaryActionText = 'Remove'
      this.primaryActionType = 'error'
    }
    this.memberToBeRemoved = member
    confirmActionDialog.open()
  }

  protected showConfirmChangeRoleModal (payload: ChangeRolePayload, confirmActionDialogWithQuestion: InstanceType<typeof ModalDialog>) {
    if (payload.member.membershipTypeCode.toString() === payload.targetRole.toString()) {
      return
    }
    const username = `${payload.member?.user?.firstname || ''} ${payload.member?.user?.lastname || ''}`.trim()
    this.modal = confirmActionDialogWithQuestion
    this.confirmActionTitle = this.$t('confirmRoleChangeTitle').toString()
    this.confirmActionText = `Change <strong>${username}</strong>'s role to ${payload.targetRole}?`
    this.roleChangeToAction = payload
    this.confirmHandler = this.changeRole
    this.primaryActionText = 'Change'
    this.primaryActionType = 'primary'
    confirmActionDialogWithQuestion.open()
  }

  protected showConfirmLeaveTeamModal (confirmActionDialog: InstanceType<typeof ModalDialog>) {
    this.modal = confirmActionDialog
    this.confirmActionTitle = this.$t('confirmLeaveTeamTitle').toString()
    this.confirmActionText = this.$t('confirmLeaveTeamText').toString()
    this.confirmHandler = this.leave
    this.primaryActionText = 'Leave'
    confirmActionDialog.open()
  }

  protected showConfirmDissolveModal (confirmActionDialog: InstanceType<typeof ModalDialog>) {
    this.modal = confirmActionDialog
    this.confirmActionTitle = this.$t('confirmDissolveTeamTitle').toString()
    this.confirmActionText = this.$t('confirmDissolveTeamText').toString()
    this.confirmHandler = this.dissolve
    this.primaryActionText = 'Dissolve'
    confirmActionDialog.open()
  }

  protected showSingleOwnerErrorModal (errorDialog: InstanceType<typeof ModalDialog>) {
    this.modal = errorDialog
    this.errorTitle = this.$t('singleOwnerErrorTitle').toString()
    this.errorText = this.$t('singleOwnerErrorText').toString()
    errorDialog.open()
  }

  protected get isAccountGovM () : boolean {
    return this.currentOrganization.accessType === AccessType.GOVM
  }

  protected get inviteUserFormText () : string {
    return this.isAccountGovM ? this.$t('inviteUsersFormTextGovM').toString() : this.$t('inviteUsersFormText').toString()
  }

  protected close (modal: InstanceType<typeof ModalDialog>) {
    modal.close()
  }

  protected async removeMember () {
    if (this.isAnonymousUser()) {
      await this.deleteUser(this.memberToBeRemoved.user.username)
    } else {
      await this.updateMember({
        memberId: this.memberToBeRemoved.id,
        status: MembershipStatus.Inactive
      })
    }
    this.modal.close()
  }

  isAnonymousUser (): boolean {
    return this.currentUser?.loginSource === LoginSource.BCROS
  }
  protected async changeRole () {
    await this.updateMember({
      memberId: this.roleChangeToAction.member.id,
      role: this.roleChangeToAction.targetRole.toString().toUpperCase(),
      notifyUser: (this.currentUser?.loginSource !== LoginSource.BCROS) ? this.notifyUser : false
    })
    this.modal.close()
  }

  protected async deny () {
    await this.updateMember({
      memberId: this.memberToBeRemoved.id,
      status: MembershipStatus.Rejected
    })
    this.$store.commit('updateHeader')
    this.modal.close()
  }

  protected async leave () {
    if (this.isAnonymousUser()) {
      await this.deleteUser(this.currentMembership.user.username)
    } else {
      await this.leaveTeam(this.currentMembership.id)
    }
    this.modal.close()
    this.$store.commit('updateHeader')
    this.$router.push('/leaveteam')
  }

  protected async dissolve () {
    await this.dissolveTeam()
    await this.leaveTeam(this.currentMembership.id)
    this.modal.close()
    this.$store.commit('updateHeader')
    const event:Event = { message: 'Dissolved the account', type: 'error', timeout: 1000 }
    EventBus.$emit('show-toast', event)
    // remove this account from the current account session storage.Header will automatically get the next valid account
    ConfigHelper.removeFromSession(SessionStorageKeys.CurrentAccount)
    this.$router.push('/')
  }
}
</script>
