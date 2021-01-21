<template>
<v-card flat class="" color="error">
  <v-alert :icon="false" prominent type="error" class="mb-0">
    <v-row>
      <v-col cols="9">
        <div class="banner-info">
          <v-icon color="link" left x-large>mdi-information-outline</v-icon>
          <div class="ml-4">
            <div class="font-weight-bold">Account Suspended</div>
            <div>Account has been suspended for outstanding balance (NSF).</div>
          </div>
        </div>
      </v-col>
      <v-col class="text-end">{{suspendedDate}}</v-col>
    </v-row>
    <v-row>
      <v-col cols="9" class="font-weight-bold balance">BALANCE DUE: $64.50</v-col>
    </v-row>
  </v-alert>
</v-card>
</template>

<script lang="ts">
import { Address, BaseAddressModel } from '@/models/address'
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { InvoiceList } from '@/models/invoice'
import { Organization } from '@/models/Organization'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component
export default class AccountSuspendAlert extends Vue {
  @OrgModule.Action('getFailedInvoices') private getFailedInvoices!: () => InvoiceList[]
  @OrgModule.State('currentOrganization') private currentOrganization!: Organization
  private formatDate = CommonUtils.formatDisplayDate
  private nsfFee: number = 0
  private nsfCount: number = 0
  private totalTransactionAmount: number = 0
  private totalAmountToPay: number = 0
  private totalPaidAmount: number = 0

  private get suspendedDate () {
    return (this.currentOrganization?.suspendedOn) ? this.formatDate(new Date(this.currentOrganization.suspendedOn)) : ''
  }

  async mounted () {
    const failedInvoices: InvoiceList[] = await this.getFailedInvoices()
    failedInvoices.forEach((failedInvoice) => {
      this.totalPaidAmount += failedInvoice?.paidAmount
      this.totalAmountToPay += failedInvoice?.invoices?.map(el => el.total).reduce((accumulator, invoiceTotal) => accumulator + invoiceTotal)
      failedInvoice?.invoices?.forEach((invoice) => {
        const nsfItems = invoice?.lineItems?.filter(lineItem => (lineItem.description === 'NSF'))
          .map(el => el.total)
        this.nsfCount += nsfItems.length
        this.nsfFee += (nsfItems.length) ? nsfItems?.reduce((accumulator, currentValue) => accumulator + currentValue) : 0
      })
    })

    this.totalTransactionAmount = this.totalAmountToPay - this.nsfFee
    this.totalAmountToPay = this.totalAmountToPay - this.totalPaidAmount
  }
}
</script>

<style lang="scss" scoped>
.banner{
  width: 100%;
  display: flex;
  justify-content: space-between;

}
 .banner-info{
    display: flex
  }
.balance{
    margin-left: 63px;
    font-size: 1.25rem;
  }
</style>
