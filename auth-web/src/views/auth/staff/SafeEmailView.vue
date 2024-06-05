<template>
  <div>
    <v-alert
      v-if="alertMessage"
      :type="alertType"
      closable
    >
      {{ alertMessage }}
    </v-alert>
    <v-simple-table>
      <thead>
        <tr>
          <th
            scope="col"
            class="text-left"
          >
            Id
          </th>
          <th
            scope="col"
            class="text-left"
          >
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
          <td>
            <v-btn
              small
              @click="deleteEmail(item.email)"
            >
              Delete
            </v-btn>
          </td>
          <v-alert
            v-if="item.email === deletedEmail"
            :type="delEmailAlertType"
            closable
          >
            {{ delEmailAlertMsg }}
          </v-alert>
        </tr>
      </tbody>
    </v-simple-table>
  </div>
</template>
<script lang="ts">
import { defineComponent, onMounted, ref } from '@vue/composition-api'
import { SafeEmail } from '@/models/safe-email'
import StaffService from '@/services/staff.services'

export default defineComponent({
  name: 'SafeEmailView',
  setup () {
    const safeEmails = ref<SafeEmail[]>()
    const alertMessage = ref('')
    const alertType = ref('')
    const deletedEmail = ref('')
    const delEmailAlertMsg = ref('')
    const delEmailAlertType = ref('')

    function showGeneralAlert (msg: string, type: string) {
      alertMessage.value = msg
      alertType.value = type
      // 2 seconds timeout
      setTimeout(() => {
        alertMessage.value = ''
      }, 2000)
    }

    function showPerEmailAlert (email: string, type: string) {
      deletedEmail.value = email
      delEmailAlertType.value = type
      if (type === 'success') {
        delEmailAlertMsg.value = `Deleted`
      } else {
        delEmailAlertMsg.value = `Error`
      }
      // 1 seconds timeout
      setTimeout(() => {
        deletedEmail.value = ''
      }, 1000)
    }

    async function getSafeEmails () {
      try {
        safeEmails.value = (await StaffService.getSafeEmails()).data
      } catch (error) {
        showGeneralAlert(`Error fetching safe emails, ${error}`, 'error')
      }
    }

    async function deleteEmail (email: string) {
      // Call the service method to delete the email from the server
      try {
        await StaffService.deleteSafeEmail(email)
        showPerEmailAlert(email, 'success')
        await getSafeEmails()
      } catch (error) {
        showPerEmailAlert(email, 'error')
        showGeneralAlert(`Error deleting ${email}, ${error}`, 'error')
      }
    }

    onMounted(async () => {
      await getSafeEmails()
    })

    return {
      deleteEmail,
      getSafeEmails,
      showGeneralAlert,
      safeEmails,
      alertMessage,
      alertType,
      deletedEmail,
      delEmailAlertMsg,
      delEmailAlertType
    }
  }
})
</script>
