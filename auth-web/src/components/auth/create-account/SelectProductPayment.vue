<template>
  <v-form
    ref="form"
    lazy-validation
    data-test="form-profile"
  >
    <v-overlay
      :value="isLoading"
      absolute
      class="loading-inner-container"
      opacity="0"
    >
      <v-progress-circular
        size="50"
        width="5"
        color="primary"
        :indeterminate="isLoading"
      />
    </v-overlay>
    <template v-if="productList && productList.length > 0">
      <div
        v-for="product in productList"
        :key="product.code"
        v-display-mode
      >
        <Product
          v-if="!product.parentCode"
          :disableWhileEditingPayment="false"
          :isCreateAccount="true"
          :productDetails="product"
          :isexpandedView="product.code === expandedProductCode"
          :isSelected="currentSelectedProducts.includes(product.code)"
          :paymentMethods="productPaymentMethods[product.code]"
          @set-selected-product="setSelectedProduct"
          @toggle-product-details="toggleProductDetails"
        />
      </div>
    </template>
    <v-divider class="mb-5" />
    <strong>Select a default payment method for your account: </strong>
    <PaymentMethods
      v-display-mode
      :currentOrgType="currentOrganizationType"
      :currentOrganization="currentOrganization"
      :currentSelectedPaymentMethod="currentOrgPaymentType"
      :isInitialTOSAccepted="readOnly"
      :isInitialAcknowledged="readOnly"
      :isCreateAccount="true"
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
    <v-row>
      <v-col
        cols="12"
        class="form__btns py-0 d-inline-flex"
      >
        <v-btn
          v-if="isStepperView"
          large
          depressed
          color="default"
          data-test="btn-back"
          @click="stepBack"
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
          v-if="isStepperView"
          large
          color="primary"
          class="save-continue-button mr-3"
          data-test="next-button"
          :disabled="!isFormValid || !isPaymentValid"
          @click="save"
        >
          <span>
            {{ readOnly ? 'Submit' : 'Create Account' }}
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>
        </v-btn>
        <ConfirmCancelButton
          v-if="!readOnly"
          :showConfirmPopup="true"
          :isEmit="true"
          @click-confirm="cancel"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import { BcolProfile } from '@/models/bcol'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import NextPageMixin from '../mixins/NextPageMixin.vue'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import { PaymentTypes } from '@/util/constants'
import Product from '@/components/auth/common/Product.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useAccountCreate } from '@/composables/account-create-factory'
import { useCodesStore } from '@/stores'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'SelectProductPayment',
  components: {
    PaymentMethods,
    ConfirmCancelButton,
    Product
  },
  mixins: [NextPageMixin, Steppable],
  props: {
    isStepperView: { type: Boolean, default: false },
    readOnly: { type: Boolean, default: false },
    orgId: { type: Number, default: undefined }
  },
  emits: ['final-step-action', 'emit-bcol-info'],
  setup (props, { root, emit }) {
    const form = ref(null)
    const orgStore = useOrgStore()
    const codesStore = useCodesStore()
    const state = reactive({
      isLoading: false,
      expandedProductCode: '',
      productList: computed(() => orgStore.productList),
      productPaymentMethods: computed(() => codesStore.productPaymentMethods),
      currentSelectedProducts: computed(() => orgStore.currentSelectedProducts),
      isFormValid: computed(() => state.currentSelectedProducts && state.currentSelectedProducts.length > 0),
      selectedPaymentMethod: '',
      errorMessage: '',
      currentOrganizationType: computed(() => orgStore.currentOrganizationType),
      currentOrgPaymentType: computed(() => orgStore.currentOrgPaymentType),
      isPaymentValid: computed(() => {
        if (state.selectedPaymentMethod === PaymentTypes.PAD) {
          return state.isPADValid
        } else if (state.selectedPaymentMethod === PaymentTypes.BCOL) {
          return state.currentOrganization.bcolProfile?.password
        } else {
          return !!state.selectedPaymentMethod
        }
      }),
      isPADValid: false
    })

    async function setup () {
      state.isLoading = true
      await codesStore.getProductPaymentMethods()
      if (props.readOnly) {
        await orgStore.getOrgProducts(props.orgId)
        orgStore.setSubscribedProducts()
      } else {
        await orgStore.getProductList()
      }
      state.isLoading = false
    }

    function setSelectedProduct (productDetails) {
      const productCode = productDetails.code
      const forceRemove = productDetails.forceRemove
      if (productCode) {
        orgStore.addToCurrentSelectedProducts({ productCode, forceRemove })
      }
    }

    function toggleProductDetails (productCode) {
      state.expandedProductCode = productCode
    }

    function goBack () {
      // Vue 3 - get rid of MIXINS and use the composition-api instead.
      (props as any).stepBack()
    }

    function cancel () {
      root.$router.push('/')
    }

    onMounted(async () => {
      await setup()
    })

    // Payment
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
      orgStore.setResetAccountTypeOnSetupAccount(true)
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
      form,
      setSelectedProduct,
      setSelectedPayment,
      setPADValid,
      setBcolInfo,
      toggleProductDetails,
      goBack,
      save,
      cancel
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.loading-inner-container {
  display: flex;
  justify-content: center;
}
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
