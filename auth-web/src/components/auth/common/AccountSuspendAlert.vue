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
      <v-col cols="9" class="font-weight-bold balance">BALANCE DUE:  ${{totalAmountToPay.toFixed(2)}}</v-col>
    </v-row>
  </v-alert>
</v-card>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import { FailedInvoice } from '@/models/invoice'
import { Organization } from '@/models/Organization'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')

@Component
export default class AccountSuspendAlert extends Vue {
  @OrgModule.Action('calculateFailedInvoices') private calculateFailedInvoices!: () => FailedInvoice
  @OrgModule.State('currentOrganization') private currentOrganization!: Organization
  private formatDate = CommonUtils.formatDisplayDate

  private totalTransactionAmount = 0
  private totalAmountToPay = 0
  private totalPaidAmount = 0

  private get suspendedDate () {
    return (this.currentOrganization?.suspendedOn) ? this.formatDate(new Date(this.currentOrganization.suspendedOn)) : ''
  }

  async mounted () {
    const failedInvoices: FailedInvoice = await this.calculateFailedInvoices()
    this.totalTransactionAmount = failedInvoices.totalTransactionAmount || 0
    this.totalAmountToPay = failedInvoices.totalAmountToPay || 0
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
