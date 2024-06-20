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
  name: 'StaffActiveAccountsTable',
  components: {
    StaffAccountsTable
  },
  data () {
    return {
      accountStatus: AccountStatus.ACTIVE as AccountStatus,
      sessionStorageKey: SessionStorageKeys.OrgSearchFilter,
      paginationNumberOfItemsKey: SessionStorageKeys.PaginationNumberOfItems,
      paginationOptionsKey: SessionStorageKeys.PaginationOptions,
    }
  }
})
</script>
