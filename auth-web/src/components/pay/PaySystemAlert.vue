<template>
        <sbc-system-banner v-if="isPaySystemDown" v-bind:show='isPaySystemDown' type="warning" v-bind:message="alertMessage"> </sbc-system-banner>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import SbcSystemBanner from 'sbc-common-components/src/components/SbcSystemBanner.vue'
import PaymentModule from '@/store/modules/payment'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    SbcSystemBanner
  }
})

export default class PaySystemAlert extends Vue {
    paymentStore = getModule(PaymentModule, this.$store)

    mounted () {
      this.paymentStore.fetchPaySystemStatus()
    }
    get isPaySystemDown () {
      return !this.paymentStore.paySystemStatus.currentStatus
    }
    get alertMessage () {
      // TODO once the server side sends when the system is back up , calculate it..
      return 'Payment processing is currently not available for corporate filings.'
    }
}
</script>
