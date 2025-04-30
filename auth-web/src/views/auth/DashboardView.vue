<template>
  <div class="dashboard-view">
    <article>
      <router-view />
    </article>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import TeamManagement from '@/components/auth/account-settings/team-management/TeamManagement.vue'

  @Component({
    name: 'Dashboard',
    components: {
      TeamManagement
    }
  })
export default class DashboardView extends Vue {}
</script>
