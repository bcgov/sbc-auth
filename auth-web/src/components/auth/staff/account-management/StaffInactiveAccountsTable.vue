<template>
  <StaffAccountsTable :accountStatus="accountStatus" />
</template>

<script lang="ts">
import { AccountStatus } from '@/util/constants'
import StaffAccountsTable from '@/components/auth/common/StaffAccountsTable.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'StaffInactiveAccountsTable',
  components: {
    StaffAccountsTable
  },
  data () {
    return {
      accountStatus: AccountStatus.INACTIVE as AccountStatus
    }
  }
})
</script>
