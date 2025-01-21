<template>
  <div>
    <v-radio-group v-model="selectedPaymentMethod">
      <v-card
        v-for="payment in filteredPaymentMethods"
        :key="payment.type"
        v-can:CHANGE_PAYMENT_METHOD.disable.card
        outlined
        :ripple="false"
        hover
        :disabled="!payment.supported"
        class="payment-card py-6 px-6 mb-4 elevation-1"
        :class="{'selected': isPaymentSelected(payment), 'mt-5': true}"
        :data-test="`div-payment-${payment.type}`"
        @click="paymentMethodSelected(payment)"
      >
        <div>
          <header class="flex-grow-1">
            <div
              class="d-inline-flex"
            >
              <v-radio
                v-show="isEditing || isCreateAccount"
                :key="payment.type"
                :value="payment.type"
              />
              <v-icon
                medium
                :color="payment.supported ? 'primary' : '#757575'"
                class="mr-1"
              >
                {{ payment.icon }}
              </v-icon>
              <h3 class="title font-weight-bold mt-n1 payment-title">
                {{ payment.title }}
                <span v-if="!payment.supported">
                  is not supported for the selected products
                </span>
              </h3>
            </div>
            <div class="mt-4">
              {{ payment.subtitle }}
            </div>
            <v-tooltip
              v-if="!isChangePaymentEnabled() && !isPaymentSelected(payment)"
              top
              content-class="top-tooltip"
              transition="fade-transition"
            >
              <template #activator="{ on, attrs }">
                <div
                  v-bind="attrs"
                  class="btn-tooltip-wrap"
                  v-on="on"
                >
                  <v-btn
                    large
                    depressed
                    color="primary"
                    width="120"
                    :class="['font-weight-bold', 'ml-auto', { 'disabled': !isChangePaymentEnabled() }]"
                    :aria-label="'Select' + ' ' + payment.title"
                    :data-test="`btn-payment-${payment.type}`"
                    disabled
                  >
                    <span>{{ isPaymentSelected(payment) ? 'SELECTED' : 'SELECT' }}</span>
                  </v-btn>
                </div>
              </template>
              <span>This payment method is not available after EFT is selected.</span>
            </v-tooltip>
          </header>

          <div class="payment-card-contents">
            <v-expand-transition>
              <div v-if="isPaymentSelected(payment)">
                <div
                  v-if="(payment.type === paymentTypes.EJV)"
                  class="pt-7"
                >
                  <GLPaymentForm
                    v-if="isEditing || isCreateAccount"
                    :canSelect="isBcolAdmin || isCreateAccount"
                    :gl-information="glInfo"
                    @is-gl-info-form-valid="isGLInfoValid"
                  />
                  <v-divider class="mb-4" />
                  <div v-if="!isEditing">
                    <h4 class="mb-2">
                      General Ledger Information
                    </h4>
                    <div v-if="!!glInfo">
                      <span class="d-flex"> Client Code: {{ glInfo.client }} </span>
                      <span class="d-flex"> Responsbility Center: {{ glInfo.responsibilityCentre }} </span>
                      <span class="d-flex"> Account Number: {{ glInfo.serviceLine }} </span>
                      <span class="d-flex"> Standard Object: {{ glInfo.stob }} </span>
                      <span class="d-flex"> Project: {{ glInfo.projectCode }} </span>
                    </div>
                  </div>
                </div>

                <div
                  v-else-if="(payment.type === paymentTypes.PAD)"
                  class="pad-form-container pt-4"
                >
                  <v-divider class="mb-5" />
                  <div v-if="!isEditing && currentOrgPADInfo && currentOrgPADInfo.bankAccountNumber">
                    <h4 class="mb-4">
                      Banking Information
                    </h4>
                    <span class="d-flex"> Transit Number: {{ currentOrgPADInfo.bankTransitNumber }} </span>
                    <span class="d-flex"> Institution Number: {{ currentOrgPADInfo.bankInstitutionNumber }} </span>
                    <span class="d-flex"> Account Number: {{ currentOrgPADInfo.bankAccountNumber }} </span>
                  </div>
                  <PADInfoForm
                    v-else
                    :isChangeView="isChangeView"
                    :isAcknowledgeNeeded="isAcknowledgeNeeded"
                    :isInitialAcknowledged="isInitialAcknowledged"
                    :isInitialTOSAccepted="isInitialTOSAccepted"
                    :clearOnEdit="isInitialTOSAccepted"
                    @is-pre-auth-debit-form-valid="isPADValid"
                    @emit-pre-auth-debit-info="getPADInfo"
                    @is-pad-info-touched="isPadInfoTouched"
                  />
                </div>

                <div
                  v-else-if="(payment.type === paymentTypes.BCOL)"
                  class="pt-7"
                >
                  <!-- showing BCOL details banner -->
                  <LinkedBCOLBanner
                    :bcolAccountName="currentOrganization.bcolAccountName"
                    :bcolAccountDetails="currentOrganization.bcolAccountDetails"
                    :isEditing="isEditing || isCreateAccount"
                    :force-edit-mode="forceEditModeBCOL"
                    @emit-bcol-info="setBcolInfo"
                  />
                </div>

                <div
                  v-else-if="(payment.type === paymentTypes.EFT)"
                  class="pt-7"
                >
                  <v-divider class="mb-7" />
                  <div class="mb-7">
                    To send us a payment through electronic funds transfer (EFT), please read the
                    <a
                      class="text-decoration-underline"
                      @click="downloadEFTInstructions"
                    >Electronic Funds Transfer Payment Instructions</a>.
                  </div>
                </div>

                <!-- Other Payment Types -->
                <div
                  v-else
                  class="pt-7"
                >
                  <v-divider class="mb-7" />
                  <div v-html="payment.description" />
                </div>
              </div>
            </v-expand-transition>
          </div>

          <p
            v-if="(payment.type === paymentTypes.BCOL)"
            class="mt-4 py-4 px-6 important bcol-warning-text ml-0"
          >
            {{ bcOnlineWarningMessage }}
          </p>
        </div>
      </v-card>
    </v-radio-group>
    <ModalDialog
      ref="warningDialog"
      max-width="650"
      :show-icon="false"
      :showCloseIcon="true"
      :title="dialogTitle"
      :text="dialogText"
      dialog-class="warning-dialog"
    >
      <template #icon>
        <v-icon
          large
          color="error"
        >
          mdi-alert-circle-outline
        </v-icon>
      </template>
      <template #actions>
        <div class="d-flex align-center justify-center w-100 h-100 ga-3">
          <v-btn
            large
            outlined
            color="outlined"
            @click="cancelModal"
          >
            Cancel
          </v-btn>
          <v-btn
            large
            color="primary"
            class="font-weight-bold"
            @click="continueModal"
          >
            Continue
          </v-btn>
        </div>
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { LDFlags, Pages, PaymentTypes } from '@/util/constants'
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { BcolProfile } from '@/models/bcol'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import { useDownloader } from '@/composables/downloader'
import { useOrgStore } from '@/stores/org'
import { useProductPayment } from '@/composables/product-payment-factory'

