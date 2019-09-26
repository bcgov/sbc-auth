<template>
  <div class="user-mgmt-view">
    <header class="view-header mt-1 mb-6">
      <h1>Manage Users</h1>
      <div class="view-header__actions">
        <v-btn outlined color="primary" @click="showInviteUsersModal()">
          <v-icon>add</v-icon>
          <span>Invite Users</span>
        </v-btn>
      </div>
    </header>

    <!-- Tab Navigation -->
    <v-tabs background-color="transparent" class="mb-6" v-model="tab">
      <v-tab>Active</v-tab>
      <v-tab>Pending</v-tab>
    </v-tabs>
    
    <!-- Tab Contents -->
    <v-card>
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
    <v-dialog content-class="invite-user-dialog" v-model="isInviteUsersModalVisible" scrollable  persistent>
      <InviteUsersForm
        @invites-complete="showInviteSummaryModal()"
        @cancel="cancelModal()"
      >
      </InviteUsersForm>
    </v-dialog>

    <!-- Notification Dialog (Success) -->
    <v-dialog content-class="notify-dialog text-center" v-model="isInviteSuccessModalVisible">
      <v-card>
        <v-card-title class="pb-2">
          <v-icon x-large color="success" class="mt-3">check</v-icon>
          <span class="mt-5">Invited {{ sentInvitations.length }} Team Members</span> 
        </v-card-title>
        <v-card-text class="text-center">
          <!--
          <p v-show="!resending">Invited {{ sentInvitations.length }} Team Members</p>
          <p v-show="resending">{{ sentInvitations.length }} invitations resent</p>
          -->
          <p class="mt-5">Your team invitations were sent successfully.</p>
        </v-card-text>
        <v-card-actions class="pb-8">
          <v-btn large color="success" @click="okCloseModal()">
            OK
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import { mapState, mapGetters, mapActions } from 'vuex'
import { Organization, Member } from '@/models/Organization'
import { Invitation } from '@/models/Invitation'
import OrgModule from '@/store/modules/org'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    InviteUsersForm
  },
  computed: {
    ...mapState('org', ['currentOrg', 'resending', 'sentInvitations']),
    ...mapState('user', ['activeBasicMembers', 'pendingBasicMembers']),
    ...mapGetters('user', ['organizations', 'activeUserListing', 'pendingUserListing'])
  },
  methods: {
    ...mapActions('user', ['getOrganizations', 'getActiveBasicMembers', 'getPendingBasicMembers']),
    ...mapActions('org', ['resendInvitation', 'deleteInvitation'])
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
  readonly activeUserListing!: any
  readonly pendingUserListing!: any

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

  showInviteSummaryModal () {
    this.isInviteUsersModalVisible = false
    this.isInviteSuccessModalVisible = true
    this.getPendingBasicMembers()
  }

  okCloseModal () {
    this.isInviteSuccessModalVisible = false
    this.isInviteErrorModalVisible = false
  }

  async resend (pendingUser: any) {
    const invitationToResend = this.pendingBasicMembers.find(invitation => invitation.id === pendingUser.invitationId)
    if (invitationToResend) {
      await this.resendInvitation(invitationToResend)
      this.getPendingBasicMembers()
    }
  }

  async removeInvite (pendingUser: any) {
    const invitationToDelete = this.pendingBasicMembers.find(invitation => invitation.id === pendingUser.invitationId)
    if (invitationToDelete) {
      await this.deleteInvitation(invitationToDelete)
      this.getPendingBasicMembers()
    }
  }
}
</script>

<style lang="scss">
  // Invite Users Dialog
  .invite-user-dialog {
    max-width: 40rem;
    width: 40rem;
  }

  // Notification Dialog (Success/Error)
  .notify-dialog {
    max-width: 30rem;

    .v-card__title {
      flex-direction: column;
    }
  }
</style>
