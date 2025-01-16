<template>
  <div data-test="div-stepper-payment-method-selector">
    <p class="payment-page-sub mb-9">
      {{ pageSubTitle }}
    </p>
    <PaymentMethods
      v-display-mode
      :currentOrgType="currentOrganizationType"
      :currentOrganization="currentOrganization"
      :currentSelectedPaymentMethod="currentOrgPaymentType"
      :isInitialTOSAccepted="readOnly"
      :isInitialAcknowledged="readOnly"
      @payment-method-selected="setSelectedPayment"
      @is-pad-valid="setPADValid"
      @emit-bcol-info="setBcolInfo"
    />
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
    <v-divider class="my-10" />
    <v-row>
      <v-col class="py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-stepper-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2"
          >
            mdi-arrow-left
          </v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-2 font-weight-bold"
          data-test="save-button"
          :disabled="!isEnableCreateBtn"
          @click="save"
        >
          <!-- need to show submit button on review payment -->
          {{ readOnly ? 'Submit' : 'Create Account' }}
        </v-btn>
        <ConfirmCancelButton
          v-if="!readOnly"
          showConfirmPopup="true"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { AccessType, PaymentTypes, SessionStorageKeys } from '@/util/constants'
import { computed, defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { BcolProfile } from '@/models/bcol'
import ConfigHelper from '@/util/config-helper'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useOrgStore } from '@/stores/org'
import { useAccountCreate } from '@/composables/account-create-factory'

export default defineComponent({
  name: 'PaymentMethodSelector',
  components: {
    ConfirmCancelButton,
    PaymentMethods
  },
  mixins: [Steppable],
  props: {
    // need toi show TOS as checked in stepper BCEID re-upload time.
    // show submit button on final stepper to update info, even this page is read only
    readOnly: {
      type: Boolean,
      default: false
    }
  },
  setup (props, { emit }) {
    const orgStore = useOrgStore()

    const state = reactive({
      selectedPaymentMethod: '',
      isPADValid: false,
      errorMessage: '',
      currentOrganization: computed(() => orgStore.currentOrganization),
      currentOrganizationType: computed(() => orgStore.currentOrganizationType),
      currentOrgPaymentType: computed(() => orgStore.currentOrgPaymentType),
      pageSubTitle: computed(() => 'Select the payment method for this account.')
    })

    onMounted(() => {
      state.selectedPaymentMethod = state.currentOrgPaymentType
    })

    function goBack () {
      // Vue 3 - get rid of MIXINS and use the composition-api instead.
      (props as any).stepBack()
    }

    function isEnableCreateBtn () {
      if (state.selectedPaymentMethod === PaymentTypes.PAD) {
        return state.isPADValid
      } else if (state.selectedPaymentMethod === PaymentTypes.BCOL) {
        return state.currentOrganization.bcolProfile?.password
      } else {
        return !!state.selectedPaymentMethod
      }
    }

    function setSelectedPayment (payment) {
      state.selectedPaymentMethod = payment
      orgStore.setCurrentOrganizationPaymentType(state.selectedPaymentMethod)
      if (state.selectedPaymentMethod !== PaymentTypes.BCOL) {
        state.errorMessage = ''
      }
    }

    function setPADValid (isValid) {
      state.isPADValid = isValid
    }

    async function save () {
      useAccountCreate().save(state, createAccount)
    }

    function createAccount () {
      emit('final-step-action')
    }

    function setBcolInfo (bcolProfile: BcolProfile) {
      orgStore.setCurrentOrganizationBcolProfile(bcolProfile)
      emit('emit-bcol-info')
    }

    return {
      ...toRefs(state),
      goBack,
      isEnableCreateBtn,
      setSelectedPayment,
      setPADValid,
      createAccount,
      setBcolInfo
    }
  }
})
</script>

<style lang="scss" scoped>
.payment-card {
  background-color: var(--v-grey-lighten5) !important;
  transition: all ease-out 0.2s;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.selected {
    box-shadow: 0 0 0 2px inset var(--v-primary-base),
                0 3px 1px -2px rgba(0,0,0,.2),
                0 2px 2px 0 rgba(0,0,0,.14),
                0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
}

.theme--light.v-card.v-card--outlined.selected {
  border-color: var(--v-primary-base);
}

.transparent-divider {
  border-color: transparent !important;
}
</style>
