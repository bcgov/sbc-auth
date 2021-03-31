<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-6">
      <h2 class="view-header__title" data-test="account-settings-title">
        Product Packges
      </h2>
      <p class="mt-3 payment-page-sub">
        Select multiple additional products this account require access. By default the account will have
        access to adipiscing elit. Aliquam at porttitor sem.  Aliquam erat volutpat. Donec placerat.
      </p>
      <h4 class="mt-3 payment-page-sub">Select Additional Product(s)</h4>
    </div>
    <template v-if="productsLoaded">
      <div v-for="product in productDetails" :key="product.code">
        <SingleProduct
          :productDetails="product"
          @set-selected-product="setSelectedProduct"
          :userName="currentUser.fullName"
          :orgName="currentOrganization.name"
        ></SingleProduct>
      </div>
    </template>
    <template v-else>
      <div>No Products are available...</div>
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
import SingleProduct from '@/components/auth/common/SingleProduct.vue'
import { namespace } from 'vuex-class'
import { productStatus } from '@/util/constants'

const OrgModule = namespace('org')
const userModule = namespace('user')

@Component({
  components: {
    SingleProduct,
    ModalDialog
  }
})
export default class ProductPackage extends Mixins(AccountChangeMixin) {
  @OrgModule.State('currentOrganization') public currentOrganization!: Organization
  @userModule.State('currentUser') public currentUser!: KCUserProfile
  @OrgModule.Action('getOrgProducts') public getOrgProducts!:(orgId: number) =>Promise<OrgProduct>
  @OrgModule.Action('addOrgProducts') public addOrgProducts!:(orgId: number, product:OrgProductsRequestBody) =>Promise<OrgProduct>

  public isBtnSaved = false
  public disableSaveBtn = false
  public isLoading: boolean = false
  public errorTitle = 'Product Request Failed'
  public errorText = ''
  public productDetails:any =[]
  public productsLoaded:boolean = null
  public productsAddSuccess:boolean = false

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
        const addProd = await this.addOrgProducts(this.currentOrganization.id, addProductsRequestBody)
        this.productsAddSuccess = true
      } catch {
        // open when error
        this.$refs.errorDialog.open()
      }
    }
  }

  public async mounted () {
    // make call to get all products here
    try {
      const orgProducts = await this.getOrgProducts(this.currentOrganization.id)
      this.productDetails = orgProducts
      this.productsLoaded = true
    } catch {
      this.productsLoaded = false
      this.productDetails = []
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

.save-btn.disabled {
  pointer-events: none;
}
</style>
