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
          </v-data-table>
        </v-tab-item>
        <v-tab-item>
          <v-data-table
                :headers="headersPending"
                :items="pendingUserListing"
                :items-per-page="5"
                class="elevation-1"
              >
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
import { Component, Vue } from 'vue-property-decorator'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import { mapState, mapGetters, mapActions } from 'vuex'
import { Organization, Member } from '@/models/Organization'
import { Invitation } from '@/models/Invitation'
import moment from 'moment'

interface ActiveUserRecord {
  name: string
  role: string
  lastActive: string
}

interface PendingUserRecord {
  email: string
  invitationSent: string
  invitationExpires?: string
}

@Component({
  components: {
    InviteUsersForm
  },
  computed: {
    ...mapState('org', ['currentOrg', 'resending', 'sentInvitations']),
    ...mapState('user', ['activeBasicMembers', 'pendingBasicMembers']),
    ...mapGetters('user', ['organizations'])
  },
  methods: {
    ...mapActions('user', ['getOrganizations', 'getActiveBasicMembers', 'getPendingBasicMembers'])
  }
})
export default class UserManagement extends Vue {
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

  headersActive = [
    {
      text: 'User',
      align: 'left',
      sortable: true,
      value: 'name'
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
    }
  ]

  headersPending = [
    {
      text: 'User',
      align: 'left',
      sortable: true,
      value: 'email'
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
    }
  ]

  get activeUserListing (): ActiveUserRecord[] {
    return this.activeBasicMembers.map(member => {
      return {
        name: `${member.user.firstname} ${member.user.lastname}`,
        role: member.membershipTypeCode,
        lastActive: moment(member.user.modified).format('l')
      }
    })
  }

  get pendingUserListing (): PendingUserRecord[] {
    return this.pendingBasicMembers.map(invitation => {
      return {
        email: invitation.recipientEmail,
        invitationSent: moment(invitation.sentDate).format('lll')
      }
    })
  }

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
