<template>
  <div class="dashboard-view">
    <article>
      <router-view />
    </article>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import EntityManagement from '@/components/auth/manage-business/EntityManagement.vue'
import TeamManagement from '@/components/auth/account-settings/team-management/TeamManagement.vue'

  @Component({
    name: 'Dashboard',
    components: {
      EntityManagement,
      TeamManagement
    }
  })
export default class DashboardView extends Vue {}
</script>
