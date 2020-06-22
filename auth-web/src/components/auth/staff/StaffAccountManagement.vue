<template>
  <v-card class="mb-4 pa-3" flat>
    <v-card-title class="d-flex align-center">
      <h2>Account Management</h2>
      <v-btn
        v-if="isStaffAdmin"
        color="primary"
        class="font-weight-bold"
        @click="gotToCreateAccount"
      >
        <v-icon small class="mr-1">mdi-plus</v-icon>Create Account
      </v-btn>
    </v-card-title>
    <v-card-text>
      <!-- Tab Navigation -->
      <v-tabs grow
        class="mb-3"
        v-model="tab"
        @change="tabChange"
        background-color="transparent">
        <v-tab data-test="active-tab">Active</v-tab>
        <template v-if="isStaffAdminBCOL">
          <v-tab data-test="pending-review-tab">
            Pending Review
          </v-tab>
          <v-tab data-test="rejected-tab">Rejected</v-tab>
        </template>
      </v-tabs>

      <!-- Tab Contents -->
      <v-tabs-items v-model="tab">
        <v-tab-item>
          <StaffActiveAccountsTable
            :columnSort="customSort"
          />
        </v-tab-item>
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
      </v-tabs-items>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Pages, Role } from '@/util/constants'
import { mapActions, mapState } from 'vuex'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Organization } from '@/models/Organization'
import StaffActiveAccountsTable from '@/components/auth/staff/StaffActiveAccountsTable.vue'
import StaffModule from '@/store/modules/staff'
import StaffPendingAccountsTable from '@/components/auth/staff/StaffPendingAccountsTable.vue'
import StaffRejectedAccountsTable from '@/components/auth/staff/StaffRejectedAccountsTable.vue'
import { getModule } from 'vuex-module-decorators'

enum TAB_CODE {
    Active = 'active-tab',
    PendingReview = 'pending-review-tab',
    Rejected = 'rejected-tab'
}

@Component({
  components: {
    StaffActiveAccountsTable,
    StaffPendingAccountsTable,
    StaffRejectedAccountsTable
  },
  methods: {
    ...mapActions('staff', [
      'syncActiveStaffOrgs',
      'syncPendingStaffOrgs',
      'syncRejectedStaffOrgs'
    ])
  },
  computed: {
    ...mapState('user', ['currentUser'])
  }
})
export default class StaffAccountManagement extends Vue {
  private staffStore = getModule(StaffModule, this.$store)
  private tab = 0
  private readonly currentUser!: KCUserProfile
  private readonly syncActiveStaffOrgs!: () => Organization[]
  private readonly syncPendingStaffOrgs!: () => Organization[]
  private readonly syncRejectedStaffOrgs!: () => Organization[]

  private tabs = [
    {
      id: 0,
      tabName: 'Active',
      code: TAB_CODE.Active
    },
    {
      id: 1,
      tabName: 'Pending Review',
      code: TAB_CODE.PendingReview
    },
    {
      id: 2,
      tabName: 'Rejected',
      code: TAB_CODE.Rejected
    }
  ]

  private async mounted () {
    await this.syncActiveStaffOrgs()
  }

  gotToCreateAccount () {
    this.$router.push({ path: `/${Pages.STAFF_SETUP_ACCOUNT}` })
  }

  private get isStaffAdmin () {
    return this.currentUser?.roles?.includes(Role.StaffAdmin)
  }

  private get isStaffAdminBCOL () {
    return this.currentUser?.roles?.includes(Role.StaffAdminBCOL)
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
      case TAB_CODE.Active:
        await this.syncActiveStaffOrgs()
        break
      case TAB_CODE.PendingReview:
        await this.syncPendingStaffOrgs()
        break
      case TAB_CODE.Rejected:
        await this.syncRejectedStaffOrgs()
        break
    }
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
</style>
