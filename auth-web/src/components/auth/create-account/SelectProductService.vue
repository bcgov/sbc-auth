<template>
  <v-form ref="form" lazy-validation data-test="form-profile">

    <div class="view-header flex-column mb-6">
    <p class="mb-9" v-if="isStepperView">To access our digitial registries services, select multiple product and services you require.</p>

    </div>
    <template v-if="isLoading">
      <div class="loading-inner-container">
          <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
        </div>
    </template>
    <template v-else>
      <template v-if="productList && productList.length > 0">
        <div v-for="product in productList" :key="product.code" v-display-mode>
          <Product
            :productDetails="product"
            @set-selected-product="setSelectedProduct"
            @toggle-product-details="toggleProductDetails"
            :isexpandedView ="product.code === expandedProductCode"
            :isSelected="currentSelectedProducts.includes(product.code)"
          ></Product>
        </div>
      </template>
      <template v-else>
        <div>No Products are available...</div>
      </template>
    </template>
    <v-divider class="mt-7 mb-10"></v-divider>
    <v-row>
      <v-col cols="12" class="form__btns py-0 d-inline-flex">
        <v-btn
          large
          depressed
          v-if="isStepperView && !noBackButton"
          color="default"
          @click="goBack"
          data-test="btn-back"
        >
          <v-icon left class="mr-2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>

        <v-btn
          large
          color="primary"
          class="save-continue-button mr-3"
          @click="next"
          v-if="isStepperView"
          data-test="next-button"
          :disabled="!isFormValid"
        >
          <span >
            Next
            <v-icon class="ml-2">mdi-arrow-right</v-icon>
          </span>

        </v-btn>
        <ConfirmCancelButton
          :showConfirmPopup="isStepperView"
          :isEmit="true"
          @click-confirm="cancel"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>

  </v-form>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { OrgProduct, Organization } from '@/models/Organization'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import Product from '@/components/auth/common/Product.vue'

import Steppable from '@/components/auth/common/stepper/Steppable.vue'

import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const userModule = namespace('user')

@Component({
  components: {
    ConfirmCancelButton,
    Product
  }
})
export default class SelectProductService extends Mixins(NextPageMixin, Steppable) {
  @Prop({ default: false }) isStepperView: boolean
  @Prop({ default: false }) noBackButton: boolean
  @Prop({ default: false }) readOnly: boolean
  @Prop({ default: undefined }) orgId: number

  @OrgModule.State('currentOrganization') public currentOrganization!: Organization
  @userModule.State('currentUser') public currentUser!: KCUserProfile
  @OrgModule.State('productList') public productList!: OrgProduct[]
  @OrgModule.State('currentSelectedProducts') public currentSelectedProducts!: []

  @OrgModule.Action('getProductList') public getProductList!:() =>Promise<OrgProduct>
  @OrgModule.Action('addToCurrentSelectedProducts') public addToCurrentSelectedProducts!:(productCode:any) =>Promise<void>
  @OrgModule.Action('resetoCurrentSelectedProducts') public resetoCurrentSelectedProducts!:() =>Promise<void>
  @OrgModule.Action('getOrgProducts') public getOrgProducts!:(orgId: number) =>Promise<OrgProduct>
  @OrgModule.Action('setSubscribedProducts') public setSubscribedProducts!:() =>Promise<OrgProduct>

  @OrgModule.Mutation('setResetAccountTypeOnSetupAccount') private setResetAccountTypeOnSetupAccount!: (resetAccountTypeOnSetupAccount: boolean) => void

  public isLoading: boolean = false
  public expandedProductCode: string = ''

  $refs: {
    form: HTMLFormElement
  }
  private async setup () {
    this.isLoading = true
    if (this.readOnly) {
      await this.getOrgProducts(this.orgId)
      this.setSubscribedProducts()
    } else {
      await this.getProductList()
    }

    this.isLoading = false
  }

  public async mounted () {
    // this.setAccountChangedHandler(this.setup)
    await this.setup()
  }

  get isFormValid () {
    return this.currentSelectedProducts && this.currentSelectedProducts.length > 0
  }

  public setSelectedProduct (productDetails) {
    const productCode = productDetails.code
    const forceRemove = productDetails.forceRemove
    // adding to store and submit on final click
    if (productCode) {
      this.addToCurrentSelectedProducts({ productCode: productCode, forceRemove })
    }
  }

  public toggleProductDetails (productCode) {
    // controll product expand here to collapse all other product
    this.expandedProductCode = productCode
  }

  public goBack () {
    this.stepBack()
  }
  public next () {
    this.setResetAccountTypeOnSetupAccount(true)
    this.stepForward()
  }
  private cancel () {
    this.$router.push('/')
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.loading-inner-container{
  display: flex;
  justify-content: center;
}

</style>
