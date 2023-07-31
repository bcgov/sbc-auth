<template>
  <v-container class="view-container"
  v-can:EDIT_REQUEST_PRODUCT_PACKAGE.disable.card
  >

    <div class="view-header flex-column mb-6">
      <h2 class="view-header__title" data-test="account-settings-title">
        Products and Services
      </h2>
      <p class="mt-3 payment-page-sub">
        Request additional products or services you wish to access through your account.
      </p>
      <h4 class="mt-3 payment-page-sub">Select Additional Product(s)</h4>
    </div>
     <template v-if="isLoading">
      <div v-if="isLoading" class="loading-inner-container">
          <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
        </div>
    </template>
    <template v-else>
      <template v-if="productList && productList.length > 0">
        <div v-for="product in productList" :key="product.code">
          <Product v-if="!product.parentCode"
            :productDetails="product"
            @set-selected-product="setSelectedProduct"
            :userName="currentUser.fullName"
            :orgName="currentOrganization.name"
            :isexpandedView ="product.code === expandedProductCode"
            @toggle-product-details="toggleProductDetails"
            :isSelected="currentSelectedProducts.includes(product.code)"
            :isAccountSettingsView="true"
            :isBasicAccount="currentOrganization.orgType === AccountEnum.BASIC"
            :orgProduct="orgProductDetails(product)"
            :orgProductFeeCodes="orgProductFeeCodes"
            @save:saveProductFee="saveProductFee"
            :canManageProductFee="canManageAccounts"
            :isProductActionLoading="isProductActionLoading"
            :isProductActionCompleted="isProductActionCompleted"
          ></Product>
        </div>
        <div class="align-right-container">
          <p data-test="text-submit-request-error-message" class="text-submit-request-error-message" v-show="submitRequestValidationError"> {{ submitRequestValidationError }} </p>
        </div>
        <v-divider class="mb-5"></v-divider>
        <div class="align-right-container">
          <v-btn
          large
          class="submit-request-button"
          color="primary"
          aria-label="Submit Request"
          data-test="btn-product-submit-request"
          @click="submitProductRequest()"
          >
            <span>Submit Request</span>
          </v-btn>
        </div>
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
      <template v-slot:icon>
        <v-icon large color="primary
        ">{{dialogIcon}}</v-icon>
      </template>
      <template v-slot:actions>
        <v-btn
          large
          color="primary"
          class="font-weight-bold"
          @click="closeError"
        >
          OK
        </v-btn>
      </template>
    </ModalDialog>
  </v-container>
</template>

<script lang="ts">
import { AccessType, Account, ProductStatus, Role } from '@/util/constants'
import { AccountFee, OrgProduct, OrgProductCode, OrgProductFeeCode, OrgProductsRequestBody, Organization } from '@/models/Organization'
import { Component, Mixins, Vue } from 'vue-property-decorator'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Product from '@/components/auth/common/Product.vue'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const userModule = namespace('user')

@Component({
  components: {
    Product,
    ModalDialog
  }
})
export default class ProductPackage extends Mixins(AccountChangeMixin) {
  @OrgModule.State('currentOrganization') public currentOrganization!: Organization
  @userModule.State('currentUser') public currentUser!: KCUserProfile
  @OrgModule.State('productList') public productList!: OrgProduct[]
  @OrgModule.State('currentSelectedProducts') public currentSelectedProducts!: []

  @OrgModule.Mutation('resetCurrentSelectedProducts') public resetCurrentSelectedProducts!:() => void

  @OrgModule.Action('getOrgProducts') public getOrgProducts!:(orgId: number) =>Promise<OrgProduct>
  @OrgModule.Action('addOrgProducts') public addOrgProducts!:(product:OrgProductsRequestBody) =>Promise<OrgProduct>
  @OrgModule.Action('addToCurrentSelectedProducts') public addToCurrentSelectedProducts!:(productCode:any) =>Promise<void>
  @OrgModule.Action('syncCurrentAccountFees') public syncCurrentAccountFees!:(accoundId:number) =>Promise<AccountFee[]>
  @OrgModule.Action('fetchOrgProductFeeCodes') public fetchOrgProductFeeCodes!:() =>Promise<OrgProductFeeCode>
  @OrgModule.Action('updateAccountFees') public updateAccountFees!:(accountFee) =>Promise<any>

