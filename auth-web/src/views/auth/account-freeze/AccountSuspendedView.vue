<template>
  <v-container class="view-container">
    <v-row justify="center">
      <v-col
        cols="12"
        sm="6"
        class="text-center"
      >
        <v-icon
          size="40"
          data-test="icon-lock-suspend-account"
          color="error"
          class="mb-6"
        >
          mdi-alert-circle-outline
        </v-icon>
        <h1 data-test="header-account-suspend">
          Your Account is Suspended
        </h1>
        <div
          v-if="isAdmin"
          data-test="div-is-admin"
        >
          <p class="mt-8 mb-10">
            Your account is suspended. For more information, please contact the BC Online Partnership Office at:<br>
          </p>
          <p class="mt-1 mb-1">
            Email: <span class="text-underline">bconline@gov.bc.ca</span>
          </p>
          <p>Telephone: 1-800-663-6102</p>
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
import moment from 'moment'
import sanitizeHtml from 'sanitize-html'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountSuspendedView',
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
    const formatDate = CommonUtils.formatDisplayDate

    const state = reactive({
      invoices: [],
      suspendedDate: (currentOrganization.value?.suspendedOn) ? formatDate(moment(currentOrganization.value.suspendedOn)) : '',
      accountAdministratorEmail: {}
    })

    async function setAdminContact () {
      const adminContact = await getAccountAdministrator()
      state.accountAdministratorEmail = adminContact.user.contacts[0].email
    }

    const accountAdministratorEmail = computed(() => {
      return sanitizeHtml(state.accountAdministratorEmail)
    })

    onMounted(() => {
      setAdminContact()
    })

    return {
      ...toRefs(state),
      accountAdministratorEmail
    }
  }
})
</script>
<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.text-underline {
    text-decoration: underline;
}
</style>
