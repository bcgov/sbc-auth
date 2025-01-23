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
      :loading="loading"
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
          v-for="statement in statements"
          :key="statement.id"
        >
          <v-col class="pt-0">
            <a
              class="text-decoration-underline"
              @click="downloadStatement(statement)"
            >
              {{ formatDateRange(statement.fromDate, statement.toDate) }}
            </a>
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
import { FailedInvoice } from '@/models/invoice'
import { useDownloader } from '@/composables/downloader'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountOverviewNSFView',
  emits: ['step-forward'],
  setup (_, { emit }) {
    const orgStore = useOrgStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)
    const currentMembership = computed(() => orgStore.currentMembership)
    const calculateFailedInvoices: any = orgStore.calculateFailedInvoices
    const downloadNSFInvoicesPDF: any = orgStore.downloadNSFInvoicesPDF
    const formatDate = CommonUtils.formatDisplayDate
    const formatDateRange = CommonUtils.formatDateRange
    const suspendedDate = (currentOrganization.value?.suspendedOn) ? formatDate(new Date(currentOrganization.value.suspendedOn)) : ''
    const state = reactive({
      statements: [],
      totalAmountDue: 0,
      loading: false
    })
    const { downloadStatement } = useDownloader(orgStore, state)

    const goNext = () => {
      emit('step-forward')
    }

    onMounted(async () => {
      const failedInvoices: FailedInvoice = await calculateFailedInvoices()
      state.statements = failedInvoices?.statements || []
      state.totalAmountDue = failedInvoices?.totalAmountToPay || 0
    })

    return {
      ...toRefs(state),
      currentOrganization,
      currentMembership,
      downloadStatement,
      suspendedDate,
      downloadNSFInvoicesPDF,
      goNext,
      formatDateRange
    }
  }
})

</script>

<style lang="scss" scoped>
.text-decoration-underline {
  text-decoration: underline;
}

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