  public isBtnSaved = false
  public disableSaveBtn = false
  public isLoading: boolean = false
  public isProductActionLoading: boolean = false
  public dialogTitle = ''
  public dialogText = ''
  public dialogIcon = ''
  public submitRequestValidationError = ''
  public expandedProductCode: string = ''
  public AccountEnum = Account
  public orgProductsFees:any = ''
  public orgProductFeeCodes:any = ''
  public isProductActionCompleted: boolean = false

  $refs: {
      confirmDialog: ModalDialog
  }

  public async setSelectedProduct (productDetails) {
    // add/remove product from the currentselectedproducts store
    const productCode = productDetails.code
    const forceRemove = productDetails.forceRemove
    if (productCode) {
      this.addToCurrentSelectedProducts({ productCode: productCode, forceRemove })
    }
  }

  private async setup () {
    this.isLoading = true
    this.resetCurrentSelectedProducts()
    await this.loadProduct()
    // if staff need to load product fee also
    if (this.canManageAccounts) {
      this.orgProductsFees = await this.syncCurrentAccountFees(this.currentOrganization.id)
      this.orgProductFeeCodes = await this.fetchOrgProductFeeCodes()
    }

    this.isLoading = false
  }

  public toggleProductDetails (productCode:string) {
    // controll product expand here to collapse all other product
    this.expandedProductCode = productCode
  }

  public async mounted () {
    this.setAccountChangedHandler(this.setup)
    await this.setup()
  }

  public async loadProduct () {
    // refactor on next ticket
    try {
      await this.getOrgProducts(this.currentOrganization.id)
    } catch (err) {
      // eslint-disable-next-line no-console
      console.log('Error while loading products ', err)
    }
  }

  private get canManageAccounts () {
    // check for role and account can have service fee (GOVM and GOVN account)
    return this.currentUser?.roles?.includes(Role.StaffManageAccounts) && this.isVariableFeeAccount()
  }
  private orgProductDetails (product) {
    const { code: productCode, subscriptionStatus } = product

    let productData
    if (this.orgProductsFees && this.orgProductsFees.length > 0) {
      const orgProd = this.orgProductsFees.filter((orgProduct) => orgProduct.product === productCode)
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

  private isVariableFeeAccount () {
    const accessType:any = this.currentOrganization.accessType
    return ([AccessType.GOVM, AccessType.GOVN].includes(accessType)) || false
  }

  private closeError () {
    this.$refs.confirmDialog.close()
  }

  private async submitProductRequest () {
    try {
      if (this.currentSelectedProducts.length === 0) {
        this.submitRequestValidationError = 'Select at least one product or service to submit request'
      } else {
        this.submitRequestValidationError = ''
        const productsSelected: OrgProductCode[] = this.currentSelectedProducts.map((code: any) => {
          return { productCode: code }
        })

        const addProductsRequestBody: OrgProductsRequestBody = {
          subscriptions: productsSelected
        }
        await this.addOrgProducts(addProductsRequestBody)
        await this.setup()

        // show confirm modal
        this.dialogTitle = 'Access Requested'
        this.dialogText = 'Request has been submitted. Account will immediately have access to the requested product and service unless staff review is required.'
        this.dialogIcon = 'mdi-check'
        this.$refs.confirmDialog.open()
      }
    } catch (ex) {
      // open when error
      this.dialogTitle = 'Product Request Failed'
      this.dialogText = ''
      this.dialogIcon = 'mdi-alert-circle-outline'
      this.$refs.confirmDialog.open()

      // eslint-disable-next-line no-console
      console.log('Error while trying to submit product request')
    }
  }

  public async saveProductFee (accountFees) {
    const accountFee = { accoundId: this.currentOrganization.id, accountFees }
    this.isProductActionLoading = true
    this.isProductActionCompleted = false
    try {
      await this.updateAccountFees(accountFee)
      this.orgProductsFees = await this.syncCurrentAccountFees(this.currentOrganization.id)
    } catch (err) {
      // eslint-disable-next-line no-console
      console.log('Error while updating product fee ', err)
    } finally {
      this.isProductActionLoading = false
      this.isProductActionCompleted = true
    }
  }
}
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
