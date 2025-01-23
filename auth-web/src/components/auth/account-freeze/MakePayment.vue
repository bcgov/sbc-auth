<template>
  <div>
    <p class="mb-10 font-weight-bold">
      Select a payment method to unlock your account
    </p>

    <v-alert
      v-if="errorText"
      type="error"
      class="mb-11"
    >
      <div v-sanitize="errorText" />
    </v-alert>

    <v-row class="mb-6">
      <v-col
        class="card d-flex"
      >
        <label
          class="d-flex"
        >
          <input
            type="radio"
            class="radio ml-6 mr-12"
            name="payment-method"
            value="EFT"
            checked
            @change="onPaymentMethodChange"
          >
          <div>
            <h2>Electronic Funds Transfer</h2>
            <p>
              Follow the                     <a
                class="text-decoration-underline"
                @click="downloadEFTInstructions"
              >payment instructions </a>to make a payment.
              Processing may take 2-5 business days after you paid.
              You will receive an email notification once your account is unlocked.
            </p>
          </div>
        </label>
      </v-col>
    </v-row>
    <v-row class="mb-6">
      <v-col
        class="card d-flex"
      >
        <label
          class="d-flex"
        >
          <input
            type="radio"
            class="radio ml-6 mr-12"
            name="payment-method"
            value="CC"
            @change="onPaymentMethodChange"
          >
          <div>
            <h2>Credit Card</h2>
            <p>Unlock your account immediately by using credit card</p>
          </div>
        </label>
      </v-col>
    </v-row>
    <v-divider />
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-reviewbank-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2 ml-n2"
          >
            mdi-arrow-left
          </v-icon>
          <span data-test="back">Back</span>
        </v-btn>
        <v-spacer />
        <v-btn
          large
          color="primary"
          :loading="isLoading"
          :disabled="isLoading"
          data-test="btn-reviewbank-next"
          @click="goNext"
        >
          <span data-test="next">Next</span>
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { CreateRequestBody, OrgPaymentDetails, PADInfo, PADInfoValidation } from '@/models/Organization'
import { defineComponent, onMounted, reactive, toRefs } from '@vue/composition-api'
import { PaymentTypes } from '@/util/constants'
import { useDownloader } from '@/composables/downloader'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'MakePayment',
  emits: ['step-forward', 'step-back', 'final-step-action', 'selected-payment-method'],
  setup (_, { emit }) {
    const orgStore = useOrgStore()
    const updateOrg = orgStore.updateOrg
    const validatePADInfo = orgStore.validatePADInfo
    const getOrgPayments = orgStore.getOrgPayments

    const state = reactive({
      padInfo: {} as PADInfo,
      refreshPAD: 0,
      isTouched: false,
      isLoading: false,
      errorText: '',
      paymentMethod: PaymentTypes.EFT
    })

    onMounted(async () => {
      const orgPayments: OrgPaymentDetails = await getOrgPayments()
      const cfsAccount = orgPayments?.cfsAccount
      state.padInfo.bankAccountNumber = cfsAccount?.bankAccountNumber
      state.padInfo.bankInstitutionNumber = cfsAccount?.bankInstitutionNumber
      state.padInfo.bankTransitNumber = cfsAccount?.bankTransitNumber
      state.padInfo.isTOSAccepted = !!(cfsAccount?.bankAccountNumber && cfsAccount?.bankInstitutionNumber && cfsAccount?.bankTransitNumber)
      state.refreshPAD++
    })

    function onPaymentMethodChange (event: any) {
      state.paymentMethod = event.target.value
    }

    async function verifyPAD () {
      state.errorText = ''
      const verifyPad: PADInfoValidation = await validatePADInfo()
      if (!verifyPad) {
        return true
      }

      if (verifyPad?.isValid) {
        return true
      }
      state.isLoading = false
      state.errorText = 'Bank information validation failed'
      if (verifyPad?.message?.length) {
        let msgList = ''
        verifyPad.message.forEach((msg) => {
          msgList += `<li>${msg}</li>`
        })
        state.errorText = `<ul class="error-list">${msgList}</ul>`
      }
      return false
    }

    async function goNext () {
      if (!state.isTouched) {
        emit('final-step-action', state.paymentMethod === PaymentTypes.EFT ? 'eft-payment-instructions' : '')
      } else {
        state.isLoading = true
        let isValid = state.isTouched ? await verifyPAD() : true
        if (isValid) {
          const createRequestBody: CreateRequestBody = {
            paymentInfo: {
              paymentMethod: PaymentTypes.PAD,
              bankTransitNumber: state.padInfo.bankTransitNumber,
              bankInstitutionNumber: state.padInfo.bankInstitutionNumber,
              bankAccountNumber: state.padInfo.bankAccountNumber
            }
          }
          try {
            await updateOrg(createRequestBody)
            emit('final-step-action')
          } catch (error) {
            // eslint-disable-next-line no-console
            console.error(error)
          } finally {
            state.isLoading = false
          }
        }
      }
    }

    async function goBack () {
      emit('step-back')
    }

    const { downloadEFTInstructions } = useDownloader(orgStore, state)

    return {
      ...toRefs(state),
      downloadEFTInstructions,
      onPaymentMethodChange,
      goNext,
      goBack
    }
  }
})
</script>

<style lang="scss" scoped>
.text-decoration-underline {
  text-decoration: underline;
}

.radio {
  transform: scale(1.5);
}

.card {
  box-shadow: 0 2px 1px -1px rgba(0,0,0,.2),0 1px 1px 0 rgba(0,0,0,.14),0 1px 3px 0 rgba(0,0,0,.12)!important;
  border-radius: 4px;
  padding: 32px 20px!important;
  border: thin solid rgba(0,0,0,.12);
  cursor: pointer;
  transition: all 0.3s ease;
  &:hover {
    border-color: var(--v-primary-base)!important
  }
  label {
    width: 100%;
    cursor: pointer;
  }
}
.selected {
  border-color: var(--v-primary-base)!important;
}
.link {
  color: var(--v-primary-base) !important;
  text-decoration: underline;
  cursor: pointer;
}
  ::v-deep .error-list {
    margin: 0;
    padding: 0;
    list-style-type: none;
  }
</style>
