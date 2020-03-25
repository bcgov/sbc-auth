// You can declare a mixin as the same style as components.
<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Member, MembershipStatus, MembershipType, Organization, PendingUserRecord, UpdateMemberPayload } from '@/models/Organization'
import MemberDataTable, { ChangeRolePayload } from '@/components/auth/MemberDataTable.vue'
import { mapActions, mapState } from 'vuex'
import { Business } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import { Invitation } from '@/models/Invitation'
import InvitationsDataTable from '@/components/auth/InvitationsDataTable.vue'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import PendingMemberDataTable from '@/components/auth/PendingMemberDataTable.vue'
import { SessionStorageKeys } from '@/util/constants'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    ModalDialog
  },
  computed: {
    ...mapState('org', [
      'currentMembership'
    ])
  },
  methods: {
    ...mapActions('org', [
      'updateMember',
      'leaveTeam',
      'dissolveTeam'
    ])
  }
})
export default class TeamManagementMixin extends Vue {
  protected successTitle: string = ''
  protected successText: string = ''
  protected errorTitle: string = ''
  protected errorText: string = ''
  private memberToBeRemoved: Member
  protected roleChangeToAction: ChangeRolePayload
  protected confirmActionTitle: string = ''
  protected confirmActionText: string = ''
  protected primaryActionText: string = ''
  protected secondaryActionText = 'No'

  protected confirmHandler: (modal:ModalDialog) => void = undefined

  protected readonly currentMembership!: Member
  protected readonly updateMember!: (updateMemberPayload: UpdateMemberPayload) => void
  protected readonly leaveTeam!: (memberId: number) => void
  protected readonly dissolveTeam!: () => void

  private notifyUser = true
  private modal: ModalDialog

  protected showConfirmRemoveModal (member: Member, confirmActionDialog: ModalDialog) {
    this.modal = confirmActionDialog
    if (member.membershipStatus === MembershipStatus.Pending) {
      this.confirmActionTitle = this.$t('confirmDenyMemberTitle').toString()
      this.confirmActionText = `Are you sure you want to deny membership to ${member.user.firstname}?`
      this.confirmHandler = this.deny
      this.primaryActionText = 'Deny'
    } else {
      this.confirmActionTitle = this.$t('confirmRemoveMemberTitle').toString()
      this.confirmActionText = `Are you sure you want to remove ${member.user.firstname} from the account?`
      this.confirmHandler = this.removeMember
      this.primaryActionText = 'Yes'
    }
    this.memberToBeRemoved = member
    confirmActionDialog.open()
  }

  protected showConfirmChangeRoleModal (payload: ChangeRolePayload, confirmActionDialogWithQuestion: ModalDialog) {
    if (payload.member.membershipTypeCode.toString() === payload.targetRole.toString()) {
      return
    }
    this.modal = confirmActionDialogWithQuestion
    this.confirmActionTitle = this.$t('confirmRoleChangeTitle').toString()
    this.confirmActionText = `Are you sure you wish to change ${payload.member.user.firstname}'s role to ${payload.targetRole}?`
    this.roleChangeToAction = payload
    this.confirmHandler = this.changeRole
    this.primaryActionText = 'Yes'
    confirmActionDialogWithQuestion.open()
  }

  protected showConfirmLeaveTeamModal (confirmActionDialog: ModalDialog) {
    this.modal = confirmActionDialog
    this.confirmActionTitle = this.$t('confirmLeaveTeamTitle').toString()
    this.confirmActionText = this.$t('confirmLeaveTeamText').toString()
    this.confirmHandler = this.leave
    this.primaryActionText = 'Leave'
    confirmActionDialog.open()
  }

  protected showConfirmDissolveModal (confirmActionDialog: ModalDialog) {
    this.modal = confirmActionDialog
    this.confirmActionTitle = this.$t('confirmDissolveTeamTitle').toString()
    this.confirmActionText = this.$t('confirmDissolveTeamText').toString()
    this.confirmHandler = this.dissolve
    this.primaryActionText = 'Dissolve'
    confirmActionDialog.open()
  }

  protected showSingleOwnerErrorModal (errorDialog: ModalDialog) {
    this.modal = errorDialog
    this.errorTitle = this.$t('singleOwnerErrorTitle').toString()
    this.errorText = this.$t('singleOwnerErrorText').toString()
    errorDialog.open()
  }

  protected close (modal: ModalDialog) {
    modal.close()
  }

  protected async removeMember () {
    await this.updateMember({
      memberId: this.memberToBeRemoved.id,
      status: MembershipStatus.Inactive
    })
    this.modal.close()
  }

  protected async changeRole () {
    await this.updateMember({
      memberId: this.roleChangeToAction.member.id,
      role: this.roleChangeToAction.targetRole.toString().toUpperCase(),
      notifyUser: this.notifyUser
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
    await this.leaveTeam(this.currentMembership.id)
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

  protected canInvite (): boolean {
    return this.currentMembership &&
            this.currentMembership.membershipStatus === MembershipStatus.Active &&
            (this.currentMembership.membershipTypeCode === MembershipType.Owner ||
             this.currentMembership.membershipTypeCode === MembershipType.Admin)
  }
}
</script>
