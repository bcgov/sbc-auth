<template>
  <v-form
    ref="form"
    lazy-validation
    data-test="form-profile"
  >
    <template v-if="isLoading">
      <div class="loading-inner-container">
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="isLoading"
        />
      </div>
    </template>
    <template v-else>
      <template v-if="productList && productList.length > 0">
        <div
          v-for="product in productList"
          :key="product.code"
          v-display-mode
        >
          <Product
            v-if="!product.parentCode"
            :productDetails="product"
            :isexpandedView="product.code === expandedProductCode"
            :isSelected="currentSelectedProducts.includes(product.code)"
            :paymentMethods="productPaymentMethods[product.code === 'BUSINESS_SEARCH' ? 'BUSINESSSearch' : product.code] || []"
            @set-selected-product="setSelectedProduct"
            @toggle-product-details="toggleProductDetails"
          />
        </div>
      </template>
      <template v-else>
        <div>No Products are available...</div>
      </template>
    </template>
    <v-divider class="mt-7 mb-10" />
    <v-row>
      <v-col
        cols="12"
        class="form__btns py-0 d-inline-flex"
      >
        <v-btn
          v-if="isStepperView && !noBackButton"
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
          :disabled="!isFormValid"
          @click="next"
        >
          <span>
            Next
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>
        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="isStepperView"
          :isEmit="true"
          @click-confirm="cancel"
        />
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { computed, defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import NextPageMixin from '../mixins/NextPageMixin.vue'
import Product from '@/components/auth/common/Product.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useOrgStore } from '@/stores/org'

export default defineComponent({
  name: 'SelectProductService',
  components: {
    ConfirmCancelButton,
    Product
  },
  mixins: [NextPageMixin, Steppable],
  props: {
    isStepperView: { type: Boolean, default: false },
    noBackButton: { type: Boolean, default: false },
    readOnly: { type: Boolean, default: false },
    orgId: { type: Number, default: undefined }
  },
  setup (props, { root }) {
    const form = ref(null)
    const orgStore = useOrgStore()

    const state = reactive({
      isLoading: false,
      expandedProductCode: '',
      productList: computed(() => orgStore.productList),
      productPaymentMethods: computed(() => orgStore.productPaymentMethods),
      currentSelectedProducts: computed(() => orgStore.currentSelectedProducts),
      isFormValid: computed(() => state.currentSelectedProducts && state.currentSelectedProducts.length > 0)
    })

    async function setup () {
      state.isLoading = true
      if (props.readOnly) {
        await orgStore.getOrgProducts(props.orgId)
        orgStore.setSubscribedProducts()
      } else {
        await orgStore.getProductList()
      }
      await orgStore.getProductPaymentMethods()
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

    function next () {
      console.log('next')
      orgStore.setResetAccountTypeOnSetupAccount(true)
      ;(props as any).stepForward()
    }

    function cancel () {
      root.$router.push('/')
    }

    onMounted(async () => {
      await setup()
    })

    return {
      ...toRefs(state),
      form,
      setSelectedProduct,
      toggleProductDetails,
      goBack,
      next,
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
</style>
