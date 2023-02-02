<template>
  <Transactions class="mt-5 pa-8" :extended="true" :showCredit="false" :showExport="false" />
</template>
<script lang="ts">
import { Transactions } from '@/components/auth/account-settings/transaction'
import { defineComponent } from '@vue/composition-api'
// if user is not allowed to see all transactions it will only show transactions for their account (handled within composable)
export default defineComponent({
  name: 'ViewAllTransactions',
  components: { Transactions }
})
</script>
