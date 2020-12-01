import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-1">Account has been suspended for outstanding balance.</p>
    <p class="mb-4">To unlock your account please complete the following steps</p>
    <v-row class="mb-12 pb-12">
      <v-col md="9">
        <v-card
          outlined
          flat
          class="suspended-info-card"
        >
          <v-card-text>
            <v-row class="suspended-row">
              <v-col class="pt-0">Suspended from</v-col>
              <v-col class="card-value-right">{{suspendedDate}}</v-col>
            </v-row>
            <v-divider class="divider-card"></v-divider>
            <v-row>
              <v-col md="9" class="pt-0">
                <div>Dishonored Bank Instrument Fee</div>
                <div class="sub-txt">As per PAD terms, you are charged $30 dishonored bank fee for every failed payment</div>
              </v-col>
              <v-col class="card-value-right">${{nsfFee.toFixed(2)}}</v-col>
            </v-row>
            <v-row class="pb-3">
              <v-col class="pt-0">Total Transactions</v-col>
              <v-col class="card-value-right">${{totalTransactionAmount.toFixed(2)}}</v-col>
            </v-row>
            <v-divider class="divider-card"></v-divider>
            <v-row class="font-weight-bold">
              <v-col class="pt-0 pb-2">Total Amount Due</v-col>
              <v-col class="pb-2 card-value-right">${{totalAmountToPay.toFixed(2)}}</v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-divider></v-divider>
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          text
          link
          color="primary"
          class="download-pdf-btn"
          @click="downloadTransactionPDF"
        >
          Download transaction invoice in PDF
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
  .v-card__text {
    color: #000 !important;
  }
  .sub-txt {
    font-style: italic;
    font-size: .75rem;
  }
  .card-value-right {
    text-align: right;
    padding-top: 0px;
  }
  .divider-card {
    border: 1px solid rgb(0, 0, 0, 42%);
    margin-bottom: 16px;
  }
}

.download-pdf-btn {
  padding: 8px 0px !important;
  text-decoration: underline;
}
</style>
