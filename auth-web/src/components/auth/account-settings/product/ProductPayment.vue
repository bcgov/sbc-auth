<template>
  <v-container
    :key="accountChangeKey"
    v-can:EDIT_REQUEST_PRODUCT_PACKAGE.disable.card
    class="view-container"
  >
    <div class="view-header flex-column mb-6">
      <h2
        class="view-header__title"
        data-test="account-settings-title"
      >
        Products and Payment
      </h2>
    </div>
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
    <template v-if="productPaymentReady">
      <h4 class="mb-4">
        Products and Services
      </h4>
      <div
        v-for="product in productList"
        :key="product.code"
      >
        <Product
          v-if="!product.parentCode"
          :key="productRenderKey"
          :productDetails="product"
          :activeSubProduct="subProduct"
          :userName="currentUser.fullName"
          :orgName="currentOrganization.name"
          :isexpandedView="product.code === expandedProductCode"
          :isSelected="currentSelectedProducts.includes(product.code)"
          :isAccountSettingsView="true"
          :orgProduct="orgProductDetails(product)"
          :orgProductFeeCodes="orgProductFeeCodes"
          :canManageProductFee="canManageAccounts"
          :isProductActionLoading="isProductActionLoading"
          :isProductActionCompleted="isProductActionCompleted"
          :disableWhileEditingPayment="isEditing"
          :paymentMethods="productPaymentMethods[product.code]"
          @set-selected-product="setSelectedProduct"
          @toggle-product-details="toggleProductDetails"
          @save:saveProductFee="saveProductFee"
        >
          <!-- Show product status message content for pending or rejected sub-product applications -->
          <template
            v-if="product.code === ProductEnum.MHR && mhrSubProductMsgContent()"
            #productContentSlot
          >
            <CautionBox
              setImportantWord="Note"
              :setAlert="mhrSubProductMsgContent().status === ProductStatus.REJECTED"
              :setMsg="mhrSubProductMsgContent().msg"
            >
              <template #prependSLot>
                <v-icon
                  class="mr-2"
                  :color="mhrSubProductMsgContent().color"
                >
                  {{ mhrSubProductMsgContent().icon }}
                </v-icon>
              </template>
            </CautionBox>
          </template>
        </Product>
      </div>
      <div class="align-right-container">
        <p
          v-show="submitRequestValidationError"
          data-test="text-submit-request-error-message"
          class="text-submit-request-error-message"
        >
          {{ submitRequestValidationError }}
        </p>
      </div>
      <v-divider class="mb-5" />
      <div class="d-flex">
        <strong :class="{'text-red': displaySavePaymentMethodsFirst}">Current Payment Method</strong>
        <span
          v-if="showEditButton"
          class="d-flex ml-auto"
          @click="isEditing = true"
        >
          <v-icon
            medium
            color="primary"
          >mdi-pencil
          </v-icon>
          Edit
        </span>
      </div>
      <span
        v-if="displaySavePaymentMethodsFirst"
        class="d-block text-red"
      >
        Please save your payment settings before making any product changes
      </span>
      <AccountPaymentMethods
        :key="paymentRenderKey"
        ref="paymentMethodRef"
        :isEditing="isEditing"
        :isBcolAdmin="isBcolAdmin"
        @disable-editing="isEditing = false"
        @reload-products="setup"
      />
    </template>

    <!-- Alert / Request Confirm Dialog -->
    <ModalDialog
      ref="confirmDialog"
      :title="dialogTitle"
      :text="dialogText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template #icon>
        <v-icon
          large
          color="primary"
        >
          {{ dialogIcon }}
        </v-icon>
      </template>
      <template #actions>
        <v-btn
          v-if="displayCancelOnDialog"
          large
          outlined
          color="outlined"
          data-test="dialog-ok-button"
          @click="closeError()"
        >
          Cancel
        </v-btn>
        <v-btn
          v-if="!dialogError"
          large
          color="primary"
          class="font-weight-bold"
          @click="displayCancelOnDialog ? submitProductRequest() : closeError()"
        >
          {{ submitDialogText }}
        </v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import {
  AccessType,
  Account,
  AccountStatus,
  Product as ProductEnum,
  ProductStatus,
  Role,
  TaskType
} from '@/util/constants'
import {
  OrgProduct,
  OrgProductCode,
  OrgProductsRequestBody
} from '@/models/Organization'
import { computed, defineComponent, onMounted, reactive, ref, toRefs, watch } from '@vue/composition-api'
import AccountPaymentMethods from '@/components/auth/account-settings/payment/AccountPaymentMethods.vue'
import CautionBox from '@/components/auth/common/CautionBox.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Product from '@/components/auth/common/Product.vue'
import { ProductStatusMsgContentIF } from '@/models/external'
import { storeToRefs } from 'pinia'
import { useAccountChangeHandler } from '@/composables'
import { useCodesStore } from '@/stores'
import { useOrgStore } from '@/stores/org'
import { useProductPayment } from '@/composables/product-payment-factory'
import { useUserStore } from '@/stores/user'
import { userAccessDisplayNames } from '@/resources/QualifiedSupplierAccessResource'

