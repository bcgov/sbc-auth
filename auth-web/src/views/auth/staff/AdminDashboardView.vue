<template>
  <v-container
    id="admin-dashboard-container"
    class="view-container"
  >
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Admin Dashboard
      </h1>
    </div>

    <v-row
      v-if="canEditBn"
      no-gutters
    >
      <v-col cols="8">
        <AdministrativeBN />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import AdministrativeBN from '@/components/auth/staff/admin/AdministrativeBN.vue'
import { Component } from 'vue-property-decorator'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Role } from '@/util/constants'
import { State } from 'pinia-class'
import Vue from 'vue'
import { useUserStore } from '@/stores/user'

@Component({
  components: {
    AdministrativeBN
  }
})
export default class AdminDashboardView extends Vue {
  @State(useUserStore) currentUser!: KCUserProfile

  get canEditBn (): boolean {
    return this.currentUser.roles.includes(Role.BnEdit) || this.currentUser.roles.includes(Role.AdminEdit)
  }
}
</script>
