<template>
    <v-simple-table>
    <thead>
      <tr>
        <th class="text-left">
          Id
        </th>
        <th class="text-left">
          Email
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-for="item in safeEmails"
        :key="item.email"
      >
        <td>{{ item.id }}</td>
        <td>{{ item.email }}</td>
      </tr>
    </tbody>
    </v-simple-table>
</template>
<script lang="ts">
import { defineComponent, onMounted, ref } from '@vue/composition-api'
import { SafeEmail } from '@/models/safe-email'
import StaffService from '@/services/staff.services'

export default defineComponent({
  name: 'SafeEmailView',
  setup () {
    const getSafeEmails = async () => {
      const response = await StaffService.getSafeEmails()
      if (response && response.data && response.status === 200) {
        return response.data
      }
    }
    const safeEmails = ref<SafeEmail[]>()

    onMounted(async () => {
      safeEmails.value = await getSafeEmails()
    })

    return {
      safeEmails
    }
  }
})
</script>
