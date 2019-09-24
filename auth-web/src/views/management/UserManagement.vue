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
                :items="activeUsers"
                :items-per-page="5"
                class="elevation-1"
              >
          </v-data-table>
        </v-tab-item>
        <v-tab-item>
          <v-data-table
                :headers="headersPending"
                :items="pendingUsers"
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
        @invite-success="showInviteSuccessModal($event)"
        @invite-error="showErrorModal()"
        @cancel="cancelModal()"
      >
      </InviteUsersForm>
    </v-dialog>

    <v-dialog v-model="isInviteSuccessModalVisible" persistent max-width="350px">
      <v-card>
          <v-card-text class="text-center">
            <v-icon class="outlined my-5" x-large color="black">check</v-icon>
            <p class="title my-5" v-show="!isResend">Invited {{ invitationsSent }} Team Members</p>
            <p class="title my-5" v-show="isResend">{{ invitationsSent }} invitations resent</p>
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
import { SuccessEmitPayload } from '@/models/user'

@Component({
  components: {
    InviteUsersForm
  }
})
export default class UserManagement extends Vue {
  tab = null
  isInviteUsersModalVisible = false
  isInviteSuccessModalVisible = false
  isInviteErrorModalVisible = false
  isResend = false
  invitationsSent = 0

  headersActive = [
    {
      text: 'User',
      align: 'left',
      sortable: true,
      value: 'fullname'
    },
    {
      text: 'Roles',
      align: 'left',
      sortable: true,
      value: 'roles'
    },
    {
      text: 'Status',
      align: 'left',
      sortable: true,
      value: 'status'
    }
  ]

  headersPending = [
    {
      text: 'User',
      align: 'left',
      sortable: true,
      value: 'fullname'
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

  activeUsers = []
  pendingUsers = []

  mount () {

  }

  showInviteUsersModal () {
    this.isInviteUsersModalVisible = true
  }

  cancelModal () {
    this.isInviteUsersModalVisible = false
  }

  showInviteSuccessModal (eventPayload: SuccessEmitPayload) {
    this.isResend = eventPayload.isResend
    this.invitationsSent = eventPayload.invitationCount
    this.isInviteUsersModalVisible = false
    this.isInviteSuccessModalVisible = true
  }

  showInviteErrorModal () {
    this.isInviteSuccessModalVisible = false
    this.isInviteErrorModalVisible = true
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
