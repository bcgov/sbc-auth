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
      <v-tabs class="mb-3" v-model="tab" background-color="transparent">
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

  private async mounted () {
    await this.syncActiveStaffOrgs()
    await this.syncPendingStaffOrgs()
    await this.syncRejectedStaffOrgs()
  }

  gotToCreateAccount () {
    this.$router.push({ path: `/${Pages.STAFF_SETUP_ACCOUNT}` })
  }

  private get isStaffAdmin () {
    return this.currentUser?.roles?.includes(Role.StaffAdmin)
  }

  private get isStaffAdminBCOL () {
    // TODO remove this negation
    return !this.currentUser?.roles?.includes(Role.StaffAdminBCOL)
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
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
</style>
