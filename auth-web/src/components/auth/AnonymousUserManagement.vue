<template>
  <v-container>
    <header class="view-header align-center">
      <h2 class="view-header__title">Team Members</h2>
      <div class="view-header__actions">
        <v-btn color="primary" v-if="canInvite" @click="showAddUsersModal()" data-test="add-people-button">
          <v-icon small>mdi-plus</v-icon>
          <span>Add Team Member</span>
        </v-btn>
      </div>
    </header>

    <!-- Team member listing -->
    <MemberDataTable
      @confirm-remove-member="showConfirmRemoveModal($event, $refs.confirmActionDialog)"
      @confirm-change-role="showConfirmChangeRoleModal($event, $refs.confirmActionDialogWithQuestion)"
      @confirm-leave-team="showConfirmLeaveTeamModal($refs.confirmActionDialog)"
      @confirm-dissolve-team="showConfirmDissolveModal($refs.confirmActionDialog)"
      @single-owner-error="showSingleOwnerErrorModal($refs.errorDialog)"
    />

    <!-- Add Users Dialog -->
    <ModalDialog
      ref="addAnonUsersDialog"
      :show-icon="false"
      :show-actions="false"
      :fullscreen-on-mobile="$vuetify.breakpoint.xsOnly || $vuetify.breakpoint.smOnly || $vuetify.breakpoint.mdOnly"
      :is-persistent="true"
      :is-scrollable="true"
      max-width="640"
    >
      <template v-slot:title>
        <span>Add Team Members</span>
      </template>
      <template v-slot:text>
        <AddUsersForm @add-users-complete="showSuccessModal()" @cancel="close($refs.addAnonUsersDialog)" />
      </template>
    </ModalDialog>

    <!-- Add Users Success Modal -->
    <ModalDialog
      ref="addUsersSuccessDialog"
      :title="successTitle"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:actions>
        <v-btn large color="error" @click="close($refs.addUsersSuccessDialog)">OK</v-btn>
      </template>

      <template v-slot:text>
        <AddUsersSuccess/>
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
        <v-btn large color="default" @click="close($refs.confirmActionDialog)">{{ secondaryActionText }}</v-btn>
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
        <v-btn large color="default" @click="close($refs.confirmActionDialogWithQuestion)">{{ secondaryActionText }}</v-btn>
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
        <v-btn large color="error" @click="close($refs.errorDialog)">OK</v-btn>
      </template>
    </ModalDialog>

  </v-container>
</template>

<script lang="ts">
import { ActiveUserRecord, AddUserBody, Member, MembershipStatus, MembershipType, Organization, PendingUserRecord, UpdateMemberPayload } from '@/models/Organization'
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import MemberDataTable, { ChangeRolePayload } from '@/components/auth/MemberDataTable.vue'
import { mapActions, mapState } from 'vuex'
import AddUsersForm from '@/components/auth/AddUsersForm.vue'
import AddUsersSuccess from '@/components/auth/AddUsersSuccess.vue'
import { Business } from '@/models/business'
import ConfigHelper from '@/util/config-helper'
import { Event } from '@/models/event'
import { EventBus } from '@/event-bus'
import { Invitation } from '@/models/Invitation'
import InvitationsDataTable from '@/components/auth/InvitationsDataTable.vue'
import InviteUsersForm from '@/components/auth/InviteUsersForm.vue'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import OrgModule from '@/store/modules/org'
import PendingMemberDataTable from '@/components/auth/PendingMemberDataTable.vue'
import { SessionStorageKeys } from '@/util/constants'
import TeamManagementMixin from '@/components/auth/mixins/TeamManagementMixin.vue'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    MemberDataTable,
    ModalDialog,
    AddUsersForm,
    AddUsersSuccess
  },
  computed: {
    ...mapState('org', [
      'createdUsers'
    ])
  },
  methods: {
    ...mapActions('org', [
      'syncActiveOrgMembers'
    ])
  }
})
export default class AnonymousUserManagement extends Mixins(TeamManagementMixin) {
  @Prop({ default: '' }) private orgId: string;
  // @Prop() private confirmActionDialogWithQuestion: ModalDialog;

  private isLoading = true

  private readonly syncActiveOrgMembers!: () => Member[]
  private readonly createdUsers!: AddUserBody[]

  $refs: {
    successDialog: ModalDialog
    errorDialog: ModalDialog
    confirmActionDialog: ModalDialog
    confirmActionDialogWithQuestion: ModalDialog
    addAnonUsersDialog: ModalDialog
    addUsersSuccessDialog: ModalDialog
  }

  private async mounted () {
    this.isLoading = false
    await this.syncActiveOrgMembers()
  }

  private showAddUsersModal () {
    this.$refs.addAnonUsersDialog.open()
  }

  private cancelAddUsersModal () {
    this.$refs.addAnonUsersDialog.close()
  }

  private showSuccessModal () {
    this.$refs.addAnonUsersDialog.close()
    this.successTitle = `Added ${this.createdUsers.length} Team Members`
    this.$refs.addUsersSuccessDialog.open()
  }
}
</script>

<style lang="scss" scoped>
  .view-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
  }
  .v-text-field {
    margin: 2px;
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

</style>