export default defineComponent({
  name: 'ProductPackage',
  components: {
    CautionBox,
    Product,
    ModalDialog,
    AccountPaymentMethods
  },
  setup (props) {
    const confirmDialog: InstanceType<typeof ModalDialog> = ref(null)

    const {
      currentUser
    } = useUserStore()
    const { setAccountChangedHandler } = useAccountChangeHandler()
    const {
      resetCurrentSelectedProducts,
      getOrgProducts,
      addOrgProducts,
      addToCurrentSelectedProducts,
      syncCurrentAccountFees,
      fetchOrgProductFeeCodes,
      updateAccountFees,
      needStaffReview,
      removeOrgProduct,
      getOrgPayments
    } = useOrgStore()

    const {
      getProductPaymentMethods
    } = useCodesStore()

    const {
      productList,
      currentSelectedProducts,
      currentOrganization // Needs to be here otherwise it won't be reactive.
    } = storeToRefs(useOrgStore())

    const paymentMethodRef = ref(null)

    const state = reactive({
      isBtnSaved: false,
      disableSaveBtn: false,
      isLoading: false,
      isProductActionLoading: false,
      dialogTitle: '',
      dialogText: '',
      dialogIcon: '',
      dialogError: false,
      submitRequestValidationError: '',
      expandedProductCode: '',
      AccountEnum: Account,
      orgProductsFees: [],
      orgProductFeeCodes: [],
      isProductActionCompleted: false,
      staffReviewClear: true,
      displayRemoveProductDialog: false,
      addProductOnAccountAdmin: undefined, // true if add product, false if remove product
      isVariableFeeAccount: computed(() => {
        const accessType:any = currentOrganization.value.accessType
        return ([AccessType.GOVM, AccessType.GOVN].includes(accessType)) || false
      }),
      canManageAccounts: computed((): boolean => {
        // check for role and account can have service fee (GOVM and GOVN account)
        return currentUser?.roles?.includes(Role.StaffManageAccounts) && state.isVariableFeeAccount
      }),
      /**
       * Return any sub-product that has a status indicating activity
       * Prioritize Active/Pending for edge-cases when multiple sub product statuses exist
       **/
      subProduct: computed((): OrgProduct => {
        return productList.value?.find(product =>
          !!product.parentCode && (
            product.subscriptionStatus === ProductStatus.ACTIVE ||
            product.subscriptionStatus === ProductStatus.PENDING_STAFF_REVIEW
          )
        ) || productList.value.find(product =>
          !!product.parentCode && product.subscriptionStatus === ProductStatus.REJECTED
        )
      }),
      // Not deconstructed otherwise name conflicts.
      productPaymentMethods: computed(() => useProductPayment(props, state).productPaymentMethods),
      displayCancelOnDialog: computed(() => !state.staffReviewClear || state.displayRemoveProductDialog),
      submitDialogText: computed(() => {
        if (state.displayCancelOnDialog && !state.dialogError) {
          if (!state.addProductOnAccountAdmin) {
            return 'Remove Product'
          } else {
            return 'Submit Request'
          }
        } else {
          return 'Close'
        }
      }),
      isEditing: false,
      productRenderKey: 0,
      paymentRenderKey: 0,
      isBcolAdmin: currentUser?.roles?.includes(Role.BcolStaffAdmin),
      showEditButton: computed(() => {
        const accessType:any = currentOrganization.value.accessType
        return !state.isEditing && (![AccessType.GOVM].includes(accessType) || state.isBcolAdmin)
      }),
      displaySavePaymentMethodsFirst: false,
      productPaymentReady: false,
      accountChangeKey: 0
    })

    const {
      hasProductOrPaymentBackendChanges
    } = useProductPayment()

    const loadProduct = async () => {
      try {
        await getOrgProducts(currentOrganization.value.id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error while loading products ', err)
      }
    }

    const setup = async () => {
      state.isLoading = true
      resetCurrentSelectedProducts()
      await getOrgPayments()
      await getProductPaymentMethods()
      await loadProduct()
      // if staff need to load product fee also
      if (state.canManageAccounts) {
        state.orgProductsFees = await syncCurrentAccountFees(currentOrganization.value.id)
        state.orgProductFeeCodes = await fetchOrgProductFeeCodes()
      }
      state.productPaymentReady = true
      state.isLoading = false
      state.displayRemoveProductDialog = false
      state.dialogError = false
      state.productRenderKey++
    }

    onMounted(async () => {
      setAccountChangedHandler(setup)
      await setup()
    })

    const toggleProductDetails = (productCode:string) => {
      // control product expand here to collapse all other product
      state.expandedProductCode = productCode
    }
    const orgProductDetails = (product) => {
      const { code: productCode, subscriptionStatus } = product

      let productData
      if (state.orgProductsFees && state.orgProductsFees.length > 0) {
        const orgProd = state.orgProductsFees.filter((orgProduct) => orgProduct.product === productCode)
        productData = (orgProd && orgProd[0])
      }

      if (!productData && subscriptionStatus !== ProductStatus.NOT_SUBSCRIBED) {
        // set default value
        productData = {
          'product': productCode,
          'applyFilingFees': true,
          'serviceFeeCode': productCode === 'ESRA' ? 'TRF03' : 'TRF01'
        }
      }

      return productData || {}
    }

    const closeError = async () => {
      confirmDialog.value.close()
      await setup()
    }

    /** Product status message content for CautionBox component */
    const mhrSubProductMsgContent = (): ProductStatusMsgContentIF => {
      // Return when no sub-products in pending or rejected state
      if (!state.subProduct) return

      const helpEmail = state.subProduct.description === TaskType.MHR_LAWYER_NOTARY
        ? 'bcolhelp@gov.bc.ca'
        : 'bcregistries@gov.bc.ca'

      switch (state.subProduct.subscriptionStatus) {
        case ProductStatus.PENDING_STAFF_REVIEW:
          return {
            status: state.subProduct.subscriptionStatus,
            icon: 'mdi-clock-outline',
            color: 'darkGray',
            msg: `Your application for Qualified Supplier – ${userAccessDisplayNames[state.subProduct.description]}
          access is under review. You will receive email notification once your request has been reviewed.`
          }
        case ProductStatus.REJECTED:
          return {
            status: state.subProduct.subscriptionStatus,
            icon: 'mdi-alert',
            color: 'error',
            msg: `Your application for Qualified Supplier – ${userAccessDisplayNames[state.subProduct.description]}
                access has been rejected. Refer to your notification email or contact
                <a href="mailto:${helpEmail}">${helpEmail}</a> for details. You can submit a new Qualified Supplier
                access request from your Manufactured Home Registry (or Asset Registries) page once you have all the
                required information.`
          }
        case ProductStatus.ACTIVE:
        default:
          return null
      }
    }

    const submitProductRequest = async () => {
      try {
        confirmDialog.value.close()
        if (currentSelectedProducts.value.length === 0) {
          state.submitRequestValidationError = 'Select at least one product or service to submit request'
        } else {
          state.submitRequestValidationError = ''
          const productsSelected: OrgProductCode[] = currentSelectedProducts.value.map((code: any) => {
            return { productCode: code }
          })

          const addProductsRequestBody: OrgProductsRequestBody = {
            subscriptions: productsSelected
          }
          if (await hasProductOrPaymentBackendChanges(currentOrganization.value.id)) {
            state.dialogTitle = 'Conflict Detected'
            state.dialogText = 'Your product/payment has been updated by another user. Please try again.'
            state.dialogIcon = 'mdi-alert-circle-outline'
            state.displayRemoveProductDialog = false
            confirmDialog.value.open()
            state.paymentRenderKey++
            await setup()
            return
          }
          if (state.addProductOnAccountAdmin) {
            await addOrgProducts(addProductsRequestBody)
          } else {
            await removeOrgProduct(productsSelected[0]?.productCode)
          }
          await setup()
          // show confirm modal
          if (state.addProductOnAccountAdmin && state.staffReviewClear) {
            state.dialogTitle = 'Product Added'
            state.dialogText = 'Your account now has access to the selected product.'
            state.dialogIcon = 'mdi-check'
            confirmDialog.value.open()
          }
        }
      } catch (ex) {
        // open when error
        state.dialogError = true
        state.dialogTitle = 'Product Request Failed'
        state.dialogText = ''
        state.dialogIcon = 'mdi-alert-circle-outline'
        confirmDialog.value.open()

        // eslint-disable-next-line no-console
        console.log('Error while trying to submit product request')
      }
      state.staffReviewClear = true
    }

    const saveProductFee = async (accountFees) => {
      const accountFee = { accountId: currentOrganization.value.id, accountFees }
      state.isProductActionLoading = true
      state.isProductActionCompleted = false
      try {
        await updateAccountFees(accountFee)
        state.orgProductsFees = await syncCurrentAccountFees(currentOrganization.value.id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error while updating product fee ', err)
      } finally {
        state.isProductActionLoading = false
        state.isProductActionCompleted = true
      }
    }

    const setSelectedProduct = async (productDetails) => {
      if (state.isEditing) {
        state.displaySavePaymentMethodsFirst = true
        return
      }
      const productCode = productDetails.code
      const forceRemove = productDetails.forceRemove

      if (productDetails.termsAccepted === false) {
        return
      }

      if (productCode) {
        addToCurrentSelectedProducts({ productCode: productCode, forceRemove })
      }

      state.staffReviewClear = !needStaffReview(productCode)
      state.addProductOnAccountAdmin = productDetails.addProductOnAccountAdmin

      if (!state.staffReviewClear && state.addProductOnAccountAdmin) {
        state.dialogTitle = 'Staff Review Required'
        state.dialogText = `This product needs a review by our staff before it is added to your account. 
        You will be notified by email once the request is reviewed.`
        confirmDialog.value.open()
      } else if (!state.addProductOnAccountAdmin) {
        state.displayRemoveProductDialog = true
        state.dialogTitle = 'Confirm Removing Product and Access'
        state.dialogText = `If you remove this product, you'll lose access. ` +
          `<br> <br>Are you sure you want to remove this product?`
        confirmDialog.value.open()
      } else {
        submitProductRequest()
      }
    }

    // Reload product list when organization changes
    watch(() => currentOrganization.value.id, async () => {
      await setup()
      state.isEditing = false
      // Required otherwise changing from USER -> ADMIN will leave it disabled
      state.accountChangeKey++
    })

    watch(() => state.isEditing, (newValue) => {
      if (!newValue) {
        state.displaySavePaymentMethodsFirst = false
      }
    })

    watch(() => state.displaySavePaymentMethodsFirst, (newValue) => {
      if (newValue) {
        paymentMethodRef.value.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    })

    return {
      setup,
      closeError,
      saveProductFee,
      orgProductDetails,
      setSelectedProduct,
      toggleProductDetails,
      submitProductRequest,
      mhrSubProductMsgContent,
      confirmDialog,
      productList,
      currentUser,
      currentOrganization,
      currentSelectedProducts,
      AccountStatus,
      ProductStatus,
      ProductEnum,
      paymentMethodRef,
      hasProductOrPaymentBackendChanges,
      ...toRefs(state)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
.text-red {
  color: $app-red
}
.align-right-container {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;
}
.loading-inner-container{
  display: flex;
  justify-content: center;
}

.save-btn.disabled {
  pointer-events: none;
}

.text-submit-request-error-message {
  color: var(--v-error-base);
}

/* Optional: Styling to center content */
.v-overlay__content {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
