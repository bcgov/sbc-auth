<template>
  <v-container
    class="view-container"
  >
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

import { PropType, defineComponent, onMounted, ref } from '@vue/composition-api'
import Stepper, { StepConfiguration } from '@/components/auth/common/stepper/Stepper.vue'
import CompletePaymentDetails from '@/components/pay/CompletePaymentDetails.vue'
import OutstandingBalances from '@/components/pay/OutstandingBalances.vue'
import { useOrgStore } from '@/stores'

export default defineComponent({
  name: 'PayOutstandingBalanceView',
  components: {
    Stepper,
    // eslint-disable-next-line vue/no-unused-components
    OutstandingBalances,
    // eslint-disable-next-line vue/no-unused-components
    CompletePaymentDetails
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
    const stepperConfig: StepConfiguration[] = [
      {
        title: 'Outstanding Balances',
        stepName: 'Outstanding Balances',
        component: OutstandingBalances,
        componentProps: {
          orgId: props.orgId,
          changePaymentType: props.changePaymentType,
          statementSummary: statementSummary
        }
      },
      {
        title: 'Payment Method Detail',
        stepName: 'Payment Method Detail',
        component: CompletePaymentDetails,
        componentProps: {
          orgId: props.orgId,
          paymentId: props.paymentId,
          changePaymentType: props.changePaymentType
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
      await getStatementSummary()
      const isOwing = (statementSummary.value?.totalDue + statementSummary.value?.totalInvoiceDue) > 0
      // Go to step two on the redirect back and payment has been completed
      if (props.paymentId && props.changePaymentType && !isOwing) {
        stepper.value.jumpToStep(2)
      }
    })

    const handleStepForward = () => {
      stepper.value.stepForward()
    }

    const handleStepBack = () => {
      stepper.value.stepBack()
    }

    return {
      isLoading,
      stepper,
      stepperConfig,
      handleStepForward,
      handleStepBack
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';

</style>
