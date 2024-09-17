<template>
  <div>
    <template v-if="isPaymentEJV">
      <GLPaymentForm
        :canSelect="isBcolAdmin"
        @is-gl-info-form-valid="isGLInfoValid"
      />
    </template>
    <template v-else-if="!isPaymentEJV">
      <v-card
        v-for="payment in allowedPaymentMethods"
        :key="payment.type"
        v-can:CHANGE_PAYMENT_METHOD.disable.card
        outlined
        :ripple="false"
        hover
        class="payment-card py-8 px-8 mb-4 elevation-1"
        :class="{'selected': isPaymentSelected(payment)}"
        :data-test="`div-payment-${payment.type}`"
      >
        <div>
          <header class="d-flex align-center flex-grow-1">
            <div class="payment-icon-container mt-n2">
              <v-icon
                x-large
                color="primary"
              >
                {{ payment.icon }}
              </v-icon>
            </div>
            <div class="pr-8 flex-grow-1">
              <h3 class="title font-weight-bold payment-title mt-n1">
                {{ payment.title }}
              </h3>
              <div>{{ payment.subtitle }}</div>
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
            <v-btn
              v-if="isPaymentSelected(payment) || isChangePaymentEnabled()"
              large
              depressed
              color="primary"
              width="120"
              :class="['font-weight-bold', 'ml-auto', { 'disabled': !isChangePaymentEnabled() }]"
              :outlined="!isPaymentSelected(payment) && isChangePaymentEnabled()"
              :aria-label="'Select' + ' ' + payment.title"
              :data-test="`btn-payment-${payment.type}`"
              @click="paymentMethodSelected(payment)"
            >
              <span>{{ (isPaymentSelected(payment)) ? 'SELECTED' : 'SELECT' }}</span>
            </v-btn>
          </header>

          <div class="payment-card-contents">
            <v-expand-transition>
              <div v-if="isPaymentSelected(payment)">
                <!-- PAD -->
                <div
                  v-if="(payment.type === paymentTypes.PAD)"
                  class="pad-form-container pt-7"
                >
                  <v-divider class="mb-7" />
                  <PADInfoForm
                    :isChangeView="isChangeView"
                    :isAcknowledgeNeeded="isAcknowledgeNeeded"
                    :isInitialAcknowledged="isInitialAcknowledged"
                    :isInitialTOSAccepted="isInitialTOSAccepted"
                    :clearOnEdit="isInitialTOSAccepted"
                    @is-pre-auth-debit-form-valid="isPADValid"
                    @emit-pre-auth-debit-info="getPADInfo"
                  />
                </div>

                <!-- BCOL -->
                <div
                  v-else-if="(payment.type === paymentTypes.BCOL)"
                  class="pt-7"
                >
                  <!-- showing BCOL details banner -->
                  <LinkedBCOLBanner
                    :bcolAccountName="currentOrganization.bcolAccountName"
                    :bcolAccountDetails="currentOrganization.bcolAccountDetails"
                    :show-edit-btn="true"
                    :force-edit-mode="forceEditModeBCOL"
                    @emit-bcol-info="setBcolInfo"
                  />
                </div>

                <!-- EFT -->
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
            class="mt-4 py-4 px-6 important bcol-warning-text"
          >
            {{ bcOnlineWarningMessage }}
          </p>
        </div>
      </v-card>
    </template>
    <!-- showing PAD form without card selector for single payment types -->
    <v-row v-else>
      <v-col
        cols="9"
        class="py-0"
      >
        <PADInfoForm
          :padInformation="{}"
          :isChangeView="isChangeView"
          :isAcknowledgeNeeded="isAcknowledgeNeeded"
          :isInitialTOSAccepted="isInitialTOSAccepted"
          :isInitialAcknowledged="isInitialAcknowledged"
          :clearOnEdit="isInitialTOSAccepted"
          @is-pre-auth-debit-form-valid="isPADValid($event)"
          @emit-pre-auth-debit-info="getPADInfo($event)"
          @is-pad-info-touched="isPadInfoTouched($event)"
        />
      </v-col>
    </v-row>
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
import { computed, defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import { BcolProfile } from '@/models/bcol'
import ConfigHelper from '@/util/config-helper'
import GLPaymentForm from '@/components/auth/common/GLPaymentForm.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import LinkedBCOLBanner from '@/components/auth/common/LinkedBCOLBanner.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import { useDownloader } from '@/composables/downloader'
import { useOrgStore } from '@/stores/org'

const PAYMENT_METHODS = {
  [PaymentTypes.CREDIT_CARD]: {
    type: PaymentTypes.CREDIT_CARD,
    icon: 'mdi-credit-card-outline',
    title: 'Credit Card',
    subtitle: 'Pay for transactions individually with your credit card.',
    description: `You don't need to provide any credit card information with your account. Credit card information will
                  be requested when you are ready to complete a transaction.`,
    isSelected: false
  },
  [PaymentTypes.EFT]: {
    type: PaymentTypes.EFT,
    icon: 'mdi-arrow-right-circle-outline',
    title: 'Electronic Funds Transfer',
    subtitle: 'Make payments from your bank account. Statement will be issued monthly.',
    description: ``,
    isSelected: false
  },
  [PaymentTypes.PAD]: {
    type: PaymentTypes.PAD,
    icon: 'mdi-bank-outline',
    title: 'Pre-authorized Debit',
    subtitle: 'Automatically debit a bank account when payments are due.',
    description: '',
    isSelected: false
  },
  [PaymentTypes.BCOL]: {
    type: PaymentTypes.BCOL,
    icon: 'mdi-link-variant',
    title: 'BC Online',
    subtitle: 'Use your linked BC Online account for payment.',
    description: '',
    isSelected: false
  },
  [PaymentTypes.ONLINE_BANKING]: {
    type: PaymentTypes.ONLINE_BANKING,
    icon: 'mdi-bank-outline',
    title: 'Online Banking',
    subtitle: 'Pay for products and services through your financial institutions website.',
    description: `
        <p><strong>Online banking is currently limited to the following institutions:</strong></p>
        <p>
          <ul>
            <li>Bank of Montreal</li>
            <li>Central 1 Credit Union</li>
            <li>Coast Capital Savings</li>
            <li>HSBC</li>
            <li>Royal Bank of Canada (RBC)</li>
            <li>Scotiabank</li>
            <li>TD Canada Trust (TD)</li>
          </ul>
        </p>
        <p>
          Once your account is created, you can use your account number to add BC Registries and Online Services as a
          payee in your financial institution's online banking system to make payments.
        </p>
        <p class="mb-0">
          BC Registries and Online Services <strong>must receive payment in full</strong> 
          from your financial institution prior to the release of items purchased through this service. 
          Receipt of an online banking payment generally takes 3-4 days from when you make the payment with your 
          financial institution.
        </p>`,
    isSelected: false
  }
}

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
    isBcolAdmin: { default: false }
  },
  emits: ['cancel', 'get-PAD-info', 'emit-bcol-info', 'is-pad-valid', 'is-ejv-valid', 'payment-method-selected', 'save'],
  setup (props, { emit, root }) {
    const { fetchCurrentOrganizationGLInfo, currentOrgPaymentDetails, getStatementsSummary } = useOrgStore()
    const warningDialog: InstanceType<typeof ModalDialog> = ref(null)

    const orgStore = useOrgStore()
    const state = reactive({
      bcOnlineWarningMessage: 'This payment method will soon be retired.',
      dialogTitle: '',
      dialogText: ''
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

    const selectedPaymentMethod = ref('')
    const paymentTypes = PaymentTypes
    const padInfo = ref({})
    const isTouched = ref(false)
    const ejvPaymentInformationTitle = 'General Ledger Information'

    // this object can define the payment methods allowed for each account tyoes
    const paymentsPerAccountType = ConfigHelper.paymentsAllowedPerAccountType()

    const allowedPaymentMethods = computed(() => {
      const paymentMethods = []
      if (props.currentOrgType) {
        const paymentTypes = paymentsPerAccountType[props.currentOrgType]
        paymentTypes?.forEach((paymentType) => {
          if (PAYMENT_METHODS[paymentType]) {
            paymentMethods.push(PAYMENT_METHODS[paymentType])
          }
        })
      }
      if (currentOrgPaymentDetails?.eftEnable) {
        paymentMethods.push(PAYMENT_METHODS[PaymentTypes.EFT])
      }
      return paymentMethods
    })

    const forceEditModeBCOL = computed(() =>
      props.currentSelectedPaymentMethod === PaymentTypes.BCOL &&
      props.currentOrgPaymentType !== undefined &&
      props.currentOrgPaymentType !== PaymentTypes.BCOL
    )

    const isPaymentEJV = computed(() => selectedPaymentMethod.value === PaymentTypes.EJV)

    // set on change of input only for single allowed payments
    const isPadInfoTouched = (isTouch: boolean) => {
      isTouched.value = isTouch
    }

    const isPaymentSelected = (payment) => {
      return (selectedPaymentMethod.value === payment.type)
    }

    const { downloadEFTInstructions } = useDownloader(orgStore, state)

    const hasBalanceOwing = async () => {
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
      if (payment.type === PaymentTypes.EFT && isTouch && selectedPaymentMethod.value !== PaymentTypes.EFT && !enableEFTPaymentMethod()) {
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
      } else if (payment.type === PaymentTypes.BCOL && isTouch && selectedPaymentMethod.value !== PaymentTypes.BCOL) {
        openBCOnlineDialog()
      } else {
        state.bcOnlineWarningMessage = 'This payment method will soon be retired.'
      }
      selectedPaymentMethod.value = payment.type
      isTouched.value = isTouch
      // Emit touched flag for the parent element
      if (props.isTouchedUpdate) {
        emit('payment-method-selected', { selectedPaymentMethod: selectedPaymentMethod.value, isTouched: isTouched.value })
      } else {
        emit('payment-method-selected', selectedPaymentMethod.value)
      }
    }

    const getPADInfo = (padInfoValue) => {
      padInfo.value = padInfoValue
      emit('get-PAD-info', padInfoValue)
    }

    const setBcolInfo = (bcolProfile: BcolProfile) => {
      emit('emit-bcol-info', bcolProfile)
    }

    const isPADValid = (isValid) => {
      if (isValid) {
        paymentMethodSelected({ type: PaymentTypes.PAD }, isTouched.value)
      }
      emit('is-pad-valid', isValid && isTouched.value)
    }

    const isGLInfoValid = (isValid) => {
      emit('is-ejv-valid', isValid)
    }

    const cancelModal = () => {
      warningDialog.value.close()
      selectedPaymentMethod.value = ''
      emit('cancel')
    }

    const continueModal = async () => {
      const hasOutstandingBalance = await hasBalanceOwing()
      const isFromEFT = props.currentOrgPaymentType === PaymentTypes.EFT
      const isEFTSelected = selectedPaymentMethod.value === PaymentTypes.EFT

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

    onMounted(async () => {
      paymentMethodSelected({ type: props.currentSelectedPaymentMethod }, false)
      if (isPaymentEJV.value) {
        await fetchCurrentOrganizationGLInfo(props.currentOrganization?.id)
      }
    })

    return {
      ...toRefs(state),
      selectedPaymentMethod,
      paymentTypes,
      padInfo,
      isTouched,
      ejvPaymentInformationTitle,
      allowedPaymentMethods,
      forceEditModeBCOL,
      isPaymentEJV,
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
      isChangePaymentEnabled
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
  margin-left: 4.5rem;
  margin-right: 120px;
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
}

.payment-card {
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

.payment-icon-container {
  flex: 0 0 auto;
  width: 4.5rem;
}

.payment-card-contents {
  padding-left: 4.5rem;
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
</style>
