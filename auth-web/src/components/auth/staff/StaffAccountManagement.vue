<template>
  <v-container class="pa-0">
    <header class="view-header align-center justify-space-between mt-n1 mb-4">
      <h2 class="view-header__title">Account Management</h2>
      <div class="view-header__actions">
        <v-btn large
          color="primary"
          class="font-weight-bold"
          v-if="canCreateAccounts"
          @click="gotToCreateAccount"
        >
          <v-icon small class="mr-1">mdi-plus</v-icon>Create Account
        </v-btn>
      </div>
    </header>
    <!-- Tab Navigation -->
    <v-tabs
      background-color="transparent"
      class="mb-9"
      v-model="tab"
      @change="tabChange">
      <v-tab data-test="active-tab"
        v-if="canViewAccounts">Active</v-tab>

      <template v-if="canCreateAccounts">
        <v-tab data-test="invitations-tab">
          <v-badge
            inline
            color="primary"
            :content="pendingInvitationsCount"
            :value="pendingInvitationsCount">
            Invitations
          </v-badge>
        </v-tab>
      </template>

      <template v-if="canManageAccounts">
        <v-tab data-test="pending-review-tab">
          <v-badge
            inline
            color="primary"
            :content="pendingReviewCount"
            :value="pendingReviewCount">
            Pending Review
          </v-badge>
        </v-tab>
        <v-tab data-test="rejected-tab">
          <v-badge
            inline
            color="primary"
            :content="rejectedReviewCount"
            :value="rejectedReviewCount">
            Rejected
          </v-badge>
        </v-tab>
      </template>
    </v-tabs>

    <!-- Tab Contents -->
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <StaffActiveAccountsTable
          :columnSort="customSort"
        />
      </v-tab-item>
      <v-tab-item v-if="canCreateAccounts">
        <StaffPendingAccountInvitationsTable
          :columnSort="customSort"
        />
      </v-tab-item>
      <template v-if="canManageAccounts">
        <v-tab-item>
          <StaffPendingAccountsTable
            :columnSort="customSort"
          />
        </v-tab-item>
        <v-tab-item>
          <StaffRejectedAccountsTable
            :columnSort="customSort"
          />
        </v-tab-item>
      </template>
    </v-tabs-items>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Pages, Role } from '@/util/constants'
import { mapActions, mapGetters, mapState } from 'vuex'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Organization } from '@/models/Organization'
import StaffActiveAccountsTable from '@/components/auth/staff/StaffActiveAccountsTable.vue'
import StaffModule from '@/store/modules/staff'
import StaffPendingAccountInvitationsTable from '@/components/auth/staff/StaffPendingAccountInvitationsTable.vue'
import StaffPendingAccountsTable from '@/components/auth/staff/StaffPendingAccountsTable.vue'
import StaffRejectedAccountsTable from '@/components/auth/staff/StaffRejectedAccountsTable.vue'
import { getModule } from 'vuex-module-decorators'

enum TAB_CODE {
    Active = 'active-tab',
    PendingReview = 'pending-review-tab',
    Rejected = 'rejected-tab',
    Invitations = 'invitations-tab'
}

@Component({
  components: {
    StaffActiveAccountsTable,
    StaffPendingAccountsTable,
    StaffRejectedAccountsTable,
    StaffPendingAccountInvitationsTable
  },
  methods: {
    ...mapActions('staff', [
      'syncPendingStaffOrgs',
      'syncRejectedStaffOrgs',
      'syncPendingInvitationOrgs'
    ])
  },
  computed: {
    ...mapState('user', ['currentUser']),
    ...mapGetters('staff', [
      'pendingReviewCount',
      'rejectedReviewCount',
      'pendingInvitationsCount'
    ])
  }
})
export default class StaffAccountManagement extends Vue {
  private staffStore = getModule(StaffModule, this.$store)
  private tab = 0
  private readonly currentUser!: KCUserProfile
  private readonly syncPendingStaffOrgs!: () => Organization[]
  private readonly syncRejectedStaffOrgs!: () => Organization[]
  private readonly syncPendingInvitationOrgs!: () => Organization[]

  private readonly pendingReviewCount!: number
  private readonly rejectedReviewCount!: number
  private readonly pendingInvitationsCount!: number

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
    }
  ]

  private async mounted () {
    await this.syncPendingStaffOrgs()
    await this.syncRejectedStaffOrgs()
    await this.syncPendingInvitationOrgs()
  }

  gotToCreateAccount () {
    this.$router.push({ path: `/${Pages.STAFF_SETUP_ACCOUNT}` })
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

  private customSort (items, index, isDescending) {
    const isDesc = isDescending.length > 0 && isDescending[0]
    items.sort((a, b) => {
      if (isDesc) {
        return a[index[0]] < b[index[0]] ? -1 : 1
      } else {
        return b[index[0]] < a[index[0]] ? -1 : 1
      }
    })
    return items
  }

  private async tabChange (tabIndex) {
    const selected = this.tabs.filter((tab) => (tab.id === tabIndex))
    switch (selected[0]?.code) {
      case TAB_CODE.PendingReview:
        await this.syncPendingStaffOrgs()
        break
      case TAB_CODE.Rejected:
        await this.syncRejectedStaffOrgs()
        break
      case TAB_CODE.Invitations:
        await this.syncPendingInvitationOrgs()
        break
      default:
        break
    }
  }
}
</script>

<style lang="scss" scoped>
</style>
