<template>
  <div>
    <header class="view-header align-center mb-5">
      <h2 class="view-header__title">
        Team Members
      </h2>
      <div class="view-header__actions">
        <v-btn
          v-can:INVITE_MEMBERS.hide
          large
          color="primary"
          data-test="add-people-button"
          @click="showAddUsersModal()"
        >
          <v-icon small>
            mdi-plus
          </v-icon>
          <span>Add Team Member</span>
        </v-btn>
      </div>
    </header>

    <SearchFilterInput
      class="mb-6"
      :filterParams="searchFilter"
      :filteredRecordsCount="teamMembersCount"
      @filter-texts="setAppliedFilterValue"
    />

    <!-- Team member listing -->
    <MemberDataTable
      :userNamefilterText="appliedFilterValue"
      @confirm-remove-member="
        showConfirmRemoveModal($event, $refs.confirmActionDialog)
      "
      @confirm-change-role="
        showConfirmChangeRoleModal(
          $event,
          $refs.confirmActionDialogWithQuestion
        )
      "
      @reset-password="showResetPasswordModal($event)"
      @confirm-leave-team="showConfirmLeaveTeamModal($refs.confirmActionDialog)"
      @confirm-dissolve-team="
        showConfirmDissolveModal($refs.confirmActionDialog)
      "
      @single-owner-error="showSingleOwnerErrorModal($refs.errorDialog)"
      @filtered-members-count="filteredTeamMembersCount"
    />

    <!-- Add Users Dialog -->
    <ModalDialog
      ref="addAnonUsersDialog"
      :show-icon="false"
      :show-actions="false"
      :fullscreen-on-mobile="
        $vuetify.breakpoint.xsOnly ||
          $vuetify.breakpoint.smOnly ||
          $vuetify.breakpoint.mdOnly
      "
      :is-persistent="true"
      :is-scrollable="true"
      max-width="800"
    >
      <template #title>
        <span>Add Team Members</span>
      </template>
      <template #text>
        <AddUsersForm
          @add-users-complete="showSuccessModal()"
          @cancel="close($refs.addAnonUsersDialog)"
        />
      </template>
    </ModalDialog>

    <!-- Add Users Dialog -->
    <ModalDialog
      ref="passwordResetDialog"
      :show-icon="false"
      :show-actions="false"
      :fullscreen-on-mobile="
        $vuetify.breakpoint.xsOnly ||
          $vuetify.breakpoint.smOnly ||
          $vuetify.breakpoint.mdOnly
      "
      :is-persistent="true"
      :is-scrollable="true"
      max-width="800"
    >
      <template #title>
        <span>Reset Password</span>
      </template>
      <template #text>
        <PasswordReset
          ref="passwordResetComp"
          :user="user"
          @reset-complete="showUpdateModal()"
          @reset-error="showPasswordResetErrorModal()"
          @cancel="close($refs.passwordResetDialog)"
        />
      </template>
    </ModalDialog>

    <PasswordReset
      ref="passwordResetComp"
      @reset-complete="showUpdateModal()"
      @reset-error="showPasswordResetErrorModal()"
    />

    <!-- Password Reset Success Modal -->
    <ModalDialog
      ref="passwordResetSuccessDialog"
      :title="successTitle"
      dialog-class="notify-dialog"
      max-width="640"
      :show-icon="true"
    >
      <template #actions>
        <v-btn
          large
          color="primary"
          @click="close($refs.passwordResetSuccessDialog)"
        >
          OK
        </v-btn>
      </template>

      <template #icon>
        <v-icon
          large
          color="success"
        >
          mdi-check
        </v-icon>
      </template>

      <template #text>
        <AddUsersSuccess
          ref="addUserSuccessRef"
          :action="action"
        />
      </template>
    </ModalDialog>

    <!-- Add Users Success Modal -->
    <ModalDialog
      ref="addUsersSuccessDialog"
      :title="successTitle"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #actions>
        <v-btn
          large
          color="primary"
          @click="close($refs.addUsersSuccessDialog)"
        >
          OK
        </v-btn>
      </template>

      <template
        v-if="!createdUsers.length && failedUsers.length"
        #icon
      >
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>

      <template #text>
        <AddUsersSuccess ref="addUserSuccessRef" />
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
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="primary"
          @click="confirmHandler()"
        >
          {{
            primaryActionText
          }}
        </v-btn>
        <v-btn
          large
          color="default"
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
      <template #icon>
        <v-icon
          large
          :color="primaryActionType"
        >
          mdi-information-outline
        </v-icon>
      </template>
      <template #actions>
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
      max-width="640"
    />

    <!-- Alert Dialog (Error) -->
    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          large
          color="error"
          @click="close($refs.errorDialog)"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import {
  BulkUsersFailed,
  BulkUsersSuccess,
  Member
} from '@/models/Organization'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapState } from 'pinia'
import AddUsersForm from '@/components/auth/account-settings/team-management/AddUsersForm.vue'
import AddUsersSuccess from '@/components/auth/account-settings/team-management/AddUsersSuccess.vue'
import MemberDataTable from '@/components/auth/account-settings/team-management/MemberDataTable.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PasswordReset from '@/components/auth/account-settings/team-management/PasswordReset.vue'
import { SearchFilterCodes } from '@/util/constants'
import SearchFilterInput from '@/components/auth/common/SearchFilterInput.vue'
import { SearchFilterParam } from '@/models/searchfilter'
import TeamManagementMixin from '@/components/auth/mixins/TeamManagementMixin.vue'
import { User } from '@/models/user'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    PasswordReset,
    MemberDataTable,
    ModalDialog,
    AddUsersForm,
    AddUsersSuccess,
    SearchFilterInput
  },
  computed: {
    ...mapState(useOrgStore, ['createdUsers', 'failedUsers'])
  },
  methods: {
    ...mapActions(useOrgStore, ['syncActiveOrgMembers'])
  }
})
export default class AnonymousUserManagement extends Mixins(
  TeamManagementMixin
) {
  @Prop({ default: '' }) private orgId: string
  // @Prop() private confirmActionDialogWithQuestion: InstanceType<typeof ModalDialog>;

  private isLoading = true

  private readonly syncActiveOrgMembers!: () => Member[]
  private readonly createdUsers!: BulkUsersSuccess[]
  private readonly failedUsers!: BulkUsersFailed[]
  private user: User = { firstname: '', lastname: '', username: '' }
  private action = ''
  private appliedFilterValue: string = ''
  private teamMembersCount = 0
  private searchFilter: SearchFilterParam[] = [
    {
      id: SearchFilterCodes.USERNAME,
      placeholder: 'Team Member',
      labelKey: 'Team Member',
      appliedFilterValue: '',
      filterInput: ''
    }
  ]

  $refs: {
    successDialog: InstanceType<typeof ModalDialog>
    errorDialog: InstanceType<typeof ModalDialog>
    confirmActionDialog: InstanceType<typeof ModalDialog>
    confirmActionDialogWithQuestion: InstanceType<typeof ModalDialog>
    addAnonUsersDialog: InstanceType<typeof ModalDialog>
    addUsersSuccessDialog: InstanceType<typeof ModalDialog>
    passwordResetDialog: InstanceType<typeof ModalDialog>
    passwordResetSuccessDialog: InstanceType<typeof ModalDialog>
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

  protected showPasswordResetErrorModal () {
    this.$refs.passwordResetDialog.close()
    this.errorTitle = this.$t('passwordResetFailureTitle').toString()
    this.errorText = this.$t('passwordResetFailureText').toString()
    this.$refs.errorDialog.open()
  }

  private showResetPasswordModal (payload: User) {
    this.user = payload
    this.$refs.passwordResetDialog.open()
  }

  private showUpdateModal () {
    this.$refs.passwordResetDialog.close()
    this.action = 'resetpassword'
    this.successTitle = `Password Reset`
    this.$refs.passwordResetSuccessDialog.open()
  }

  private showSuccessModal () {
    this.$refs.addAnonUsersDialog.close()
    this.successTitle = `${this.createdUsers.length} Team Members Added`
    if (this.createdUsers.length) {
      this.successTitle = `${this.createdUsers.length} of ${this.failedUsers
        .length + this.createdUsers.length} Team Members Added`
    }
    this.$refs.addUsersSuccessDialog.open()
  }

  private setAppliedFilterValue (filter: SearchFilterParam[]) {
    this.appliedFilterValue = filter[0].appliedFilterValue
  }

  private filteredTeamMembersCount (count: number) {
    this.teamMembersCount = count
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
</style>
