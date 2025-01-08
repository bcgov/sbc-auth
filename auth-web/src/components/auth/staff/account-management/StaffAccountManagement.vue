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

      <template v-if="canViewInvitations">
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

      <v-tab
        v-if="canViewAccounts"
        data-test="inactive-tab"
        :to="pagesEnum.STAFF_DASHBOARD_INACTIVE"
      >
        Inactive
      </v-tab>
    </v-tabs>

    <!-- Tab Contents -->
    <v-tabs-items v-model="tab">
      <router-view />
    </v-tabs-items>
    <StaffCreateAccountModal ref="staffCreateAccountDialog" />
  </v-container>
</template>

<script lang="ts">
import { Pages, Role } from '@/util/constants'
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import StaffCreateAccountModal from '@/components/auth/staff/account-management/StaffCreateAccountModal.vue'
import { useCodesStore } from '@/stores/codes'
import { useStaffStore } from '@/stores/staff'
import { useTaskStore } from '@/stores/task'
import { useUserStore } from '@/stores/user'

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

    const state = reactive({
      tab: 0,
      pagesEnum: Pages,
      canManageAccounts: computed(() => currentUser?.roles?.includes(Role.StaffManageAccounts) ||
      currentUser?.roles?.includes(Role.ContactCentreStaff)),
      canViewInvitations: computed(() => currentUser?.roles?.includes(Role.StaffCreateAccounts) ||
        currentUser?.roles?.includes(Role.ContactCentreStaff)),
      canCreateAccounts: computed(() => currentUser?.roles?.includes(Role.StaffCreateAccounts) &&
      !currentUser?.roles?.includes(Role.ContactCentreStaff)),
      canViewAccounts: computed(() => currentUser?.roles?.includes(Role.StaffViewAccounts)),
      canSuspendAccounts: computed(() => currentUser?.roles?.includes(Role.StaffSuspendAccounts) ||
        currentUser?.roles?.includes(Role.StaffViewAccounts))
    })

    onMounted(async () => {
      await getCodes()
      await syncTasks()
      await syncSuspendedStaffOrgs()
      if (state.canCreateAccounts) {
        await syncPendingInvitationOrgs()
      }
    })

    const tabs = reactive([
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
      },
      {
        id: 5,
        tabName: 'Inactive',
        code: TAB_CODE.Inactive
      }
    ])

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
      tabs,
      pendingInvitationsCount,
      pendingTasksCount,
      rejectedTasksCount,
      suspendedReviewCount
    }
  }
})
</script>
