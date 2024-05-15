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
          color="primary"
          class="mb-6"
        >
          mdi-clock-outline
        </v-icon>
        <h1 data-test="header-account-suspend">
          Your account is temporarily on hold
        </h1>
        <!-- should be isAdmin -->
        <div
          v-if="!isAdmin"
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
            v-for="invoice in invoices"
            :key="invoice.id"
            class="mb-2 link"
          >
            April 1 - 30, 2024
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
            Please contact the account administrator to reactive your account.
          </p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { FailedEFTInvoice } from '@/models/invoice'
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
    const calculateFailedInvoices: any = orgStore.calculateFailedEFTInvoices
    const formatDate = CommonUtils.formatDisplayDate
    const suspendedDate = (currentOrganization.value?.suspendedOn) ? formatDate(new Date(currentOrganization.value.suspendedOn)) : ''
    const state = reactive({
      invoices: []
    })

    onMounted(async () => {
      const failedInvoices: FailedEFTInvoice = await calculateFailedInvoices()
      state.invoices = failedInvoices?.invoices || []
    })

    return {
      ...toRefs(state),
      suspendedDate
    }
  }
})
</script>
<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.link {
    color: var(--v-primary-base) !important;
    text-decoration: underline;
    cursor: pointer;
}
.text-underline {
    text-decoration: underline;
}
</style>
