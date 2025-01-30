<template>
  <v-container
    class="view-container"
  >
    <div
      v-if="changePaymentType !== ''"
      class="view-header flex-column"
    >
      <h1
        class="view-header__title"
        data-test="account-settings-title"
      >
        Changing Payment Method to {{ getPaymentTypeText }}
      </h1>
    </div>
    <v-card flat>
      <Stepper
        ref="stepper"
        :stepper-configuration="stepperConfig"
        :isLoading="isLoading"
        :show-contact-info="false"
        redirectWhenDone="/"
        @step-forward="handleStepForward"
        @step-back="handleStepBack"
      />
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { LDFlags, PaymentTypes } from '@/util/constants'
import { PropType, computed, defineComponent, onMounted, ref } from '@vue/composition-api'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import OutstandingBalances from '@/components/pay/OutstandingBalances.vue'
import { useOrgStore } from '@/stores'

export default defineComponent({
  name: 'PayOutstandingBalanceView',
  components: {
    Stepper,
    // eslint-disable-next-line vue/no-unused-components
    OutstandingBalances,
  },
  props: {
    orgId: {
      type: String as PropType<string>,
      default: ''
    },
    paymentId: {
      type: String as PropType<string>,
      default: ''
    },
    changePaymentType: {
      type: String as PropType<string>,
      default: ''
    }
  },
  setup (props) {
    const orgStore = useOrgStore()
    const isLoading = ref(false)
    const statementSummary = ref(null)
    const stepper = ref(null)
    const enableEFTBalanceByPADFeature = computed(() => {
      return LaunchDarklyService.getFlag(LDFlags.EnableEFTBalanceByPAD) || false
    })
    const stepperConfig: StepConfiguration[] = [
      {
        title: 'Outstanding Balances',
        stepName: 'Outstanding Balances',
        component: OutstandingBalances,
        componentProps: {
          orgId: props.orgId,
          changePaymentType: props.changePaymentType,
          stepForward: handleStepForward,
          enableEFTBalanceByPADFeature: enableEFTBalanceByPADFeature.value
        }
      }
    ]

    async function getStatementSummary () {
      try {
        const responseData = await orgStore.getStatementsSummary(Number(props.orgId))
        statementSummary.value = responseData
      } catch (error) {
        console.log(error)
      }
    }

    onMounted(async () => {
      try {
        await getStatementSummary()
        const isOwing = (statementSummary.value?.totalDue + statementSummary.value?.totalInvoiceDue) > 0
        // Go to step two on the redirect back and payment has been completed
        if (props.paymentId && props.changePaymentType && !isOwing) {
          stepper.value.jumpToStep(2)
        }
      } catch (error) {
        // Failed to retrieve statement summary, so we should stay step 1
        console.error('Failed getting statement summary', error)
      }
    })

    function handleStepForward () {
      stepper.value.stepForward()
    }

    function handleStepBack () {
      stepper.value.stepBack()
    }

    function handleStepJumpTo (num) {
      stepper.value.jumpToStep(num)
    }

    const getPaymentTypeText = computed(() => {
      if (props.changePaymentType === PaymentTypes.BCOL) {
        return 'BC Online'
      } else if (props.changePaymentType === PaymentTypes.PAD) {
        return 'Pre-authorized Debit'
      }
      return ''
    })

    return {
      isLoading,
      stepper,
      stepperConfig,
      handleStepForward,
      handleStepBack,
      getPaymentTypeText,
      enableEFTBalanceByPADFeature
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/actions.scss';

</style>
