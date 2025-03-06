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
    <template>
      <v-tabs
        v-model="tab"
        background-color="transparent"
        class="mb-9"
        @change="tabChange"
      >
        <v-tab
          v-for="tab in tabs"
          :key="tab.code"
          :data-test="tab.code"
          :to="tab.page"
        >
          <template v-if="tab.hasBadge">
            <v-badge
              inline
              color="primary"
              :content="tab.count.value"
              :value="tab.count.value"
            >
              {{ tab.tabName}}
            </v-badge>
          </template>
          <template v-else>
            {{ tab.tabName }}
          </template>
        </v-tab>
      </v-tabs>
    </template>

    <!-- Tab Contents -->
    <v-tabs-items v-model="tab">
      <router-view />
    </v-tabs-items>
    <StaffCreateAccountModal ref="staffCreateAccountDialog" />
  </v-container>
</template>

<script lang="ts">
import { Pages, Permission, Role } from '@/util/constants'
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import StaffCreateAccountModal from '@/components/auth/staff/account-management/StaffCreateAccountModal.vue'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores'
import { useStaffStore } from '@/stores/staff'
import { useTaskStore } from '@/stores/task'
import { useUserStore } from '@/stores/user'
import { storeToRefs } from 'pinia'

enum TAB_CODE {
    Active = 'active-tab',
    PendingReview = 'pending-review-tab',
    Rejected = 'rejected-tab',
    Invitations = 'invitations-tab',
    Suspended = 'suspended-tab',
    Inactive = 'inactive-tab'
}

export default defineComponent({
  name: 'StaffAccountManagement',
  components: {
    StaffCreateAccountModal
  },
  setup () {
    const orgStore = useOrgStore()
    const { permissions } = storeToRefs(orgStore)
    const { currentUser } = useUserStore()
    const { syncPendingInvitationOrgs, syncSuspendedStaffOrgs } = useStaffStore()
    const { getCodes } = useCodesStore()
    const { syncTasks } = useTaskStore()
    const staffStore = useStaffStore()
    const taskStore = useTaskStore()
    const pendingInvitationsCount = computed(() => staffStore.pendingInvitationsCount)
    const suspendedReviewCount = computed(() => staffStore.suspendedReviewCount)
    const pendingTasksCount = computed(() => taskStore.pendingTasksCount)
    const rejectedTasksCount = computed(() => taskStore.rejectedTasksCount)

    interface TabConfig {
      permission: Permission;
      tabName: string;
      code: string;
      page: string;
      hasBadge?: boolean;
      count?: ComputedRef<number>;
    }

    const TAB_CONFIGS: TabConfig[] = [
      { permission: Permission.VIEW_ACTIVE_ACCOUNTS,
        tabName: 'Active',
        code: TAB_CODE.Active,
        page: Pages.STAFF_DASHBOARD_ACTIVE
      },
      { permission: Permission.VIEW_ACCOUNT_INVITATIONS,
        tabName: 'Invitations',
        code: TAB_CODE.Invitations,
        hasBadge: true,
        count: pendingInvitationsCount.value,
        page: Pages.STAFF_DASHBOARD_INVITATIONS
      },
      { permission: Permission.VIEW_PENDING_TASKS,
        tabName: 'Pending Review',
        code: TAB_CODE.PendingReview,
        hasBadge: true,
        count: pendingTasksCount.value,
        page: Pages.STAFF_DASHBOARD_REVIEW
      },
      { permission: Permission.VIEW_REJECTED_TASKS,
        tabName: 'Rejected',
        code: TAB_CODE.Rejected,
        hasBadge: true,
        count: rejectedTasksCount,
        page: Pages.STAFF_DASHBOARD_REJECTED
      },
      { permission: Permission.VIEW_SUSPENDED_ACCOUNTS,
        tabName: 'Suspended',
        code: TAB_CODE.Suspended,
        hasBadge: true,
        count: suspendedReviewCount.value,
        page: Pages.STAFF_DASHBOARD_SUSPENDED
      },
      { permission: Permission.VIEW_INACTIVE_ACCOUNTS,
        tabName: 'Inactive',
        code: TAB_CODE.Inactive,
        page: Pages.STAFF_DASHBOARD_INACTIVE
      }
    ]

    const state = reactive({
      tab: 0,
      canManageAccounts: computed(() => currentUser?.roles?.includes(Role.StaffManageAccounts) ||
      currentUser?.roles?.includes(Role.ExternalStaffReadonly)),
      canViewInvitations: computed(() => currentUser?.roles?.includes(Role.StaffCreateAccounts) ||
        currentUser?.roles?.includes(Role.ExternalStaffReadonly)),
      canCreateAccounts: computed(() => currentUser?.roles?.includes(Role.StaffCreateAccounts) &&
      !currentUser?.roles?.includes(Role.ExternalStaffReadonly)),
      canViewAccounts: computed(() => currentUser?.roles?.includes(Role.StaffViewAccounts)),
      canSuspendAccounts: computed(() => currentUser?.roles?.includes(Role.StaffSuspendAccounts) ||
        currentUser?.roles?.includes(Role.StaffViewAccounts)),
      tabs: computed(() => {
        return TAB_CONFIGS
          .filter(({ permission }) => permissions.value.some(code => code === permission))
          .map((tabConfig, index) => ({
            id: index,
            hasBadge: false,
            ...tabConfig
          }))
      })
    })

    onMounted(async () => {
      await getCodes()
      await syncTasks()
      await syncSuspendedStaffOrgs()
      if (state.canManageAccounts) {
        await syncPendingInvitationOrgs()
      }
    })

    function openCreateAccount () {
      this.$refs.staffCreateAccountDialog.open()
    }

    async function tabChange (tabIndex) {
      const selected = this.tabs.filter((tab) => (tab.id === tabIndex))
      if (selected[0]?.code === TAB_CODE.Invitations) {
        await this.syncPendingInvitationOrgs()
      }
    }

    return {
      ...toRefs(state),
      openCreateAccount,
      tabChange,
      pendingInvitationsCount,
      pendingTasksCount,
      rejectedTasksCount,
      suspendedReviewCount
    }
  }
})
</script>
