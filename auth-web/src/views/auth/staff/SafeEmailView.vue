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
import { defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { SafeEmail } from '@/models/safe-email'
import StaffService from '@/services/staff.services'

export default defineComponent({
  name: 'SafeEmailView',
  setup () {
    const state = reactive({
      safeEmails: [] as SafeEmail[],
      alertMessage: '',
      alertType: '',
      deletedEmail: '',
      delEmailAlertMsg: '',
      delEmailAlertType: ''
    })

    function showGeneralAlert (msg: string, type: string) {
      state.alertMessage = msg
      state.alertType = type
      // 2 seconds timeout
      setTimeout(() => {
        state.alertMessage = ''
      }, 2000)
    }

    function showPerEmailAlert (email: string, type: string) {
      state.deletedEmail = email
      state.delEmailAlertType = type
      state.delEmailAlertMsg = type === 'success' ? 'Deleted' : 'Error'
      // 1 seconds timeout
      setTimeout(() => {
        state.deletedEmail = ''
      }, 1000)
    }

    async function getSafeEmails () {
      try {
        state.safeEmails = (await StaffService.getSafeEmails()).data
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
      ...toRefs(state),
      deleteEmail,
      getSafeEmails,
      showGeneralAlert
    }
  }
})
</script>
