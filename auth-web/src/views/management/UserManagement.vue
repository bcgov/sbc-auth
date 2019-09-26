<template>
  <div>
    <div class="header">
      <h2>Manage Users</h2>
      <v-btn class="invite-user-btn" color="primary" @click="showInviteUsersModal()">
        Invite Users
      </v-btn>
    </div>
    <v-card class="user-table">
      <v-tabs v-model="tab">
        <v-tab>
          Active
        </v-tab>
        <v-tab>
          Pending
        </v-tab>
      </v-tabs>
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <v-data-table
                :headers="headersActive"
                :items="activeUserListing"
                :items-per-page="5"
                class="elevation-1"
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
                class="elevation-1"
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
    <v-dialog v-model="isInviteUsersModalVisible" persistent max-width="550px">
      <InviteUsersForm
        @invites-complete="showInviteSummaryModal()"
        @cancel="cancelModal()"
      >
      </InviteUsersForm>
    </v-dialog>

    <v-dialog v-model="isInviteSuccessModalVisible" persistent max-width="350px">
      <v-card>
          <v-card-text class="text-center">
            <v-icon class="outlined my-5" x-large color="black">check</v-icon>
            <p class="title my-5" v-show="!resending">Invited {{ sentInvitations.length }} Team Members</p>
            <p class="title my-5" v-show="resending">{{ sentInvitations.length }} invitations resent</p>
            <p class="my-5">Your team invitations were sent successfully.</p>
            <v-btn class="my-5" @click="okCloseModal()" color="primary" large>
              Okay
            </v-btn>
          </v-card-text>
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
      value: 'role'
    },
    {
      text: 'Last Active',
      align: 'left',
      sortable: true,
      value: 'lastActive'
    },
    {
      text: '',
      value: 'action',
      sortable: false
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
      value: 'invitationSent'
    },
    {
      text: 'Expires',
      align: 'left',
      sortable: true,
      value: 'invitationExpires'
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
  .header {
    display: flex;
    justify-content: space-between
  }

  .invite-user-btn {
    margin-right: 1.5em
  }

  .user-table {
    margin-right: 1.5em
  }

  .v-icon.outlined {
    border: 1px solid currentColor;
    border-radius:50%;
    height: 56px;
    width: 56px;
  }
</style>
