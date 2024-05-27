<template>
  <div>
    <p class="mb-10 red--text">
      <v-icon
        color="red"
        class="pr-1"
        small
      >
        mdi-alert
      </v-icon>
      You have overdue payments for your account. Please settle outstanding payments to reactivate your account.
    </p>

    <v-card
      outlined
      flat
      class="suspended-info-card mb-12"
    >
      <v-card-text class="py-2 px-6">
        <v-row>
          <v-col cols="9">
            Suspended from
          </v-col>
          <v-col class="text-end">
            {{ suspendedDate }}
          </v-col>
        </v-row>
        <v-divider class="my-2" />
        <v-row>
          <v-col cols="9">
            <div>Overdue statements</div>
          </v-col>
        </v-row>
        <v-row
          v-for="invoice in invoices"
          :key="invoice.id"
        >
          <v-col class="pt-0">
            <div class="link">
              {{ formatDateRange(invoice.fromDate, invoice.toDate) }}
            </div>
          </v-col>
        </v-row>
        <v-divider class="my-2" />
        <v-row class="font-weight-bold">
          <v-col cols="9">
            Total Amount Due
          </v-col>
          <v-col class="text-end">
            ${{ totalAmountDue.toFixed(2) }}
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-divider />
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-spacer />
        <v-btn
          large
          color="primary"
          @click="goNext"
        >
          <span>Next</span>
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { FailedEFTInvoice } from '@/models/invoice'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountOverviewNSFView',
  emits: ['step-forward'],
  setup (_, { emit }) {
    const orgStore = useOrgStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)
    const currentMembership = computed(() => orgStore.currentMembership)
    const calculateFailedInvoices: any = orgStore.calculateFailedEFTInvoices
    const downloadNSFInvoicesPDF: any = orgStore.downloadNSFInvoicesPDF
    const formatDate = CommonUtils.formatDisplayDate
    const formatDateRange = CommonUtils.formatDateRange
    const suspendedDate = (currentOrganization.value?.suspendedOn) ? formatDate(new Date(currentOrganization.value.suspendedOn)) : ''

    const state = reactive({
      invoices: [],
      totalAmountDue: 0
    })

    const goNext = () => {
      emit('step-forward')
    }

    onMounted(async () => {
      const failedInvoices: FailedEFTInvoice = await calculateFailedInvoices()
      state.invoices = failedInvoices?.invoices || []
      state.totalAmountDue = failedInvoices?.totalAmountDue || 0
    })

    return {
      ...toRefs(state),
      currentOrganization,
      currentMembership,
      suspendedDate,
      downloadNSFInvoicesPDF,
      goNext,
      formatDateRange
    }
  }
})

</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

.link {
  color: var(--v-primary-base) !important;
  text-decoration: underline;
  cursor: pointer;
}

.suspended-info-card {
  border-color: $BCgovInputError !important;
  border-width: 2px !important;

  .sub-txt {
    font-size: .75rem;
  }
}
</style>
