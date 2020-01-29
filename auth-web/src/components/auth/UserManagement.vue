<template>
  <v-container>
    <header class="view-header align-center">
      <h2 class="view-header__title">Team Members</h2>
      <div class="view-header__actions">
        <v-btn color="primary" v-if="canInvite()" @click="showInviteUsersModal()" data-test="invite-people-button">
          <v-icon small>mdi-plus</v-icon>
          <span>Invite People</span>
        </v-btn>
      </div>
    </header>

    <!-- Tab Navigation -->
    <v-tabs class="mb-9" height="40" v-model="tab" background-color="transparent">
      <v-tab data-test="active-tab">Active</v-tab>
      <v-tab data-test="pending-approval-tab" v-show="canInvite()">
        <v-badge inline color="error"
          :content="pendingApprovalCount"
          :value="pendingApprovalCount">
          Pending Approval
        </v-badge>
      </v-tab>
      <v-tab data-test="invitations-tab" v-show="canInvite()">Invitations</v-tab>
    </v-tabs>

    <!-- Tab Contents -->
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <MemberDataTable
          @confirm-remove-member="showConfirmRemoveModal($event)"
          @confirm-change-role="showConfirmChangeRoleModal($event)"
          @confirm-leave-team="showConfirmLeaveTeamModal()"
          @single-owner-error="showSingleOwnerErrorModal()"
        />
      </v-tab-item>
      <v-tab-item>
        <PendingMemberDataTable
          @confirm-approve-member="showConfirmApproveModal($event)"
          @confirm-deny-member="showConfirmRemoveModal($event)"
        />
      </v-tab-item>
      <v-tab-item>
        <InvitationsDataTable
          @confirm-remove-invite="showConfirmRemoveInviteModal($event)"
          @resend="resend($event)"
        />
      </v-tab-item>
    </v-tabs-items>

    <!-- Invite Users Dialog -->
    <ModalDialog
      ref="inviteUsersDialog"
      :show-icon="false"
      :show-actions="false"
      :fullscreen-on-mobile="$vuetify.breakpoint.xsOnly || $vuetify.breakpoint.smOnly || $vuetify.breakpoint.mdOnly"
      :is-persistent="true"
      :is-scrollable="true"
      max-width="640"
    >
      <template v-slot:title>
        <span>Invite Team Members</span>
      </template>
      <template v-slot:text>
        <InviteUsersForm @invites-complete="showSuccessModal()" @cancel="cancelInviteUsersModal()" />
      </template>
    </ModalDialog>

    <!-- Confirm Action Dialog -->
    <ModalDialog
      ref="confirmActionDialog"
      :title="confirmActionTitle"
      :text="confirmActionText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="confirmHandler()">{{ primaryActionText }}</v-btn>
        <v-btn large color="default" @click="cancel()">{{ secondaryActionText }}</v-btn>
      </template>
    </ModalDialog>

    <!-- Confirm Action Dialog With Email Question-->
    <ModalDialog
      ref="confirmActionDialogWithQuestion"
      :title="confirmActionTitle"
      :text="confirmActionText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="primary">mdi-information-outline</v-icon>
      </template>
      <template v-slot:text>
        {{ confirmActionText }}
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="confirmHandler()">{{ primaryActionText }}</v-btn>
        <v-btn large color="default" @click="cancelEmailModal()">{{ secondaryActionText }}</v-btn>
      </template>
    </ModalDialog>

    <!-- Alert Dialog (Success) -->
    <ModalDialog
      ref="successDialog"
      :title="successTitle"
      :text="successText"
      dialog-class="notify-dialog"
      max-width="640"
    ></ModalDialog>

    <!-- Alert Dialog (Error) -->
    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="error" @click="close()">OK</v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import { ActiveUserRecord, Member, MembershipStatus, MembershipType, Organization, PendingUserRecord, UpdateMemberPayload } from '@/models/Organization'
