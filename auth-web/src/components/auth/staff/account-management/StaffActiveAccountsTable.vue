<template>
  <StaffAccountsTable :accountStatus="accountStatus" :sessionStorageKeys="sessionStorageKeys" />
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
      sessionStorageKeys: SessionStorageKeys.OrgSearchFilter
    }
  }
})
</script>
