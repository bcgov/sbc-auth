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
          <Product
            :productDetails="product"
            @set-selected-product="setSelectedProduct"
            :userName="currentUser.fullName"
            :orgName="currentOrganization.name"
            :isexpandedView ="product.code === expandedProductCode"
            @toggle-product-details="toggleProductDetails"
            :isSelected="showAsSelected(product.subscriptionStatus)"
          ></Product>
        </div>
      </template>
      <template v-else>
        <div>No Products are available...</div>
      </template>
    </template>

        <!-- Alert Dialog (Error) -->
    <ModalDialog
      ref="errorDialog"
      :title="errorTitle"
      :text="errorText"
      dialog-class="notify-dialog"
      max-width="640"
    >
      <template v-slot:icon>
        <v-icon large color="error">mdi-alert-circle-outline</v-icon>
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

import { Component, Mixins, Vue } from 'vue-property-decorator'
import { OrgProduct, OrgProductCode, OrgProductsRequestBody, Organization } from '@/models/Organization'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import Product from '@/components/auth/common/Product.vue'
import { namespace } from 'vuex-class'
import { productStatus } from '@/util/constants'

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

  @OrgModule.Action('getOrgProducts') public getOrgProducts!:(orgId: number) =>Promise<OrgProduct>
  @OrgModule.Action('addOrgProducts') public addOrgProducts!:(product:OrgProductsRequestBody) =>Promise<OrgProduct>

  public isBtnSaved = false
  public disableSaveBtn = false
  public isLoading: boolean = false
  public errorTitle = 'Product Request Failed'
  public errorText = ''

  public productsLoaded:boolean = null
  public productsAddSuccess:boolean = false
  public expandedProductCode: string = ''

  $refs: {
      errorDialog: ModalDialog
  }

  public async setSelectedProduct (product) {
    // set product and save call come here
    if (product && product.code) {
      try {
        const productsSelected: OrgProductCode[] = [{
          productCode: product.code
        }]

        const addProductsRequestBody: OrgProductsRequestBody = {
          subscriptions: productsSelected
        }
        // TODO now comment to avoid requesting product on check box. revisit as a part of new ticket
        // await this.addOrgProducts(addProductsRequestBody)
        // this.loadProduct()
        this.productsAddSuccess = true
      } catch {
        // open when error
        this.$refs.errorDialog.open()
      }
    }
  }

  public showAsSelected (productStatusCode) {
    const isSubscribed = [productStatus.ACTIVE].includes(productStatusCode)
    return isSubscribed
  }

  private async setup () {
    this.isLoading = true
    await this.loadProduct()
    this.isLoading = false
  }

  public toggleProductDetails (productCode) {
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
      this.getOrgProducts(this.currentOrganization.id)
      this.productsLoaded = true
    } catch {
      this.productsLoaded = false
    }
  }

  private closeError () {
    this.$refs.errorDialog.close()
  }
}
</script>

<style lang="scss" scoped>
.form__btns {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;

  .v-btn {
    width: 6rem;
  }
}
.loading-inner-container{
  display: flex;
  justify-content: center;
}

.save-btn.disabled {
  pointer-events: none;
}
</style>
