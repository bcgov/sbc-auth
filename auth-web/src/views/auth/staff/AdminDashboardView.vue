<template>
  <v-container id="admin-dashboard-container" class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">Admin Dashboard</h1>
    </div>

    <v-row no-gutters>
      <v-col cols="8">
        <AdministrativeBN />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import AdministrativeBN from '@/components/auth/staff/admin/AdministrativeBN.vue'
import { Component } from 'vue-property-decorator'
import Vue from 'vue'

@Component({
  components: {
    AdministrativeBN
  }
})
export default class AdminDashboardView extends Vue {}
</script>