export default defineComponent({
  name: 'PaymentMethods',
  components: {
    PADInfoForm,
    LinkedBCOLBanner,
    GLPaymentForm,
    ModalDialog
  },
  props: {
    currentOrgType: { default: '' },
    currentOrganization: { default: undefined },
    currentSelectedPaymentMethod: { default: '' },
    currentOrgPaymentType: { default: undefined },
    isChangeView: { default: false },
    isAcknowledgeNeeded: { default: true },
    isTouchedUpdate: { default: false },
    isInitialTOSAccepted: { default: false },
    isInitialAcknowledged: { default: false },
    isBcolAdmin: { default: false },
    isEditing: { default: false },
    isCreateAccount: { default: false }
  },
  emits: ['cancel', 'get-PAD-info', 'emit-bcol-info', 'is-pad-valid', 'is-ejv-valid', 'payment-method-selected', 'save'],
  setup (props, { emit, root }) {
    const { fetchCurrentOrganizationGLInfo, getStatementsSummary, currentOrgPADInfo } = useOrgStore()
    const warningDialog: InstanceType<typeof ModalDialog> = ref(null)
    const ejvPaymentInformationTitle = 'General Ledger Information'

    const orgStore = useOrgStore()
    const state = reactive({
      bcOnlineWarningMessage: 'This payment method will soon be retired.',
      dialogTitle: '',
      dialogText: '',
      selectedPaymentMethod: '',
      padInfo: {},
      isTouched: false,
      isPaymentEJV: computed(() => state.selectedPaymentMethod === PaymentTypes.EJV),
      forceEditModeBCOL: computed(() =>
        props.currentSelectedPaymentMethod === PaymentTypes.BCOL &&
        props.currentOrgPaymentType !== undefined &&
        props.currentOrgPaymentType !== PaymentTypes.BCOL
      ),
      glInfo: computed(() => orgStore.currentOrgGLInfo)
    })

    const openBCOnlineDialog = () => {
      state.dialogTitle = 'BC Online Payment Option Ending Soon'
      state.dialogText = 'The "BC Online" payment option will soon be retired. Are you sure you want to continue?'
      warningDialog.value.open()
    }

    const openEFTWarningDialog = () => {
      state.dialogTitle = 'Confirm Payment Method Change'
      state.dialogText = `Are you sure you want to change your payment method to Electronic Funds Transfer?
                This action cannot be undone, and you will not be able to select a different payment method later.`
      warningDialog.value.open()
    }
    const paymentTypes = PaymentTypes

    // set on change of input only for single allowed payments
    const isPadInfoTouched = (isTouch: boolean) => {
      state.isTouched = isTouch
    }

    const isPaymentSelected = (payment) => {
      return (state.selectedPaymentMethod === payment.type)
    }

    const { downloadEFTInstructions } = useDownloader(orgStore, state)

    const hasBalanceOwing = async () => {
      if (!props.currentOrganization.id) {
        return null
      }
      try {
        const responseData = await getStatementsSummary(props.currentOrganization.id)
        return responseData?.totalDue || responseData?.totalInvoiceDue
      } catch (error) {
        console.log(error)
      }
    }

    const enableEFTPaymentMethod = () => {
      const enableEFTPayment: boolean = LaunchDarklyService.getFlag(LDFlags.EnablePaymentChangeFromEFT, false)
      return enableEFTPayment
    }

    const isChangePaymentEnabled = () => {
      return props.currentOrgPaymentType !== PaymentTypes.EFT || enableEFTPaymentMethod()
    }

    const paymentMethodSelected = async (payment, isTouch = true) => {
      const isFromEFT = props.currentOrgPaymentType === PaymentTypes.EFT
      if (payment.type === PaymentTypes.EFT && isTouch && state.selectedPaymentMethod !== PaymentTypes.EFT && !enableEFTPaymentMethod()) {
        openEFTWarningDialog()
      } else if (payment.type === PaymentTypes.PAD && isFromEFT) {
        const hasOutstandingBalance = await hasBalanceOwing()
        if (hasOutstandingBalance) {
          await root.$router.push({
            name: Pages.PAY_OUTSTANDING_BALANCE,
            params: { orgId: props.currentOrganization.id },
            query: { changePaymentType: payment.type }
          })
        }
      } else if (payment.type === PaymentTypes.BCOL && isTouch && state.selectedPaymentMethod !== PaymentTypes.BCOL) {
        openBCOnlineDialog()
      } else {
        state.bcOnlineWarningMessage = 'This payment method will soon be retired.'
      }
      state.selectedPaymentMethod = payment.type
      state.isTouched = isTouch
      // Emit touched flag for the parent element
      if (props.isTouchedUpdate) {
        emit('payment-method-selected', { selectedPaymentMethod: state.selectedPaymentMethod, isTouched: state.isTouched })
      } else {
        emit('payment-method-selected', state.selectedPaymentMethod)
      }
    }

    const getPADInfo = (padInfoValue) => {
      state.padInfo = padInfoValue
      emit('get-PAD-info', padInfoValue)
    }

    const setBcolInfo = (bcolProfile: BcolProfile) => {
      emit('emit-bcol-info', bcolProfile)
    }

    const isPADValid = (isValid) => {
      if (isValid) {
        paymentMethodSelected({ type: PaymentTypes.PAD }, state.isTouched)
      }
      emit('is-pad-valid', isValid && state.isTouched)
    }

    const isGLInfoValid = (isValid) => {
      emit('is-ejv-valid', isValid)
    }

    const cancelModal = () => {
      warningDialog.value.close()
      state.selectedPaymentMethod = ''
      emit('cancel')
    }

    const continueModal = async () => {
      const hasOutstandingBalance = await hasBalanceOwing()
      const isFromEFT = props.currentOrgPaymentType === PaymentTypes.EFT
      const isEFTSelected = state.selectedPaymentMethod === PaymentTypes.EFT

      if (isEFTSelected) {
        warningDialog.value.close()
        emit('save')
      } else {
        if (!hasOutstandingBalance) {
          warningDialog.value.close()
        } else if (isFromEFT) {
          await root.$router.push({
            name: Pages.PAY_OUTSTANDING_BALANCE,
            params: { orgId: props.currentOrganization.id },
            query: { changePaymentType: props.currentSelectedPaymentMethod }
          })
        }
        state.bcOnlineWarningMessage = 'This payment method will soon be retired. It is recommended to select a different payment method.'
      }
    }

    // Purpose: reset the payment method without having to reload the component.
    watch(() => props.currentSelectedPaymentMethod, (newValue) => {
      state.selectedPaymentMethod = newValue
    })

    const { PAYMENT_METHODS, filteredPaymentMethods } = useProductPayment(props, state)
    watch(() => [filteredPaymentMethods.value], () => {
      if (props.isCreateAccount && state.selectedPaymentMethod) {
        const paymentMethod = PAYMENT_METHODS[state.selectedPaymentMethod]
        if (!paymentMethod?.supported) {
          state.selectedPaymentMethod = ''
          emit('payment-method-selected', state.selectedPaymentMethod)
        }
      }
    })

    onMounted(async () => {
      paymentMethodSelected({ type: props.currentSelectedPaymentMethod }, false)
      if (state.isPaymentEJV) {
        await fetchCurrentOrganizationGLInfo(props.currentOrganization?.id)
      }
    })
    return {
      ...toRefs(state),
      paymentTypes,
      ejvPaymentInformationTitle,
      downloadEFTInstructions,
      paymentMethodSelected,
      getPADInfo,
      setBcolInfo,
      isPADValid,
      isPadInfoTouched,
      isPaymentSelected,
      warningDialog,
      cancelModal,
      continueModal,
      isGLInfoValid,
      isChangePaymentEnabled,
      currentOrgPADInfo,
      filteredPaymentMethods
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
@import '@/assets/scss/actions.scss';
@import '@/assets/scss/tooltip.scss';
.text-decoration-underline {
  text-decoration: underline;
}

.important {
  background-color: #fff7e3;
  border: 2px solid #fcba19;
  color: #495057;
  font-size: 12px;
}

.w-100 {
  width: 100%;
}

.h-100 {
  height: 100%;
}

.ga-3 {
  gap: 12px;
}

::v-deep {
  .v-btn.v-btn--outlined {
      border-color: var(--v-primary-base);
      color: var(--v-primary-base);
  }
  .v-input--radio-group__input {
    display: block
  }
}

.payment-card {
  transition: all ease-out 0.3s, opacity 0.3s ease, background-color 0.3 ease;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.selected {
    box-shadow: 0 0 0 2px inset var(--v-primary-base),
                0 3px 1px -2px rgba(0,0,0,.2),
                0 2px 2px 0 rgba(0,0,0,.14),
                0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
  &:active {
    opacity: .85;
    background-color: $gray1
  }
  &:focus:before {
    opacity: 0;
  }
}

.payment-card ::v-deep .v-icon.v-icon {
    align-items: flex-start !important;
}

.theme--light.v-card.v-card--outlined.selected {
  border-color: var(--v-primary-base);
}

.transparent-divider {
  border-color: transparent !important;
}

.payment-icon-container {
  flex: 0 0 auto;
  width: 4.5rem;
}

.pad-form-container {
  max-width: 75ch;
}

.bcol-warning-text {
  font-size: 14px;
}

.disabled {
  pointer-events: none;
}

.d-flex {
  display: flex;
}

.flex-grow-1 {
  flex-grow: 1;
}

// TODO change
.v-card--disabled {
  opacity: 0.8 !important;
}
</style>
