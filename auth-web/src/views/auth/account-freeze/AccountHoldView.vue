<template>
  <v-container class="view-container">
    <v-row
      justify="center"
    >
      <v-col
        cols="12"
        sm="6"
        class="text-center"
      >
        <v-icon
          size="40"
          data-test="icon-lock-suspend-account"
          color="primary"
          class="mb-6"
        >
          mdi-clock-outline
        </v-icon>
        <h1 data-test="header-account-suspend">
          Your Account is Temporarily on Hold
        </h1>
        <div
          v-if="isAdmin"
          data-test="div-is-admin"
        >
          <p class="mt-8 mb-10">
            Your account is on hold until payment is received.
            Once your payment is processed, your account will be activated.
            We will send a notification email when your account is activated.<br>
          </p>
          <p class="mt-1 font-weight-bold">
            Overdue Statements
          </p>
          <p
            v-for="statement in statements"
            :key="statement.id"
            class="mb-2 link"
          >
            <a
              class="text-decoration-underline"
              @click="downloadStatement(statement)"
            >
              {{ formatDateRange(statement.fromDate, statement.toDate) }}
            </a>
          </p>
        </div>
        <div
          v-else
          data-test="div-is-user"
        >
          <p class="mt-4">
            Your account is suspended from: <span class="font-weight-bold">{{ suspendedDate }}</span>
          </p>
          <p class="mt-4">
            Please contact the account administrator to reactivate your account.
          </p>
          <p class="mt-4 mb-10">
            Account Administrator Email: <a :href="'mailto:' + accountAdministratorEmail">{{ accountAdministratorEmail }}</a>
          </p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { FailedInvoice } from '@/models/invoice'
import moment from 'moment'
import sanitizeHtml from 'sanitize-html'
import { useDownloader } from '@/composables/downloader'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountHoldView',
  props: {
    isAdmin: {
      type: Boolean,
      default: false
    }
  },
  setup () {
    const orgStore = useOrgStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)
    const getAccountAdministrator = orgStore.getAccountAdministrator
    const calculateFailedInvoices: any = orgStore.calculateFailedInvoices
    const formatDate = CommonUtils.formatDisplayDate
    const formatDateRange = CommonUtils.formatDateRange

    const state = reactive({
      loading: false, //  unused, but still used in our downloader.
      statements: [],
      suspendedDate: (currentOrganization.value?.suspendedOn) ? formatDate(moment(currentOrganization.value.suspendedOn)) : '',
      accountAdministratorEmail: ''
    })
    const { downloadStatement } = useDownloader(orgStore, state)

    async function setAdminContact () {
      const adminContact = await getAccountAdministrator()
      state.accountAdministratorEmail = adminContact.user.contacts[0].email
    }

    const accountAdministratorEmail = computed(() => {
      return sanitizeHtml(state.accountAdministratorEmail)
    })

    onMounted(async () => {
      await setAdminContact()
      const failedInvoices: FailedInvoice = await calculateFailedInvoices()
      state.statements = failedInvoices?.statements || []
    })

    return {
      ...toRefs(state),
      formatDateRange,
      accountAdministratorEmail,
      downloadStatement
    }
  }
})
</script>
<style lang="scss" scoped>
.link {
    color: var(--v-primary-base) !important;
    text-decoration: underline;
    cursor: pointer;
}
.text-underline {
    text-decoration: underline;
}
</style>
