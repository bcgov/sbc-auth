<template>
  <div>
    <header class="view-header align-center mt-n1 mb-7">
      <h2 class="view-header__title">Team Members</h2>
      <v-btn
        large
        color="primary"
        class="ml-auto"
        v-can:INVITE_MEMBERS.hide @click="showInviteUsersModal()"
        data-test="invite-people-button">
        <v-icon small class="ml-n2">mdi-plus</v-icon>
        <span>Invite Team Members</span>
      </v-btn>
    </header>

    <SearchFilterInput class="mb-4"
      :filterParams="searchFilter"
      :filteredRecordsCount="filteredMembersCount"
      @filter-texts="setAppliedFilterValue"
    ></SearchFilterInput>

    <!-- Tab Navigation -->
    <v-tabs class="mb-8" v-model="tab" background-color="transparent">
      <v-tab data-test="active-tab">Active</v-tab>
      <v-tab data-test="pending-approval-tab" v-can:INVITE_MEMBERS.hide>
        <v-badge
          inline
          color="primary"
          :content="pendingApprovalCount"
          :value="pendingApprovalCount">
          Pending Approval
        </v-badge>
      </v-tab>
      <v-tab data-test="invitations-tab" v-can:INVITE_MEMBERS.hide>Invitations</v-tab>
    </v-tabs>

    <!-- Tab Contents -->
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <MemberDataTable
          @confirm-remove-member="showConfirmRemoveModal($event, $refs.confirmActionDialog)"
          @confirm-change-role="showConfirmChangeRoleModal($event, $refs.confirmActionDialogWithQuestion)"
          @confirm-leave-team="showConfirmLeaveTeamModal($refs.confirmActionDialog)"
          @confirm-dissolve-team="showConfirmDissolveModal($refs.confirmActionDialog)"
          @single-owner-error="showSingleOwnerErrorModal($refs.errorDialog)"
          :userNamefilterText="appliedFilterValue"
          @filtered-members-count="filteredTeamMembersCount"
        />
      </v-tab-item>
      <v-tab-item>
        <PendingMemberDataTable
          @confirm-approve-member="showConfirmApproveModal($event)"
          @confirm-deny-member="showConfirmRemoveModal($event, $refs.confirmActionDialog)"
          :userNamefilterText="appliedFilterValue"
          @filtered-members-count="filteredPendingMembersCount"
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
        Invite Team Members
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
      max-width="480"
    >
      <template v-slot:icon>
        <v-icon
          large
          :color="primaryActionType"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template v-slot:actions>
        <v-btn
          large
          :color="primaryActionType"
          class="font-weight-bold"
          @click="confirmHandler()"
        >
          {{ primaryActionText }}
        </v-btn>
        <v-btn
          large
          depressed
          @click="close($refs.confirmActionDialog)"
        >
          {{ secondaryActionText }}
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Confirm Action Dialog With Email Question-->
    <ModalDialog
      ref="confirmActionDialogWithQuestion"
      :title="confirmActionTitle"
      :text="confirmActionText"
      dialog-class="notify-dialog"
      max-width="480"
    >
      <template v-slot:icon>
        <v-icon
          large
          :color="primaryActionType"
        >
          mdi-information-outline
        </v-icon>
      </template>
      <template v-slot:actions>
        <v-btn
          large
          :color="primaryActionType"
          @click="confirmHandler()"
        >
          {{ primaryActionText }}
        </v-btn>
        <v-btn
          large
          depressed
          @click="close($refs.confirmActionDialogWithQuestion)"
        >
          {{ secondaryActionText }}
        </v-btn>
      </template>
    </ModalDialog>

    <!-- Alert Dialog (Success) -->
    <ModalDialog
      ref="successDialog"
      :title="successTitle"
      :text="successText"
      dialog-class="notify-dialog"
      max-width="600"
    ></ModalDialog>

    <!-- Alert Dialog (Error) -->
    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="480"
    >
      <template v-slot:icon>
        <v-icon
          large
          color="primary"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template v-slot:actions>
        <v-btn
          large
          color="primary"
          class="font-weight-bold"
          @click="close($refs.errorDialog)"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { LoginSource, Pages, SearchFilterCodes } from '@/util/constants'
