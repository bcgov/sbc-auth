<template>
  <div>
    <p class="mb-10">
      This account has been suspended for a failed payment.
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
            <div>Dishonored Bank Instrument Fee</div>
            <div class="font-italic">
              As per PAD terms, you are charged $30 dishonored bank fee for every failed payment
            </div>
          </v-col>
          <v-col class="text-end">
            ${{ nsfFee.toFixed(2) }}
          </v-col>
        </v-row>
        <v-row>
          <v-col cols="9">
            Total Transactions
          </v-col>
          <v-col class="text-end">
            ${{ totalTransactionAmount.toFixed(2) }}
          </v-col>
        </v-row>
        <v-divider class="my-2" />
        <v-row class="font-weight-bold">
          <v-col cols="9">
            Total Amount Due
          </v-col>
          <v-col class="text-end">
            ${{ totalAmountToPay.toFixed(2) }}
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
        <v-btn
          large
          text
          color="primary"
          @click="downloadNSFInvoicesPDF"
        >
          <v-icon class="ml-n2">
            mdi-download
          </v-icon>
          <span>Download Transaction Invoice (PDF)</span>
        </v-btn>
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
import { Member, Organization } from '@/models/Organization'
import { defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import CommonUtils from '@/util/common-util'
import { FailedInvoice } from '@/models/invoice'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountOverviewView',
  emits: ['step-forward'],
  setup (_, { emit }) {
    const orgStore = useOrgStore()
    const currentOrganization: Organization = orgStore.currentOrganization
    const currentMembership: Member = orgStore.currentMembership
    const calculateFailedInvoices: any = orgStore.calculateFailedInvoices
    const downloadNSFInvoicesPDF: any = orgStore.downloadNSFInvoicesPDF
    const formatDate = CommonUtils.formatDisplayDate
    const suspendedDate = (currentOrganization?.suspendedOn) ? formatDate(new Date(currentOrganization.suspendedOn)) : ''

    const state = reactive({
      nsfFee: 0,
      nsfCount: 0,
      totalTransactionAmount: 0,
      totalAmountToPay: 0,
      totalPaidAmount: 0
    })

    const goNext = () => {
      emit('step-forward')
    }

    onMounted(async () => {
      const failedInvoices: FailedInvoice = await calculateFailedInvoices()
      state.nsfCount = failedInvoices?.nsfCount || 0
      state.totalTransactionAmount = failedInvoices?.totalTransactionAmount || 0
      state.nsfFee = failedInvoices?.nsfFee || 0
      state.totalAmountToPay = failedInvoices?.totalAmountToPay || 0
    })

    return {
      ...toRefs(state),
      currentOrganization,
      currentMembership,
      suspendedDate,
      downloadNSFInvoicesPDF,
      goNext
    }
  }
})

</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";

.suspended-info-card {
  border-color: $BCgovInputError !important;
  border-width: 2px !important;

  .sub-txt {
    font-size: .75rem;
  }
}
</style>
