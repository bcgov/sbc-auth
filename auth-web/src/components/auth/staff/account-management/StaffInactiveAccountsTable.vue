<template>
  <StaffAccountsTable
    :accountStatus="accountStatus"
    :sessionStorageKey="sessionStorageKey"
    :paginationNumberOfItemsKey="paginationNumberOfItemsKey"
    :paginationOptionsKey="paginationOptionsKey"
  />
</template>

<script lang="ts">
import { AccountStatus, SessionStorageKeys } from '@/util/constants'
import StaffAccountsTable from '@/components/auth/common/StaffAccountsTable.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'StaffInactiveAccountsTable',
  components: {
    StaffAccountsTable
  },
  data () {
    return {
      accountStatus: AccountStatus.INACTIVE as AccountStatus,
      sessionStorageKey: SessionStorageKeys.InactiveSearchFilter,
      paginationNumberOfItemsKey: SessionStorageKeys.InactivePaginationNumberOfItems,
      paginationOptionsKey: SessionStorageKeys.InactivePaginationOptions,
    }
  }
})
</script>
