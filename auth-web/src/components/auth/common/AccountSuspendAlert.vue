<template>
  <v-alert
    class="px-8 py-7"
    :icon="false"
    prominent
    type="error"
  >
    <div class="account-alert">
      <div class="account-alert-inner">
        <v-icon
          large
          class="mt-2"
        >
          mdi-alert
        </v-icon>
        <div
          v-if="isSuspendedForNSF"
          class="account-alert__info ml-7"
        >
          <div class="font-weight-bold">
            Account Suspended
          </div>
          <div>
            This acount has been suspended. Returned system error message: {{ suspensionReason }}.
          </div>
          <div class="mt-6 title font-weight-bold">
            BALANCE DUE:  ${{ totalAmountToPay.toFixed(2) }}
          </div>
        </div>
        <div
          v-if="isSuspendedForNSF"
          class="account-alert__date"
        >
          {{ suspendedDate }}
        </div>
        <div
          v-else
          class="d-flex flex-column ml-7"
        >
          <div class="title font-weight-bold">
            Account Suspended ({{ suspendedReason }})
          </div>
          <div class="d-flex">
            <span>Date Suspended: {{ suspendedDate }}<span class="vertical-line" /> Suspended by: {{ suspendedBy }}</span>
          </div>
        </div>
      </div>
    </div>
  </v-alert>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { AccountStatus } from '@/util/constants'
import CommonUtils from '@/util/common-util'
import { FailedInvoice } from '@/models/invoice'
import { useCodesStore } from '@/stores/codes'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'AccountSuspendAlert',
  setup () {
    const orgStore = useOrgStore()
    const codesStore = useCodesStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)

    const state = reactive({
      totalTransactionAmount: 0,
      totalAmountToPay: 0,
      totalPaidAmount: 0,
      suspensionReason: computed(() => {
        return codesStore.suspensionReasonCodes?.find(
          suspensionReasonCode => suspensionReasonCode?.code === currentOrganization.value?.suspensionReasonCode
        )?.desc
      }),
      suspendedDate: currentOrganization.value?.suspendedOn
        ? CommonUtils.formatDateToHumanReadable(currentOrganization.value.suspendedOn) : '',
      isSuspendedForNSF: computed(() => currentOrganization.value?.statusCode === AccountStatus.NSF_SUSPENDED),
      suspendedBy: computed(() => currentOrganization.value?.decisionMadeBy),
      suspendedReason: computed(() => {
        return codesStore.suspensionReasonCodes?.find(
          suspensionReasonCode => suspensionReasonCode?.code === currentOrganization.value?.suspensionReasonCode
        )?.desc
      })
    })

    onMounted(async () => {
      if (state.isSuspendedForNSF) {
        const failedInvoices: FailedInvoice = await orgStore.calculateFailedInvoices()
        state.totalTransactionAmount = failedInvoices.totalTransactionAmount || 0
        state.totalAmountToPay = failedInvoices.totalAmountToPay || 0
      }
    })
    return {
      ...toRefs(state)
    }
  }
})
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

  .vertical-line {
  margin: 0 2em;
  border-left: solid;
  border-width: 0.125em;
  }

</style>
