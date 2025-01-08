<template>
  <v-container
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
    <template v-if="isLoading">
      <div
        v-if="isLoading"
        class="loading-inner-container"
      >
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
        <h4 class="mb-2">
          Products and Services
        </h4>
        <div
          v-for="product in productList"
          :key="product.code"
        >
          <Product
            v-if="!product.parentCode"
            :productDetails="product"
            :activeSubProduct="subProduct"
            :userName="currentUser.fullName"
            :orgName="currentOrganization.name"
            :isexpandedView="product.code === expandedProductCode"
            :isSelected="currentSelectedProducts.includes(product.code)"
            :isAccountSettingsView="true"
            :isBasicAccount="currentOrganization.orgType === AccountEnum.BASIC"
            :orgProduct="orgProductDetails(product)"
            :orgProductFeeCodes="orgProductFeeCodes"
            :canManageProductFee="canManageAccounts"
            :isProductActionLoading="isProductActionLoading"
            :isProductActionCompleted="isProductActionCompleted"
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
      </template>
      <template v-else>
        <div>No Products are available...</div>
      </template>
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
          large
          color="primary"
          class="font-weight-bold"
          @click="displayCancelOnDialog ? submitProductRequest() : closeError()"
        >
          {{ cancelDialogText }}
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
import { computed, defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import CautionBox from '@/components/auth/common/CautionBox.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Product from '@/components/auth/common/Product.vue'
import { ProductStatusMsgContentIF } from '@/models/external'
import { storeToRefs } from 'pinia'
import { useAccountChangeHandler } from '@/composables'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'
import { userAccessDisplayNames } from '@/resources/QualifiedSupplierAccessResource'

export default defineComponent({
  name: 'ProductPackage',
  components: {
    CautionBox,
    Product,
    ModalDialog
  },
  setup () {
    const confirmDialog: InstanceType<typeof ModalDialog> = ref(null)

    const { currentUser } = useUserStore()
    const { setAccountChangedHandler } = useAccountChangeHandler()
    const {
      resetCurrentSelectedProducts,
      getOrgProducts,
      addOrgProducts,
      removeOrgProducts,
      addToCurrentSelectedProducts,
      syncCurrentAccountFees,
      fetchOrgProductFeeCodes,
      updateAccountFees,
      needStaffReview
    } = useOrgStore()
    const orgStore = useOrgStore()

    const {
      currentOrganization,
      productList,
      currentSelectedProducts
    } = storeToRefs(useOrgStore())

    const localState = reactive({
      isBtnSaved: false,
      disableSaveBtn: false,
      isLoading: false,
      isProductActionLoading: false,
      dialogTitle: '',
      dialogText: '',
      dialogIcon: '',
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
        return currentUser?.roles?.includes(Role.StaffManageAccounts) && localState.isVariableFeeAccount
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
      productPaymentMethods: computed(() => orgStore.productPaymentMethods),
      displayCancelOnDialog: computed(() => !localState.staffReviewClear || localState.displayRemoveProductDialog),
      cancelDialogText: computed(() => {
        return localState.displayCancelOnDialog
          ? (!localState.addProductOnAccountAdmin ? 'Remove Product' : 'Submit Request')
          : 'Close'
      })
    })

    const loadProduct = async () => {
      // refactor on next ticket
      try {
        await getOrgProducts(currentOrganization.value.id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error while loading products ', err)
      }
    }

    const setup = async () => {
      localState.isLoading = true
      resetCurrentSelectedProducts()
      await loadProduct()
      // if staff need to load product fee also
      if (localState.canManageAccounts) {
        localState.orgProductsFees = await syncCurrentAccountFees(currentOrganization.value.id)
        localState.orgProductFeeCodes = await fetchOrgProductFeeCodes()
      }
      await orgStore.getProductPaymentMethods()
      localState.isLoading = false
      localState.displayRemoveProductDialog = false
    }

    onMounted(async () => {
      setAccountChangedHandler(setup)
      await setup()
    })

    const toggleProductDetails = (productCode:string) => {
      // control product expand here to collapse all other product
      localState.expandedProductCode = productCode
    }
    const orgProductDetails = (product) => {
      const { code: productCode, subscriptionStatus } = product

      let productData
      if (localState.orgProductsFees && localState.orgProductsFees.length > 0) {
        const orgProd = localState.orgProductsFees.filter((orgProduct) => orgProduct.product === productCode)
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
      if (!localState.subProduct) return

      const helpEmail = localState.subProduct.description === TaskType.MHR_LAWYER_NOTARY
        ? 'bcolhelp@gov.bc.ca'
        : 'bcregistries@gov.bc.ca'

      switch (localState.subProduct.subscriptionStatus) {
        case ProductStatus.PENDING_STAFF_REVIEW:
          return {
            status: localState.subProduct.subscriptionStatus,
            icon: 'mdi-clock-outline',
            color: 'darkGray',
            msg: `Your application for Qualified Supplier – ${userAccessDisplayNames[localState.subProduct.description]}
          access is under review. You will receive email notification once your request has been reviewed.`
          }
        case ProductStatus.REJECTED:
          return {
            status: localState.subProduct.subscriptionStatus,
            icon: 'mdi-alert',
            color: 'error',
            msg: `Your application for Qualified Supplier – ${userAccessDisplayNames[localState.subProduct.description]}
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
          localState.submitRequestValidationError = 'Select at least one product or service to submit request'
        } else {
          localState.submitRequestValidationError = ''
          const productsSelected: OrgProductCode[] = currentSelectedProducts.value.map((code: any) => {
            return { productCode: code }
          })

          const addProductsRequestBody: OrgProductsRequestBody = {
            subscriptions: productsSelected
          }
          if (localState.addProductOnAccountAdmin) {
            await addOrgProducts(addProductsRequestBody)
          } else {
            await currentSelectedProducts.value.forEach(code => removeOrgProducts(code))
          }
          await setup()
          // show confirm modal
          if (localState.addProductOnAccountAdmin && localState.staffReviewClear) {
            localState.dialogTitle = 'Product Added'
            localState.dialogText = 'Your account now has access to the selected product.'
            localState.dialogIcon = 'mdi-check'
            confirmDialog.value.open()
          }
        }
      } catch (ex) {
        // open when error
        localState.dialogTitle = 'Product Request Failed'
        localState.dialogText = ''
        localState.dialogIcon = 'mdi-alert-circle-outline'
        confirmDialog.value.open()

        // eslint-disable-next-line no-console
        console.log('Error while trying to submit product request')
      }
      localState.staffReviewClear = true
    }

    const saveProductFee = async (accountFees) => {
      const accountFee = { accoundId: currentOrganization.value.id, accountFees }
      localState.isProductActionLoading = true
      localState.isProductActionCompleted = false
      try {
        await updateAccountFees(accountFee)
        localState.orgProductsFees = await syncCurrentAccountFees(currentOrganization.value.id)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error while updating product fee ', err)
      } finally {
        localState.isProductActionLoading = false
        localState.isProductActionCompleted = true
      }
    }

    const setSelectedProduct = async (productDetails) => {
      // add/remove product from the currentselectedproducts store
      const productCode = productDetails.code
      const forceRemove = productDetails.forceRemove
      if (!productDetails.termsAccepted && productDetails.termsAccepted !== undefined) {
        return
      }

      if (productCode) {
        addToCurrentSelectedProducts({ productCode: productCode, forceRemove })
      }

      localState.staffReviewClear = !needStaffReview(productCode)
      localState.addProductOnAccountAdmin = productDetails.addProductOnAccountAdmin

      if (!localState.staffReviewClear && localState.addProductOnAccountAdmin) {
        localState.dialogTitle = 'Staff Review Required'
        localState.dialogText = `This product needs a review by our staff before it's added to your account. 
          We'll notify you by email once it's approved.`
        confirmDialog.value.open()
      } else if (!localState.addProductOnAccountAdmin) {
        localState.displayRemoveProductDialog = true
        localState.dialogTitle = 'Confirm Removing Product and Access'
        localState.dialogText = `If you remove this product, you'll lose access and need staff approval to add it back. ` +
          `This process may take a few business days.<br> <br>Areyou sure you want to remove this product?`
        confirmDialog.value.open()
      } else {
        submitProductRequest()
      }
    }

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
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
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
</style>
