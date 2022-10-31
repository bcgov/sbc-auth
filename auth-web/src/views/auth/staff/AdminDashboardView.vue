<template>
  <v-container id="admin-dashboard-container" class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">Admin Dashboard</h1>
    </div>

    <v-row no-gutters v-if="canEditBn">
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
import Vue from 'vue'

import { namespace } from 'vuex-class'

const userModule = namespace('user')

@Component({
  components: {
    AdministrativeBN
  }
})
export default class AdminDashboardView extends Vue {
  @userModule.State('currentUser') public currentUser!: KCUserProfile

  private get canEditBn (): boolean {
    return this.currentUser.roles.includes(Role.BnEdit) || this.currentUser.roles.includes(Role.AdminEdit)
  }
}
</script>
