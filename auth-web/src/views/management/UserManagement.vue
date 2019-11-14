<template>
  <v-container class="view-container">
    <header class="view-header mt-1 mb-5">
      <h1>Manage Team</h1>
      <div class="view-header__actions">
        <v-btn outlined color="primary" @click="showInviteUsersModal()">
          <v-icon>add</v-icon>
          <span>Invite People</span>
        </v-btn>
      </div>
    </header>

    <v-card>
      <!-- Tab Navigation -->
      <v-tabs class="mb-0" v-model="tab">
        <v-tab>Active</v-tab>
        <v-tab>Pending Approval</v-tab>
        <v-tab>Invitations</v-tab>
      </v-tabs>

      <!-- Tab Contents -->
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <MemberDataTable
            @confirm-remove-member="showConfirmRemoveModal($event)"
            @confirm-change-role="showConfirmChangeRoleModal($event)"
          />
        </v-tab-item>
        <v-tab-item>
          <PendingMemberDataTable
            @confirm-approve-member="showConfirmApproveModal($event)"
            @confirm-deny-member="showConfirmDenyModal($event)"
          />
        </v-tab-item>
        <v-tab-item>
          <InvitationsDataTable
            @confirm-remove-invite="showConfirmRemoveInviteModal($event)"
            @resend="resend($event)"
          />
        </v-tab-item>
      </v-tabs-items>
    </v-card>

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

    <!-- Confirm Delete Dialog -->
    <ModalDialog
      ref="confirmRemoveDialog"
      :title="$t('confirmRemoveMemberTitle')"
      :text="confirmRemoveMemberText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">error</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="removeMember()">Remove</v-btn>
        <v-btn large color="default" @click="cancel()">Cancel</v-btn>
      </template>
    </ModalDialog>

    <!-- Confirm Role Change Dialog -->
    <ModalDialog
      ref="confirmRoleChangeDialog"
      :title="$t('confirmRoleChangeTitle')"
      :text="confirmRoleChangeText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">error</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="changeRole()">Confirm</v-btn>
        <v-btn large color="default" @click="cancel()">Cancel</v-btn>
      </template>
    </ModalDialog>

    <!-- Confirm Remove Invite Dialog -->
    <ModalDialog
      ref="confirmRemoveInviteDialog"
      :title="$t('confirmRemoveInviteTitle')"
      :text="confirmRemoveInviteText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">error</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="removeInvite()">Remove</v-btn>
        <v-btn large color="default" @click="cancel()">Cancel</v-btn>
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
  </v-container>
</template>

<script lang="ts">
import { ActiveUserRecord, Member, Organization, PendingUserRecord, UpdateMemberPayload } from '@/models/Organization'
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
import UserModule from '@/store/modules/user'
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
      'sentInvitations'
    ]),
    ...mapState('business', ['currentBusiness'])
  },
  methods: {
    ...mapActions('org', [
      'resendInvitation',
      'deleteInvitation',
      'deleteMember',
      'updateMemberRole'
    ])
  }
})
export default class UserManagement extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private successTitle = ''
  private successText = ''
  private tab = null
  private isLoading = true
  private memberToBeRemoved: Member
  private invitationToBeRemoved: Invitation
  private roleChangeToAction: ChangeRolePayload
  private confirmRemoveMemberText = ''
  private confirmRoleChangeText = ''
  private confirmRemoveInviteText = ''

  private readonly currentBusiness!: Business
  private readonly resending!: boolean
  private readonly sentInvitations!: Invitation[]
  private readonly resendInvitation!: (invitation: Invitation) => void
  private readonly deleteInvitation!: (invitationId: number) => void
  private readonly deleteMember!: (memberId: number) => void
  private readonly updateMemberRole!: (updateMemberPayload: UpdateMemberPayload) => void

  $refs: {
    successDialog: ModalDialog
    inviteUsersDialog: ModalDialog
    confirmRemoveDialog: ModalDialog
    confirmRoleChangeDialog: ModalDialog
    confirmRemoveInviteDialog: ModalDialog
  }

  private async mounted () {
    this.isLoading = false
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
    this.successText = 'Your team invitations have been sent successfully.'
    this.$refs.successDialog.open()
  }

  private async resend (invitation: Invitation) {
    await this.resendInvitation(invitation)
    this.showSuccessModal()
  }

  private showConfirmRemoveModal (member: Member) {
    this.confirmRemoveMemberText = `Are you sure you want to remove ${member.user.firstname} from the team?`
    this.memberToBeRemoved = member
    this.$refs.confirmRemoveDialog.open()
  }

  private showConfirmChangeRoleModal (payload: ChangeRolePayload) {
    if (payload.member.membershipTypeCode.toUpperCase() === payload.targetRole.toUpperCase()) {
      return
    }
    this.confirmRoleChangeText = `Are you sure you wish to change ${payload.member.user.firstname}'s role to ${payload.targetRole}?`
    this.roleChangeToAction = payload
    this.$refs.confirmRoleChangeDialog.open()
  }

  private showConfirmRemoveInviteModal (invitation: Invitation) {
    this.confirmRemoveInviteText = `Are you sure wish to remove the invite to ${invitation.recipientEmail}?`
    this.invitationToBeRemoved = invitation
    this.$refs.confirmRemoveInviteDialog.open()
  }

  private cancel () {
    this.$refs.confirmRemoveDialog.close()
    this.$refs.confirmRoleChangeDialog.close()
    this.$refs.confirmRemoveInviteDialog.close()
  }

  private async removeMember () {
    await this.deleteMember(this.memberToBeRemoved.id)
    this.$refs.confirmRemoveDialog.close()
  }

  private async changeRole () {
    await this.updateMemberRole({
      memberId: this.roleChangeToAction.member.id,
      role: this.roleChangeToAction.targetRole.toUpperCase()
    })
    this.$refs.confirmRoleChangeDialog.close()
  }

  private async removeInvite () {
    await this.deleteInvitation(this.invitationToBeRemoved.id)
    this.$refs.confirmRemoveInviteDialog.close()
  }
}
</script>

<style lang="scss" scoped>
.view-container {
  display: flex;
  flex-direction: column;
}

.view-container__content {
  flex: 1 1 auto;
}

::v-deep .v-data-table td {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

::v-deep .v-data-table.user-list__active td {
  height: 4rem;
  vertical-align: top;
}

.user-name {
  display: block;
  font-weight: 700;
}
</style>