import { Member, MembershipStatus, Organization } from '@/models/Organization'
import { mapActions, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import { Invitation } from '@/models/Invitation'
import InvitationsDataTable from '@/components/auth/account-settings/team-management/InvitationsDataTable.vue'
import InviteUsersForm from '@/components/auth/account-settings/team-management/InviteUsersForm.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import MemberDataTable from '@/components/auth/account-settings/team-management/MemberDataTable.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PendingMemberDataTable from '@/components/auth/account-settings/team-management/PendingMemberDataTable.vue'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import TeamManagementMixin from '@/components/auth/mixins/TeamManagementMixin.vue'

@Component({
  components: {
    MemberDataTable,
    InvitationsDataTable,
    PendingMemberDataTable,
    InviteUsersForm,
    ModalDialog,
    SearchFilterInput
  },
  computed: {
    ...mapState('user', ['currentUser']),
    ...mapState('org', [
      'resending',
      'sentInvitations',
      'pendingOrgMembers',
      'memberLoginOption'
    ]),
    ...mapState('business', ['currentBusiness'])
  },
  methods: {
    ...mapActions('org', [
      'resendInvitation',
      'deleteInvitation',
      'syncPendingOrgInvitations',
      'syncPendingOrgMembers',
      'syncActiveOrgMembers',
      'syncMemberLoginOption'
    ])
  }
})
export default class UserManagement extends Mixins(AccountChangeMixin, TeamManagementMixin, AccountMixin) {
  @Prop({ default: '' }) private orgId: string;

  private tab = null
  private isLoading = true
  private memberToBeApproved: Member
  private invitationToBeRemoved: Invitation

  private readonly sentInvitations!: Invitation[]
  private readonly memberLoginOption!: string
  private readonly syncMemberLoginOption!: (currentAccount: number) => string

  private readonly resendInvitation!: (invitation: Invitation) => void
  private readonly deleteInvitation!: (invitationId: number) => void
  private readonly syncPendingOrgMembers!: () => Member[]
  private readonly syncPendingOrgInvitations!: () => Invitation[]
  private readonly syncActiveOrgMembers!: () => Member[]
  readonly currentUser!: KCUserProfile
  private appliedFilterValue: string = ''
  private teamMembersCount = 0
  private pendingMembersCount = 0
  private searchFilter: SearchFilterParam[] = [
    {
      id: SearchFilterCodes.USERNAME,
      placeholder: 'Team Member',
      labelKey: 'Team Member',
      appliedFilterValue: '',
      filterInput: ''
    }
  ]

  // PROTOTYPE TAB ICON (PENDING APPROVAL)
  private readonly pendingOrgMembers!: Member[]

  $refs: {
    successDialog: InstanceType<typeof ModalDialog>
    errorDialog: InstanceType<typeof ModalDialog>
    inviteUsersDialog: InstanceType<typeof ModalDialog>
    confirmActionDialog: InstanceType<typeof ModalDialog>
    confirmActionDialogWithQuestion: InstanceType<typeof ModalDialog>
  }

  private get pendingApprovalCount () {
    return this.pendingOrgMembers.length
  }

  private async mounted () {
    this.setAccountChangedHandler(this.setup)
    await this.setup()
  }

  private async setup () {
    this.isLoading = true
    await this.syncActiveOrgMembers()
    await this.syncPendingOrgInvitations()
    await this.syncPendingOrgMembers()
    // await this.redirectIfNoAuthMethodSetup()
    this.isLoading = false
  }

  // unused for now..Keeping it there for some time if requirement again changes
  private async redirectIfNoAuthMethodSetup () {
    if (!this.memberLoginOption) {
      await this.syncMemberLoginOption(this.currentOrganization.id)
    }
    if (!this.memberLoginOption) {
      await this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/login-option`)
    }
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
    this.successText = 'Once team members accept the invitation and log in, you will need to approve their access to this account.'
    this.$refs.successDialog.open()
  }

  private async resend (invitation: Invitation) {
    await this.resendInvitation(invitation)
    this.showSuccessModal()
  }
  private get isBCEIDUser (): boolean {
    return this.currentUser?.loginSource === LoginSource.BCEID
  }

  private showConfirmRemoveInviteModal (invitation: Invitation) {
    this.confirmActionTitle = this.$t('confirmRemoveInviteTitle').toString()
    this.confirmActionText = `Remove the invitation to sent to <strong>${invitation.recipientEmail}</strong>?`
    this.invitationToBeRemoved = invitation
    this.confirmHandler = this.removeInvite
    this.primaryActionText = 'Remove'
    this.secondaryActionText = 'Cancel'
    this.primaryActionType = 'error'
    this.$refs.confirmActionDialog.open()
  }

  private showConfirmApproveModal (member: Member) {
    this.confirmActionTitle = this.$t('confirmApproveMemberTitle').toString()
    this.confirmActionText = `Approve account access for <strong>${member?.user?.firstname} ${member?.user?.lastname}</strong>?`
    this.memberToBeApproved = member
    this.confirmHandler = this.approve
    this.primaryActionText = 'Approve'
    this.secondaryActionText = 'Cancel'
    this.primaryActionType = 'primary'
    this.$refs.confirmActionDialog.open()
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

  private setAppliedFilterValue (filter: SearchFilterParam[]) {
    this.appliedFilterValue = filter[0].appliedFilterValue
  }

  private filteredTeamMembersCount (count: number) {
    this.teamMembersCount = count
  }

  private filteredPendingMembersCount (count: number) {
    this.pendingMembersCount = count
  }

  private get filteredMembersCount () {
    // display the filtered record count according to the tab selected
    switch (this.tab) {
      case 0: return this.teamMembersCount
      case 1: return this.pendingMembersCount
      default: return 0
    }
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
    .v-data-table th {
      white-space: nowrap;
    }

    .v-data-table td {
      height: auto;
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
