<template>
  <div class="user-mgmt-view">
    <header class="view-header mt-1 mb-5">
      <h1>Manage Users</h1>
      <div class="view-header__actions">
        <v-btn outlined color="primary" @click="showInviteUsersModal()">
          <v-icon>add</v-icon>
          <span>Invite Users</span>
        </v-btn>
      </div>
    </header>

    <!-- Tab Navigation -->
    <v-tabs v-model="tab" background-color="transparent" class="mb-3">
      <v-tab>Active</v-tab>
      <v-tab>Pending</v-tab>
    </v-tabs>

    <v-card>
      <!-- Tab Contents -->
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <v-data-table
            :headers="headersActive"
            :items="activeUserListing"
            :items-per-page="5"
          >
            <template v-slot:item.action="{ item }">
              <v-btn outlined @click="removeMember(item)">
                Remove
              </v-btn>
            </template>
          </v-data-table>
        </v-tab-item>
        <v-tab-item>
          <v-data-table
            :headers="headersPending"
            :items="pendingUserListing"
            :items-per-page="5"
          >
            <template v-slot:item.action="{ item }">
              <v-btn outlined class="mr-2" @click="resend(item)">
                Resend
              </v-btn>
              <v-btn outlined @click="removeInvite(item)">
                Remove
              </v-btn>
            </template>
          </v-data-table>
        </v-tab-item>
      </v-tabs-items>
    </v-card>

    <!-- Invite Users Modal -->
    <v-dialog content-class="invite-user-dialog" :fullscreen="$vuetify.breakpoint.mdOnly" v-model="isInviteUsersModalVisible" scrollable persistent>
      <InviteUsersForm
        @invites-complete="showSuccessModal()"
        @cancel="cancelModal()"
      >
      </InviteUsersForm>
    </v-dialog>

    <!-- Alert Dialog (Success) -->
    <ModalDialog
      ref="successDialog"
      :title="successTitle"
      :text="successText">
    </ModalDialog>

  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import AlertDialogContent from '@/components/AlertDialogContent.vue'
import { mapState, mapGetters, mapActions } from 'vuex'
import { Organization, Member, PendingUserRecord, ActiveUserRecord } from '@/models/Organization'
import { Invitation } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'
import ModalDialog from '@/components/auth/ModalDialog.vue'

@Component({
  components: {
    InviteUsersForm,
    AlertDialogContent,
    ModalDialog
  },
  computed: {
    ...mapState('org', ['currentOrg', 'resending', 'sentInvitations']),
    ...mapState('user', ['organizations', 'activeBasicMembers', 'pendingBasicMembers']),
    ...mapGetters('user', ['activeUserListing', 'pendingUserListing'])
  },
  methods: {
    ...mapActions('user', ['getOrganizations', 'getActiveBasicMembers', 'getPendingBasicMembers']),
    ...mapActions('org', ['resendInvitation', 'deleteInvitation', 'deleteMember'])
  }
})
export default class UserManagement extends Vue {
  userStore = getModule(UserModule, this.$store)
  orgStore = getModule(OrgModule, this.$store)
  tab = null
  isInviteUsersModalVisible = false
  isInviteSuccessModalVisible = false
  isInviteErrorModalVisible = false

  readonly organizations!: Organization[]
  readonly currentOrg!: Organization
  readonly resending!: boolean
  readonly sentInvitations!: Invitation[]
  readonly activeBasicMembers!: Member[]
  readonly pendingBasicMembers!: Invitation[]
  readonly getOrganizations!: () => Organization[]
  readonly getActiveBasicMembers!: () => Member[]
  readonly getPendingBasicMembers!: () => Invitation[]
  readonly resendInvitation!: (Invitation) => void
  readonly deleteInvitation!: (Invitation) => void
  readonly deleteMember!: (Member) => void
  readonly activeUserListing!: ActiveUserRecord[]
  readonly pendingUserListing!: PendingUserRecord[]

  private successTitle = ''
  private successText = ''

  $refs: {
    successDialog: ModalDialog
  }

  headersActive = [
    {
      text: 'User',
      align: 'left',
      sortable: true,
      value: 'name',
      width: '25%'
    },
    {
      text: 'Roles',
      align: 'left',
      sortable: true,
      value: 'role',
      width: '25%'
    },
    {
      text: 'Last Active',
      align: 'left',
      sortable: true,
      value: 'lastActive',
      width: '25%'
    },
    {
      text: ' ',
      value: 'action',
      sortable: false,
      width: '25%'
    }
  ]

  headersPending = [
    {
      text: 'User',
      align: 'left',
      sortable: true,
      value: 'email',
      width: '25%'
    },
    {
      text: 'Invitation Sent',
      align: 'left',
      sortable: true,
      value: 'invitationSent',
      width: '25%'
    },
    {
      text: 'Expires',
      align: 'left',
      sortable: true,
      value: 'invitationExpires',
      width: '25%'
    },
    {
      text: '',
      value: 'action',
      sortable: false
    }
  ]

  mounted () {
    this.getOrganizations()
    this.getActiveBasicMembers()
    this.getPendingBasicMembers()
  }

  showInviteUsersModal () {
    this.isInviteUsersModalVisible = true
  }

  cancelModal () {
    this.isInviteUsersModalVisible = false
  }

  showSuccessModal () {
    this.isInviteUsersModalVisible = false
    this.successTitle = `Invited ${this.sentInvitations.length} Team Members`
    this.successText = 'Your team invitations have been sent successfully.'
    this.$refs.successDialog.open()
    this.getPendingBasicMembers()
  }

  okCloseModal () {
    this.isInviteSuccessModalVisible = false
    this.isInviteErrorModalVisible = false
  }

  async resend (pendingUser: PendingUserRecord) {
    const invitationToResend = this.pendingBasicMembers.find(invitation => invitation.id === pendingUser.invitationId)
    if (invitationToResend) {
      await this.resendInvitation(invitationToResend)
      this.showSuccessModal()
    }
  }

  async removeInvite (pendingUser: PendingUserRecord) {
    const invitationToDelete = this.pendingBasicMembers.find(invitation => invitation.id === pendingUser.invitationId)
    if (invitationToDelete) {
      await this.deleteInvitation(invitationToDelete)
      this.getPendingBasicMembers()
    }
  }

  async removeMember (activeMember: ActiveUserRecord) {
    const memberToDelete = this.activeBasicMembers.find(member => member.user.username === activeMember.username)
    if (memberToDelete) {
      this.organizations
        .filter(org => org.orgType === 'IMPLICIT')
        .forEach(async org => {
          await this.deleteMember({ orgId: org.id, memberId: memberToDelete.id })
        })
      this.getActiveBasicMembers()
    }
  }
}
</script>

<style lang="scss">
  @media (min-width: 1264px) {
    .invite-user-dialog {
      max-width: 45rem;
    }
  }
</style>
