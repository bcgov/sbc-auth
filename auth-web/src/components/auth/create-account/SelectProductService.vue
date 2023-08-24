<template>
  <v-form
    ref="form"
    lazy-validation
    data-test="form-profile"
  >
    <div class="view-header flex-column mb-6">
      <p
        v-if="isStepperView"
        class="mb-9"
      >
        To access our digitial registries services, select multiple product and services you require.
      </p>
    </div>
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
          @click="goBack"
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
import { Action, State } from 'pinia-class'
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { OrgProduct, Organization } from '@/models/Organization'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import Product from '@/components/auth/common/Product.vue'

import Steppable from '@/components/auth/common/stepper/Steppable.vue'

import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

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

  @State(useOrgStore) public currentOrganization!: Organization
  @State(useUserStore) public currentUser!: KCUserProfile
  @State(useOrgStore) public productList!: OrgProduct[]
  @State(useOrgStore) public currentSelectedProducts!: []

  @Action(useOrgStore) public getProductList!:() =>Promise<OrgProduct>
  @Action(useOrgStore) public addToCurrentSelectedProducts!:(productCode:any) =>Promise<void>
  @Action(useOrgStore) public resetoCurrentSelectedProducts!:() =>Promise<void>
  @Action(useOrgStore) public getOrgProducts!:(orgId: number) =>Promise<OrgProduct>
  @Action(useOrgStore) public setSubscribedProducts!:() =>Promise<OrgProduct>

  @Action(useOrgStore) private setResetAccountTypeOnSetupAccount!: (resetAccountTypeOnSetupAccount: boolean) => void

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
  cancel () {
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
