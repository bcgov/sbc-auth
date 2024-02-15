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
import { computed, defineComponent } from '@vue/composition-api'
import AdministrativeBN from '@/components/auth/staff/admin/AdministrativeBN.vue'
import { Role } from '@/util/constants'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'AdminDashboardView',
  components: {
    AdministrativeBN
  },
  setup () {
    const userStore = useUserStore()

    const canEditBn = computed(() => {
      return userStore.currentUser.roles.includes(Role.BnEdit) || userStore.currentUser.roles.includes(Role.AdminEdit)
    })

    return {
      canEditBn
    }
  }
})
</script>
