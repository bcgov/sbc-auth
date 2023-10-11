<template>
  <v-container class="pa-0">
    <header class="view-header align-center justify-space-between mt-n1 mb-4">
      <h2 class="view-header__title">
        Account Management
      </h2>
      <div class="view-header__actions">
        <v-btn
          v-if="canCreateAccounts"
          large
          color="primary"
          class="font-weight-bold"
          @click="openCreateAccount"
        >
          <v-icon
            small
            class="mr-1"
          >
            mdi-plus
          </v-icon>Create Account
        </v-btn>
      </div>
    </header>
    <!-- Tab Navigation -->
    <v-tabs
      v-model="tab"
      background-color="transparent"
      class="mb-9"
      @change="tabChange"
    >
      <v-tab
        v-if="canViewAccounts"
        data-test="active-tab"
        :to="pagesEnum.STAFF_DASHBOARD_ACTIVE"
      >
        Active
      </v-tab>

      <template v-if="canCreateAccounts">
        <v-tab
          data-test="invitations-tab"
          :to="pagesEnum.STAFF_DASHBOARD_INVITATIONS"
        >
          <v-badge
            inline
            color="primary"
            :content="pendingInvitationsCount"
            :value="pendingInvitationsCount"
          >
            Invitations
          </v-badge>
        </v-tab>
      </template>

      <template v-if="canManageAccounts">
        <v-tab
          data-test="pending-review-tab"
          :to="pagesEnum.STAFF_DASHBOARD_REVIEW"
        >
          <v-badge
            inline
            color="primary"
            :content="pendingTasksCount"
            :value="pendingTasksCount"
          >
            Pending Review
          </v-badge>
        </v-tab>
        <v-tab
          data-test="rejected-tab"
          :to="pagesEnum.STAFF_DASHBOARD_REJECTED"
        >
          <v-badge
            inline
            color="primary"
            :content="rejectedTasksCount"
            :value="rejectedTasksCount"
          >
            Rejected
          </v-badge>
        </v-tab>
      </template>

      <template v-if="canSuspendAccounts">
        <v-tab
          data-test="suspended-tab"
          :to="pagesEnum.STAFF_DASHBOARD_SUSPENDED"
        >
          <v-badge
            inline
            color="primary"
            :content="suspendedReviewCount"
            :value="suspendedReviewCount"
          >
            Suspended
          </v-badge>
        </v-tab>
      </template>
    </v-tabs>

    <!-- Tab Contents -->
    <v-tabs-items v-model="tab">
      <router-view />
    </v-tabs-items>
    <StaffCreateAccountModal ref="staffCreateAccountDialog" />
  </v-container>
</template>

<script lang="ts">
import { Action, State } from 'pinia-class'
import { Component, Vue } from 'vue-property-decorator'
import { Pages, Role } from '@/util/constants'
import { mapActions, mapState } from 'pinia'
import { Code } from '@/models/Code'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Organization } from '@/models/Organization'
import StaffActiveAccountsTable from '@/components/auth/staff/account-management/StaffActiveAccountsTable.vue'
import StaffCreateAccountModal from '@/components/auth/staff/account-management/StaffCreateAccountModal.vue'
import StaffPendingAccountInvitationsTable from '@/components/auth/staff/account-management/StaffPendingAccountInvitationsTable.vue'
import StaffPendingAccountsTable from '@/components/auth/staff/account-management/StaffPendingAccountsTable.vue'
import StaffRejectedAccountsTable from '@/components/auth/staff/account-management/StaffRejectedAccountsTable.vue'
import { useCodesStore } from '@/stores/codes'
import { useStaffStore } from '@/stores/staff'
import { useTaskStore } from '@/stores/task'
import { useUserStore } from '@/stores/user'

enum TAB_CODE {
    Active = 'active-tab',
    PendingReview = 'pending-review-tab',
    Rejected = 'rejected-tab',
    Invitations = 'invitations-tab',
    Suspended = 'suspended-tab'
}

@Component({
  components: {
    StaffActiveAccountsTable,
    StaffPendingAccountsTable,
    StaffRejectedAccountsTable,
    StaffPendingAccountInvitationsTable,
    StaffCreateAccountModal
  },
  methods: {
    ...mapActions(useStaffStore, [
      'syncPendingInvitationOrgs',
      'syncSuspendedStaffOrgs'
    ])
  },
  computed: {
    ...mapState(useUserStore, ['currentUser']),
    ...mapState(useStaffStore, [
      'pendingInvitationsCount',
      'suspendedReviewCount'
    ])
  }
})
export default class StaffAccountManagement extends Vue {
  private tab = 0
  private readonly currentUser!: KCUserProfile
  private readonly syncRejectedStaffOrgs!: () => Organization[]
  private readonly syncPendingInvitationOrgs!: () => Organization[]
  private readonly syncSuspendedStaffOrgs!: () => Organization[]
  @Action(useCodesStore) readonly getCodes!: () => Promise<Code[]>
  @Action(useTaskStore) readonly syncTasks!: () => Promise<void>
  @State(useTaskStore) private pendingTasksCount: number
  @State(useTaskStore) private rejectedTasksCount: number

  private readonly pendingInvitationsCount!: number
  private readonly suspendedReviewCount!: number
  private pagesEnum = Pages

  $refs: {
      staffCreateAccountDialog: any
  }

  private tabs = [
    {
      id: 0,
      tabName: 'Active',
      code: TAB_CODE.Active
    },
    {
      id: 1,
      tabName: 'Invitations',
      code: TAB_CODE.Invitations
    },
    {
      id: 2,
      tabName: 'Pending Review',
      code: TAB_CODE.PendingReview
    },
    {
      id: 3,
      tabName: 'Rejected',
      code: TAB_CODE.Rejected
    },
    {
      id: 4,
      tabName: 'Suspended',
      code: TAB_CODE.Suspended
    }
  ]

  private get isGovmInviteEnable (): boolean {
    return true
  }

  private async mounted () {
    await this.getCodes()
    await this.syncTasks()
    await this.syncSuspendedStaffOrgs()
    if (this.canCreateAccounts) {
      await this.syncPendingInvitationOrgs()
    }
  }

  openCreateAccount () {
    if (this.isGovmInviteEnable) {
      this.$refs.staffCreateAccountDialog.open()
    } else {
      this.$router.push({ path: `/${Pages.STAFF_SETUP_ACCOUNT}` })
    }
  }

  private get canManageAccounts () {
    return this.currentUser?.roles?.includes(Role.StaffManageAccounts)
  }

  private get canCreateAccounts () {
    return this.currentUser?.roles?.includes(Role.StaffCreateAccounts)
  }

  private get canViewAccounts () {
    return this.currentUser?.roles?.includes(Role.StaffViewAccounts)
  }

  private get canSuspendAccounts () {
    return this.currentUser?.roles?.includes(Role.StaffSuspendAccounts) || this.currentUser?.roles?.includes(Role.StaffViewAccounts)
  }

  private async tabChange (tabIndex) {
    const selected = this.tabs.filter((tab) => (tab.id === tabIndex))
    if (selected[0]?.code === TAB_CODE.Invitations) {
      await this.syncPendingInvitationOrgs()
    }
  }
}
</script>