import { Component, Vue } from 'vue-property-decorator'
import MemberDataTable, { ChangeRolePayload } from '@/components/auth/MemberDataTable.vue'
import { mapActions, mapGetters, mapState } from 'vuex'
import { Business } from '@/models/business'
import { Invitation } from '@/models/Invitation'
import InvitationsDataTable from '@/components/auth/InvitationsDataTable.vue'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import PendingMemberDataTable from '@/components/auth/PendingMemberDataTable.vue'
import _ from 'lodash'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    MemberDataTable,
    InvitationsDataTable,
    PendingMemberDataTable,
    InviteUsersForm,
    ModalDialog
  },
  computed: {
    ...mapState('org', [
      'resending',
      'sentInvitations',
      'pendingOrgMembers'
    ]),
    ...mapState('business', ['currentBusiness']),
    ...mapGetters('org', ['myOrgMembership'])
  },
  methods: {
    ...mapActions('org', [
      'resendInvitation',
      'deleteInvitation',
      'updateMember',
      'approveMember',
      'leaveTeam',
      'syncOrganizations',
      'syncActiveOrgMembers',
      'syncPendingOrgInvitations',
      'syncPendingOrgMembers'

    ])
  }
})
export default class UserManagement extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private successTitle: string = ''
  private successText: string = ''
  private errorTitle: string = ''
  private errorText: string = ''
  private tab = null
  private isLoading = true
  private memberToBeRemoved: Member
  private memberToBeApproved: Member
  private invitationToBeRemoved: Invitation
  private roleChangeToAction: ChangeRolePayload
  private confirmActionTitle: string = ''
  private confirmActionText: string = ''
  private primaryActionText: string = ''
  private secondaryActionText = 'No'

  private confirmHandler: () => void = undefined

  private readonly currentBusiness!: Business
  private readonly resending!: boolean
  private readonly sentInvitations!: Invitation[]
  private readonly myOrgMembership!: Member
  private readonly resendInvitation!: (invitation: Invitation) => void
  private readonly deleteInvitation!: (invitationId: number) => void
  private readonly updateMember!: (updateMemberPayload: UpdateMemberPayload) => void
  private readonly approveMember!: (memberId: number) => void
  private readonly leaveTeam!: (memberId: number) => void
  private readonly syncOrganizations!: () => Promise<Organization[]>
  private readonly syncPendingOrgMembers!: () => Member[]
  private readonly syncPendingOrgInvitations!: () => Invitation[]
  private readonly syncActiveOrgMembers!: () => Member[]

  private notifyUser = true

  // PROTOTYPE TAB ICON (PENDING APPROVAL)
  private readonly pendingOrgMembers!: Member[]

  $refs: {
    successDialog: ModalDialog
    errorDialog: ModalDialog
    inviteUsersDialog: ModalDialog
    confirmActionDialog: ModalDialog
    confirmActionDialogWithQuestion: ModalDialog
  }

  private get pendingApprovalCount () {
    return this.pendingOrgMembers.length
  }

  private async mounted () {
    this.isLoading = false
    await this.syncActiveOrgMembers()
    await this.syncPendingOrgInvitations()
    await this.syncPendingOrgMembers()
  }

  private canInvite (): boolean {
    return this.myOrgMembership &&
            this.myOrgMembership.membershipStatus === MembershipStatus.Active &&
            (this.myOrgMembership.membershipTypeCode === MembershipType.Owner ||
             this.myOrgMembership.membershipTypeCode === MembershipType.Admin)
  }

  private showInviteUsersModal () {
    this.$refs.inviteUsersDialog.open()
  }

  private cancelInviteUsersModal () {
    this.$refs.inviteUsersDialog.close()
  }

  private showSuccessModal () {
    this.$refs.inviteUsersDialog.close()
    this.successTitle = `Invited ${this.sentInvitations.length} Team Members`
    this.successText = 'When team members accept this invitation, you will need to approve their access to this account.'
    this.$refs.successDialog.open()
  }

  private async resend (invitation: Invitation) {
    await this.resendInvitation(invitation)
    this.showSuccessModal()
  }

  private showConfirmRemoveModal (member: Member) {
    if (member.membershipStatus === MembershipStatus.Pending) {
      this.confirmActionTitle = this.$t('confirmDenyMemberTitle').toString()
      this.confirmActionText = `Are you sure you want to deny membership to ${member.user.firstname}?`
      this.confirmHandler = this.deny
      this.primaryActionText = 'Deny'
    } else {
      this.confirmActionTitle = this.$t('confirmRemoveMemberTitle').toString()
      this.confirmActionText = `Are you sure you want to remove ${member.user.firstname} from the team?`
      this.confirmHandler = this.removeMember
      this.primaryActionText = 'Remove'
    }
    this.memberToBeRemoved = member
    this.$refs.confirmActionDialog.open()
  }

  private showConfirmChangeRoleModal (payload: ChangeRolePayload) {
    if (payload.member.membershipTypeCode.toString() === payload.targetRole.toString()) {
      return
    }
    this.confirmActionTitle = this.$t('confirmRoleChangeTitle').toString()
    this.confirmActionText = `Are you sure you wish to change ${payload.member.user.firstname}'s role to ${payload.targetRole}?`
    this.roleChangeToAction = payload
    this.confirmHandler = this.changeRole
    this.primaryActionText = 'Yes'
    this.$refs.confirmActionDialogWithQuestion.open()
  }

  private showConfirmLeaveTeamModal () {
    this.confirmActionTitle = this.$t('confirmLeaveTeamTitle').toString()
    this.confirmActionText = this.$t('confirmLeaveTeamText').toString()
    this.confirmHandler = this.leave
    this.primaryActionText = 'Leave'
    this.$refs.confirmActionDialog.open()
  }

  private showSingleOwnerErrorModal () {
    this.errorTitle = this.$t('singleOwnerErrorTitle').toString()
    this.errorText = this.$t('singleOwnerErrorText').toString()
    this.$refs.errorDialog.open()
  }

  private showConfirmRemoveInviteModal (invitation: Invitation) {
    this.confirmActionTitle = this.$t('confirmRemoveInviteTitle').toString()
    this.confirmActionText = `Are you sure wish to remove the invite to ${invitation.recipientEmail}?`
    this.invitationToBeRemoved = invitation
    this.confirmHandler = this.removeInvite
    this.primaryActionText = 'Remove'
    this.$refs.confirmActionDialog.open()
  }

  private showConfirmApproveModal (member: Member) {
    this.confirmActionTitle = this.$t('confirmApproveMemberTitle').toString()
    this.confirmActionText = `Are you sure you wish to approve membership for ${member.user.firstname}?`
    this.memberToBeApproved = member
    this.confirmHandler = this.approve
    this.primaryActionText = 'Approve'
    this.$refs.confirmActionDialog.open()
  }

  private cancel () {
    this.$refs.confirmActionDialog.close()
  }

  private cancelEmailModal () {
    this.$refs.confirmActionDialogWithQuestion.close()
  }

  private async removeMember () {
    await this.updateMember({
      memberId: this.memberToBeRemoved.id,
      status: MembershipStatus.Inactive
    })
    this.$refs.confirmActionDialog.close()
  }

  private async changeRole () {
    await this.updateMember({
      memberId: this.roleChangeToAction.member.id,
      role: this.roleChangeToAction.targetRole.toString().toUpperCase(),
      notifyUser: this.notifyUser
    })
    this.$refs.confirmActionDialogWithQuestion.close()
    await this.syncOrganizations()
  }

  private async removeInvite () {
    await this.deleteInvitation(this.invitationToBeRemoved.id)
    this.$refs.confirmActionDialog.close()
  }

  private async approve () {
    await this.updateMember({
      memberId: this.memberToBeApproved.id,
      status: MembershipStatus.Active
    })
    this.$store.commit('updateHeader')
    this.$refs.confirmActionDialog.close()
  }

  private async deny () {
    await this.updateMember({
      memberId: this.memberToBeRemoved.id,
      status: MembershipStatus.Rejected
    })
    this.$store.commit('updateHeader')
    this.$refs.confirmActionDialog.close()
  }

  private async leave () {
    await this.leaveTeam(this.myOrgMembership.id)
    this.$refs.confirmActionDialog.close()
    this.$router.push('/leaveteam')
  }

  private close () {
    this.$refs.errorDialog.close()
  }
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }

  ::v-deep {
    .v-data-table td {
      padding-top: 1rem;
      padding-bottom: 1rem;
      height: auto;
      vertical-align: top;
    }

    .v-list-item__title {
      display: block;
      font-weight: 700;
    }

    .v-badge--inline .v-badge__wrapper {
      margin-left: 0;

      .v-badge__badge {
        margin-right: -0.25rem;
        margin-left: 0.25rem;
      }
    }
  }

  .notify-checkbox {
    justify-content: center;

    ::v-deep {
      .v-input__slot {
        margin-bottom: 0 !important;
      }
    }
  }
</style>
