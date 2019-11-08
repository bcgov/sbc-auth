<template>
  <v-container class="view-container">
    <header class="view-header mt-1 mb-5">
      <h1>Team Members <span class="body-1" v-if="currentBusiness">({{ currentBusiness.name }})</span></h1>
      <div class="view-header__actions">
        <v-btn outlined color="primary" @click="showInviteUsersModal()">
          <v-icon>add</v-icon>
          <span>Invite People</span>
        </v-btn>
      </div>
    </header>

    <!-- Tab Navigation -->
    <v-tabs v-model="tab" background-color="transparent" class="mb-3">
      <v-tab>Active</v-tab>
      <v-tab>Pending Approval</v-tab>
      <v-tab>Invitations</v-tab>
    </v-tabs>

    <v-card>
      <!-- Tab Contents -->
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <v-data-table
            class="user-list__active"
            :headers="headerMembers"
            :items="orgMembers"
            :items-per-page="5"
            :calculate-widths="true"
            :loading="isLoading"
          >
            <template v-slot:loading>
              Loading...
            </template>
            <template v-slot:item.name="{ item }">
              <span class="user-name">{{ item.user.firstname }} {{ item.user.lastname }}</span>
              <span v-if="item.user.contacts && item.user.contacts.length > 0">{{ item.user.contacts[0].email }}</span>
            </template>
            <template v-slot:item.role="{ item }">
              <v-menu offset-y>
                <template v-slot:activator="{ on }">
                  <v-btn depressed small v-on="on">
                    {{ item.membershipTypeCode }}
                    <v-icon small class="ml-1">keyboard_arrow_down</v-icon>
                  </v-btn>
                </template>
                <v-list>
                  <v-list-item
                    v-for="(role, index) in availableRoles"
                    :key="index"
                    @click="changeRole(item, role)"
                  >
                    <v-list-item-title>{{ role }}</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </template>
            <template v-slot:item.lastActive="{ item }">
              {{ formatDate(item.user.modified) }}
            </template>
            <template v-slot:item.action="{ item }">
              <v-btn depressed small @click="showConfirmRemoveModal(item)">Remove</v-btn>
            </template>
          </v-data-table>
        </v-tab-item>
        <v-tab-item>
        </v-tab-item>
        <v-tab-item>
          <v-data-table
            class="user-list__pending"
            :headers="headerInvitations"
            :items="orgInvitations"
            :items-per-page="5"
            :calculate-widths="true"
          >
            <template v-slot:item.sentDate="{ item }">
              {{ formatDate (item.sentDate) }}
            </template>
            <template v-slot:item.expiresOn="{ item }">
              {{ formatDate (item.expiresOn) }}
            </template>
            <template v-slot:item.action="{ item }">
              <v-btn depressed small class="mr-2" @click="resend(item)">Resend</v-btn>
              <v-btn depressed small @click="removeInvite(item)">Remove</v-btn>
            </template>
          </v-data-table>
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
      :text="$t('confirmRemoveMemberText')"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">error</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn large color="primary" @click="removeMember()">Remove</v-btn>
        <v-btn large color="default" @click="cancelRemove()">Cancel</v-btn>
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
import { mapActions, mapGetters, mapState } from 'vuex'
import { Business } from '@/models/business'
import { Invitation } from '@/models/Invitation'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import UserModule from '@/store/modules/user'
import _ from 'lodash'
import { getModule } from 'vuex-module-decorators'
import moment from 'moment'

@Component({
  components: {
    InviteUsersForm,
    ModalDialog
  },
  computed: {
    ...mapState('org', [
      'currentOrg',
      'organizations',
      'resending',
      'sentInvitations'
    ]),
    ...mapState('business', ['currentBusiness']),
    orgMembers () {
      if (this.currentOrg) {
        return this.currentOrg.members
      }
    },
    orgInvitations () {
      if (this.currentOrg) {
        return this.currentOrg.invitations
      }
    }
  },
  methods: {
    ...mapActions('org', [
      'syncCurrentOrg',
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

  private readonly currentOrg!: Organization
  private readonly currentBusiness!: Business
  private readonly organizations!: Organization[]
  private readonly resending!: boolean
  private readonly sentInvitations!: Invitation[]
  private readonly syncCurrentOrg!: () => Organization
  private readonly resendInvitation!: (invitation: Invitation) => void
  private readonly deleteInvitation!: (invitationId: number) => void
  private readonly deleteMember!: (memberId: number) => void
  private readonly updateMemberRole!: (updateMemberPayload: UpdateMemberPayload) => void

  $refs: {
    successDialog: ModalDialog
    inviteUsersDialog: ModalDialog
    confirmRemoveDialog: ModalDialog
  }

  availableRoles = [
    'Member',
    'Admin',
    'Owner'
  ]

  headerMembers = [
    {
      text: 'Team Member',
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
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '95'
    }
  ]

  headerInvitations = [
    {
      text: 'Email',
      align: 'left',
      sortable: true,
      value: 'recipientEmail'
    },
    {
      text: 'Invitation Sent',
      align: 'left',
      sortable: true,
      value: 'sentDate'
    },
    {
      text: 'Expires',
      align: 'left',
      sortable: true,
      value: 'expiresOn'
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '195'
    }
  ]

  // get orgMembers (): Member[] {
  //   return this.currentOrg && this.currentOrg.members ? this.currentOrg.members : []
  // }

  // get orgInvitations (): Invitation[] {
  //   return this.currentOrg && this.currentOrg.invitations ? this.currentOrg.invitations : []
  // }

  private formatDate (date: Date) {
    return moment(date).format('DD MMM, YYYY')
  }

  async mounted () {
    this.isLoading = true
    if (!this.currentOrg) {
      await this.syncCurrentOrg()
    }
    this.isLoading = false
  }

  showInviteUsersModal () {
    this.$refs.inviteUsersDialog.open()
  }

  cancelInviteUsersModal () {
    this.$refs.inviteUsersDialog.close()
  }

  showSuccessModal () {
    this.$refs.inviteUsersDialog.close()
    this.successTitle = `Invited ${this.sentInvitations.length} Team Members`
    this.successText = 'Your team invitations have been sent successfully.'
    this.$refs.successDialog.open()
  }

  async resend (pendingUser: PendingUserRecord) {
    await this.resendInvitation(pendingUser.invitation)
    this.showSuccessModal()
  }

  async removeInvite (invitation: Invitation) {
    await this.deleteInvitation(invitation.id)
  }

  showConfirmRemoveModal (member: Member) {
    this.memberToBeRemoved = member
    this.$refs.confirmRemoveDialog.open()
  }

  cancelRemove () {
    this.$refs.confirmRemoveDialog.close()
  }

  private async removeMember () {
    await this.deleteMember(this.memberToBeRemoved.id)
    this.$refs.confirmRemoveDialog.close()
  }

  private async changeRole (member: Member, targetRole: string) {
    if (member.membershipTypeCode.toUpperCase() === targetRole.toUpperCase()) {
      return
    }

    await this.updateMemberRole({
      memberId: member.id,
      role: targetRole.toUpperCase()
    })
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
