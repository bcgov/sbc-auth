<template>
  <div>
    <p class="mb-10 balance-paid">
      <v-icon
        class="pr-1"
        small
      >
        mdi-check-circle
      </v-icon>
      <span>Outstanding balance paid. You are now able to change your payment method.</span>
    </p>
    <template v-if="changePaymentType === paymentTypes.BCOL">
      <h3 class="mb-2 payment-type-header">
        <v-icon
          class="pr-1"
        >
          mdi-link-variant
        </v-icon>
        BC Online
      </h3>
      <div class="mt-2 mb-8">
        <span>Use your linked BC Online Account for payment.</span>
      </div>

      <v-divider />
      <LinkedBCOLBanner
        class="mt-4"
        data-test="bcol-form"
        @emit-bcol-info="setBcolInfo"
      />
      <CautionBox
        class="mb-4"
        setImportantWord="Important"
        :setAlert="false"
        :setMsg="warningMessage()"
        data-test="bcol-warning"
      />
    </template>
    <template v-else>
      <p
        class="mb-10"
        data-test="error-payment-method"
      >
        <v-icon
          color="red"
          class="pr-1"
          small
        >
          mdi-alert
        </v-icon>
        Unable to determine payment method to change to.
      </p>
    </template>
    <v-slide-y-transition>
      <div
        v-show="errorMessage"
        class="pb-2"
      >
        <v-alert
          type="error"
          icon="mdi-alert-circle-outline"
          data-test="alert-bcol-error"
        >
          {{ errorMessage }}
        </v-alert>
      </div>
    </v-slide-y-transition>

    <v-divider />
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          class="secondary-btn"
          data-test="btn-stepper-back"
          @click="cancel"
        >
          <span>Cancel</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          @click="complete"
        >
          <span>Complete</span>
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Pages, PaymentTypes } from '@/util/constants'
import { PropType, defineComponent, reactive, toRefs } from '@vue/composition-api'
import { BcolProfile } from '@/models/bcol'
import CautionBox from '@/components/auth/common/CautionBox.vue'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import { useOrgStore } from '@/stores'

export default defineComponent({
  name: 'CompletePaymentDetails',
  components: { CautionBox, LinkedBCOLBanner },
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
  emits: ['step-forward'],
  setup (props, { root }) {
    const orgStore = useOrgStore()
    const paymentTypes = PaymentTypes
    const state = reactive({
      bcolInfo: {} as BcolProfile,
      errorMessage: undefined
    })

    function setBcolInfo (bcolProfile: BcolProfile) {
      state.bcolInfo = bcolProfile
    }

    function warningMessage () {
      if (props.changePaymentType === PaymentTypes.BCOL) {
        return 'This payment method will soon be retired. It is recommended to select a different payment method.'
      }
    }

    function goToPaymentOptions () {
      root.$router.push(`${Pages.ACCOUNT_SETTINGS}/${Pages.PAYMENT_OPTION}`)
    }

    function cancel () {
      goToPaymentOptions()
    }

    const complete = async () => {
      state.errorMessage = ''
      if (props.changePaymentType === PaymentTypes.BCOL) {
        const isValid = !!(state.bcolInfo.userId && state.bcolInfo.password)
        if (!isValid) {
          state.errorMessage = 'Missing User ID and Password for BC Online.'
          return
        }
      }
      const createRequestBody = {
        paymentInfo: {
          paymentMethod: PaymentTypes.BCOL
        },
        bcOnlineCredential: state.bcolInfo
      }
      try {
        await orgStore.updateOrg(createRequestBody)
        goToPaymentOptions()
      } catch (error) {
        switch (error.response.status) {
          case 400:
          case 409:
            state.errorMessage = error.response.data.message
            break
          default:
            state.errorMessage = 'An error occurred while attempting to create your account.'
        }
      }
    }

    return {
      ...toRefs(state),
      complete,
      paymentTypes,
      setBcolInfo,
      warningMessage,
      cancel
    }
  }
})

</script>

<style lang="scss" scoped>
@import "$assets/scss/theme.scss";
@import "$assets/scss/actions.scss";

.payment-type-header{
  .v-icon {
    color: $app-blue
  }
}

.balance-paid {
  .v-icon{
    font-size: 20px !important;
    color: $BCgovGreen1 !important;
  }
  span {
    font-size: 14px !important;
  }
}

</style>
