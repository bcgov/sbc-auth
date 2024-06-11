<template>
  <StaffAccountsTable :accountStatus="accountStatus" />
</template>

<script lang="ts">
import { AccountStatus } from '@/util/constants'
import StaffAccountsTable from '@/components/auth/common/StaffAccountsTable.vue'
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
  name: 'StaffActiveAccountsTable',
  components: {
    StaffAccountsTable
  },
  data () {
    return {
      accountStatus: AccountStatus.ACTIVE as AccountStatus
    }
  }
})
</script>
