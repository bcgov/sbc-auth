<template>
  <v-alert class="px-8 py-7" :icon="false" prominent type="error">
    <div class="account-alert">
      <div class="account-alert-inner">
        <v-icon large class="mt-2">mdi-information-outline</v-icon>
        <div class="account-alert__info ml-7">
          <div class="font-weight-bold">Account Suspended</div>
          <div>Account has been suspended for outstanding balance (NSF).</div>
          <div class="mt-6 title font-weight-bold">BALANCE DUE:  ${{totalAmountToPay.toFixed(2)}}</div>
        </div>
        <div class="account-alert__date">
          {{suspendedDate}}
        </div>
      </div>
    </div>
  </v-alert>
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
  .account-alert-inner {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
  }

  .account-alert__info {
    flex: 1 1 auto;
  }

  .account-alert__date {
    flex: 0 0 auto;
  }

</style>
