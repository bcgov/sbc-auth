<template>
  <div class="user-mgmt-view">
    <header class="view-header mt-1 mb-5">
      <h1>Manage Team</h1>
      <div class="view-header__actions">
        <v-btn outlined color="primary" @click="showInviteUsersModal()">
          <v-icon>add</v-icon>
          <span>Invite Team Members</span>
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
            class="user-list__active"
            :headers="headersActive"
            :items="basicMembers"
            :items-per-page="5"
            :calculate-widths="true"
            :loading="isLoading"
          >
            <template v-slot:loading>
              Loading...
            </template>
            <template v-slot:item.name="{ item }">
              <span class="user-name">{{ item.name }}</span>
              {{ item.email }}
            </template>
            <template v-slot:item.role="{ item }">
              <v-menu offset-y>
                <template v-slot:activator="{ on }">
                  <v-btn depressed small v-on="on">
                    {{ item.role }}
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
            <template v-slot:item.action="{ item }">
              <v-btn depressed small @click="removeMember(item)">Remove</v-btn>
            </template>
          </v-data-table>
        </v-tab-item>
        <v-tab-item>
          <v-data-table
            class="user-list__pending"
            :headers="headersPending"
            :items="basicInvitations"
            :items-per-page="5"
            :calculate-widths="true"
          >
            <template v-slot:item.action="{ item }">
              <v-btn depressed small class="mr-2" @click="resend(item)">Resend</v-btn>
              <v-btn depressed small @click="removeInvite(item)">Remove</v-btn>
            </template>
          </v-data-table>
        </v-tab-item>
      </v-tabs-items>
    </v-card>

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

    <!-- Alert Dialog (Success) -->
    <ModalDialog
      ref="successDialog"
      :title="successTitle"
      :text="successText"
      dialog-class="notify-dialog"
      max-width="640"
    ></ModalDialog>
  </div>
</template>

<script lang="ts">
import { ActiveUserRecord, Member, Organization, PendingUserRecord, UpdateMemberPayload } from '@/models/Organization'
import { Component, Vue } from 'vue-property-decorator'
import { mapActions, mapGetters, mapState } from 'vuex'
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
      'organizations',
      'resending',
      'sentInvitations'
    ]),
    basicMembers (): ActiveUserRecord[] {
      return _.uniqWith(
        _.flatten(this.organizations.map(org => org.members)),
        (memberA: Member, memberB: Member) => memberA.user.username === memberB.user.username
      )
        .map((member: Member) => {
          return {
            username: member.user.username,
            name: `${member.user.firstname} ${member.user.lastname}`,
            role: member.membershipTypeCode,
            lastActive: moment(member.user.modified).format('DD MMM, YYYY'),
            member
          }
        })
    },
    basicInvitations (): PendingUserRecord[] {
      return _.flatten(this.organizations.map(org => org.invitations))
        .filter((inv: Invitation) => inv.status === 'PENDING')
        .map((invitation: Invitation) => {
          return {
            email: invitation.recipientEmail,
            invitationSent: moment(invitation.sentDate).format('DD MMM, YYYY'),
            invitationExpires: moment(invitation.expiresOn).format('DD MMM, YYYY'),
            invitation
          }
        })
    }
  },
  methods: {
    ...mapActions('org', [
      'syncOrganizations',
      'resendInvitation',
      'deleteInvitation',
      'deleteMember',
      'updateMemberRole'
    ])
  }
})
export default class UserManagement extends Vue {
  private orgStore = getModule(OrgModule, this.$store)
  private userStore = getModule(UserModule, this.$store)
  private successTitle = ''
  private successText = ''
  private tab = null
  private isLoading = true

  private readonly organizations!: Organization[]
  private readonly resending!: boolean
  private readonly sentInvitations!: Invitation[]
  private readonly syncOrganizations!: () => Organization[]
  private readonly resendInvitation!: (invitation: Invitation) => void
  private readonly deleteInvitation!: (invitation: Invitation) => void
  private readonly deleteMember!: (deleteMemberPayload: UpdateMemberPayload) => void
  private readonly updateMemberRole!: (UpdateMemberPayload: UpdateMemberPayload) => void

  $refs: {
    successDialog: ModalDialog
    inviteUsersDialog: ModalDialog
  }

  availableRoles = [
    'Member',
    'Admin',
    'Owner'
  ]

  headersActive = [
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

  headersPending = [
    {
      text: 'Email',
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
    },
    {
      text: 'Actions',
      align: 'left',
      value: 'action',
      sortable: false,
      width: '195'
    }
  ]

  async created () {
    this.isLoading = true
    await this.syncOrganizations()
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

  async removeInvite (pendingUser: PendingUserRecord) {
    await this.deleteInvitation(pendingUser.invitation)
  }

  async removeMember (activeMember: ActiveUserRecord) {
    // BASIC user only
    this.organizations
      .filter(org => org.orgType === 'IMPLICIT')
      .forEach(async org => {
        await this.deleteMember({ orgIdentifier: org.id, memberId: activeMember.member.id })
      })
  }

  changeRole (activeMember: ActiveUserRecord, targetRole: string) {
    if (activeMember.role.toUpperCase() === targetRole.toUpperCase()) {
      return
    }
    // BASIC user only
    this.organizations
      .filter(org => org.orgType === 'IMPLICIT')
      .forEach(async org => {
        await this.updateMemberRole({
          orgIdentifier: org.id,
          memberId: activeMember.member.id,
          role: targetRole.toUpperCase()
        })
      })
  }
}
</script>

<style lang="scss" scoped>
>>> .v-data-table td {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

>>> .v-data-table.user-list__active td {
  height: 4rem;
  vertical-align: top;
}

.user-name {
  display: block;
  font-weight: 700;
}
</style>
