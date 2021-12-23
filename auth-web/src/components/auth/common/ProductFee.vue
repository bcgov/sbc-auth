<template>
  <v-card elevation="0">
    <div class="d-flex justify-space-between">
      <div class="d-flex" :class="{ 'w-100': !viewOnlyMode }">
        <div
          class="font-weight-bold mr-5"
          :class="{ 'prod-fee-label': !viewOnlyMode }"
        >
          Product Fee:
        </div>
        <div v-if="viewOnlyMode">
          <div>
            Statutory Fee:
            <span class="font-weight-bold">{{ applyFilling }}</span>
          </div>
          <div>
            Service Fee:
            <span class="font-weight-bold">{{ getProductFee }}</span>
          </div>
        </div>
        <div v-else class="d-flex w-100">
          <ProductFeeSelector
            :canSelect="true"
            :orgProductFeeCodes="orgProductFeeCodes"
            @update:updatedProductFee="updatedProductFee"
            :productCode="orgProduct.product"
            :selectedApplyFilingFees="existingFeeCodes"
          />
        </div>
      </div>
      <!-- v-can:CHANGE_ORG_NAME.disable -->
      <div v-if="viewOnlyMode">
        <span
          class="primary--text cursor-pointer"
          @click="updateViewOnlyMode(false)"
          data-test="btn-edit"
        >
          <v-icon color="primary" size="20"> mdi-pencil</v-icon>
          Change
        </span>
      </div>
    </div>

    <v-card-actions class="pt-1 pr-0" v-if="!viewOnlyMode">
      <v-spacer></v-spacer>
      <v-btn
        large
        class="save-btn px-9"
        color="primary"
        :loading="isProductActionLoading"
        aria-label="Save product fee"
        @click="saveProductFee()"
      >
        <span class="save-btn__label">Save</span>
      </v-btn>
      <v-btn
        outlined
        large
        depressed
        class="ml-2 px-9"
        color="primary"
        aria-label="Cancel product fee"
        @click="updateViewOnlyMode(true)"
        data-test="reset-button"
        >Cancel</v-btn
      >
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'

import { OrgProductFeeCode } from '@/models/Organization'
import ProductFeeSelector from '@/components/auth/common/ProductFeeSelector.vue'

@Component({
  components: {
    ProductFeeSelector
  }
})
export default class ProductFee extends Vue {
  @Prop({ default: undefined }) orgProduct: any // product available for orgs
  @Prop({ default: undefined }) orgProductFeeCodes: OrgProductFeeCode[] // product
  @Prop({ default: false }) isProductActionLoading: boolean // loading
  @Prop({ default: false }) isProductActionCompleted: boolean // close after saving

  private viewOnlyMode = true
  private selectedFee: any = {}

  @Watch('isProductActionCompleted')
  onProductActionCompleted (val, oldVal) {
    if (val && val !== oldVal) {
      this.updateViewOnlyMode(true)
    }
  }

  get applyFilling () {
    return this.orgProduct?.applyFilingFees === true ? 'Yes' : 'No'
  }

  get getProductFee () {
    const fee: any = this.productFee()
    return fee && fee.amount ? `$ ${fee && fee?.amount.toFixed(2)}` : ''
  }

  public updateViewOnlyMode (mode = true) {
    this.viewOnlyMode = mode
    if (mode === false) {
      // reset on cancel
      this.selectedFee = {}
    }
  }
  private productFee () {
    if (this.orgProductFeeCodes.length > 0) {
      const fees = this.orgProductFeeCodes.filter(
        (fee) => fee.code === this.orgProduct.serviceFeeCode
      )

      return fees && fees[0]
    }
    return {}
  }

  private updatedProductFee (data) {
    this.selectedFee = data
    return this.selectedFee
  }

  @Emit('save:saveProductFee')
  private saveProductFee () {
    return this.selectedFee
  }

  get existingFeeCodes () {
    const existingApplyFilingFees = this.selectedFee?.applyFilingFees
      ? this.selectedFee?.applyFilingFees
      : this.orgProduct?.applyFilingFees
    const fee: any = this.productFee()
    const selectedFeeCode = fee && fee.code
    const existingserviceFeeCode = this.selectedFee?.serviceFeeCode
      ? this.selectedFee?.serviceFeeCode
      : selectedFeeCode
    return { existingApplyFilingFees, existingserviceFeeCode }
  }
}
</script>
<style lang="scss" scoped>
.w-100 {
  width: 100%;
}
.prod-fee-label {
  width: 13%;
}
</style>
