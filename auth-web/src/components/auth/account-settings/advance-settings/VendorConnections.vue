<template>
  <v-container class="vendor-connections-container">
    <div class="view-header flex-column mb-3">
      <h2
        class="view-header__title"
        data-test="vendor-connections-title"
      >
        {{ $t('vendorConnectionsTitle') }}
      </h2>
      <p class="mt-3 payment-page-sub">
        {{ $t('vendorConnectionsSubtitle') }}
      </p>
    </div>
    <VendorConnectionsTable />
  </v-container>
</template>

<script lang="ts">
import { defineComponent, onMounted } from '@vue/composition-api'
import { Pages } from '@/util/constants'
import VendorConnectionsTable from '@/components/auth/account-settings/advance-settings/VendorConnectionsTable.vue'
import { canAccessVendorConnections } from '@/util/vendor-connection-util'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'VendorConnections',
  components: {
    VendorConnectionsTable
  },
  setup (_, { root }) {
    const orgStore = useOrgStore()
    const userStore = useUserStore()

    onMounted(() => {
      if (!canAccessVendorConnections(
        orgStore.currentMembership?.membershipTypeCode,
        userStore.currentUser?.roles
      )) {
        root.$router.push(`/${Pages.MAIN}/${orgStore.currentOrganization?.id}/settings/account-info`)
      }
    })
  }
})
</script>

<style lang="scss" scoped>
.view-header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
</style>
