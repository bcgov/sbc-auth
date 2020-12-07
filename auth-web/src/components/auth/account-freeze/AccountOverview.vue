import { AccessType } from '@/util/constants'
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
          <v-col cols="9">Suspended from</v-col>
          <v-col class="text-end">{{suspendedDate}}</v-col>
        </v-row>
        <v-divider class="my-2"></v-divider>
        <v-row>
          <v-col cols="9">
            <div>Dishonored Bank Instrument Fee</div>
            <div class="font-italic">As per PAD terms, you are charged $30 dishonored bank fee for every failed payment</div>
          </v-col>
          <v-col class="text-end">${{nsfFee.toFixed(2)}}</v-col>
        </v-row>
        <v-row>
          <v-col cols="9">Total Transactions</v-col>
          <v-col class="text-end">${{totalTransactionAmount.toFixed(2)}}</v-col>
        </v-row>
        <v-divider class="my-2"></v-divider>
        <v-row class="font-weight-bold">
          <v-col cols="9">Total Amount Due</v-col>
          <v-col class="text-end">${{totalAmountToPay.toFixed(2)}}</v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <v-divider></v-divider>
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          text
          color="primary"
          @click="downloadTransactionPDF"
        >
          <v-icon class="ml-n2">mdi-download</v-icon>
          <span>Download Transaction Invoice (PDF)</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          @click="goNext"
        >
          <span>Next</span>
          <v-icon class="ml-2">mdi-arrow-right</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import { InvoiceList } from '@/models/invoice'
import { Organization } from '@/models/Organization'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions('org', [
      'getFailedInvoices'
    ])
  }
})
export default class AccountOverview extends Mixins(Steppable) {
  private readonly currentOrganization!: Organization
  private readonly getFailedInvoices!: () => InvoiceList[]
  private formatDate = CommonUtils.formatDisplayDate
  private nsfFee: number = 0
  private nsfCount: number = 0
  private totalTransactionAmount: number = 0
  private totalAmountToPay: number = 0

  private goNext () {
    this.stepForward()
  }

  private get suspendedDate () {
    return (this.currentOrganization?.suspendedOn) ? this.formatDate(new Date(this.currentOrganization.suspendedOn)) : ''
  }

  private downloadTransactionPDF () {
    // download PDF
  }

  async mounted () {
    const failedInvoices: InvoiceList[] = await this.getFailedInvoices()

    failedInvoices.forEach((failedInvoice) => {
      this.totalAmountToPay += failedInvoice?.invoices?.map(el => el.total).reduce((accumulator, invoiceTotal) => accumulator + invoiceTotal)
      failedInvoice?.invoices?.forEach((invoice) => {
        const nsfItems = invoice?.lineItems?.filter(lineItem => (lineItem.description === 'NSF'))
          .map(el => el.total)
        this.nsfCount += nsfItems.length
        this.nsfFee += (nsfItems.length) ? nsfItems?.reduce((accumulator, currentValue) => accumulator + currentValue) : 0
      })
    })

    this.totalTransactionAmount = this.totalAmountToPay - this.nsfFee
  }
}
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
