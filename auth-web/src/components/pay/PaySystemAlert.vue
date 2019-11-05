<template>
  <sbc-system-banner
    v-if="isPaySystemDown"
    v-bind:show="isPaySystemDown"
    type="warning"
    v-bind:message="alertMessage"
  ></sbc-system-banner>
</template>

<script lang='ts'>
import { Component, Vue } from 'vue-property-decorator'
import SbcSystemBanner from 'sbc-common-components/src/components/SbcSystemBanner.vue'
import StatusModule from '@/store/modules/status'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    SbcSystemBanner
  }
})

export default class PaySystemAlert extends Vue {
  statusStore = getModule(StatusModule, this.$store)

  private getBoolean (value: boolean | string | number): boolean {
    var resultVal = value
    if (typeof value === 'string') {
      resultVal = value.toLowerCase()
    }
    switch (resultVal) {
      case true:
      case 'true':
      case 1:
      case '1':
      case 'on':
      case 'yes':
      case 'none':
        return true
      default:
        return false
    }
  }

  mounted () {
    this.statusStore.fetchPaySystemStatus()
  }
  get isPaySystemDown () {
    return !this.getBoolean(this.statusStore.paySystemStatus.currentStatus)
  }
  get alertMessage () {
    // TODO once the server side sends when the system is back up , calculate it..
    return 'Payment processing is currently not available for corporate filings.'
  }
}

</script>
