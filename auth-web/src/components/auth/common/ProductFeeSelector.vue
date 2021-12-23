<template>

  <v-form ref="productFeeForm" id="productFeeForm" class="fee-form">
    <v-row >
      <v-col cols="6" class="pt-0">
        <v-select
          filled
          label="Statutory fee"
          item-text="text"
          item-value="value"
          :items="applyFilingFeesValues"
          :rules="applyFilingFeesRules"
          v-model="applyFilingFees"
          @change="selectChange"
          :data-test="getIndexedTag('select-apply-filing-fees', index)"
          req
          :disabled="!canSelect"
          class="fee-form"
        />
      </v-col>
      <v-col cols="6" class="pt-0">
        <v-select
          filled
          label="Service fee"
          :rules="serviceFeeCodeRules"
          :items="orgProductFeeCodes"
          item-text="amount"
          item-value="code"
          v-model="serviceFeeCode"
          @change="selectChange"
          :data-test="getIndexedTag('select-service-fee-code', index)"
          req
          :disabled="!canSelect"
          class="fee-form"
        >
          <template slot="selection" slot-scope="data">
            $ {{ data.item.amount.toFixed(2) }}
          </template>
          <template slot="item" slot-scope="data">
            {{ displayProductFee(data.item.amount) }}
          </template>
        </v-select>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { AccountFee, OrgProductFeeCode } from '@/models/Organization'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'

@Component({})
export default class ProductFee extends Vue {
  @Prop({ default: undefined }) orgProductFeeCodes: OrgProductFeeCode // product
  @Prop({ default: false }) private canSelect: boolean
  @Prop({ default: '' }) private productCode: any
  @Prop({ default: {} }) private selectedApplyFilingFees: any

  public applyFilingFees = 'false'
  public serviceFeeCode = ''
  public index = 1
  private applyFilingFeesValues = [
    {
      text: 'Yes',
      value: 'true'
    },
    {
      text: 'No',
      value: 'false'
    }
  ]

  $refs: {
    productFeeForm: HTMLFormElement
  }

  @Watch('selectedApplyFilingFees', { deep: true })
  updateFilingFees (val, oldVal) {
    if (
      val?.existingApplyFilingFees.toString() !==
      oldVal?.existingApplyFilingFees.toString()
    ) {
      this.applyFilingFees = val?.existingApplyFilingFees.toString() || ''
    }
    if (
      val?.existingserviceFeeCode.toString() !==
      oldVal?.existingserviceFeeCode.toString()
    ) {
      this.serviceFeeCode = val?.existingserviceFeeCode || ''
    }
  }

  private mounted () {
    this.applyFilingFees =
      this.selectedApplyFilingFees?.existingApplyFilingFees.toString() ||
      this.applyFilingFees
    this.serviceFeeCode =
      this.selectedApplyFilingFees?.existingserviceFeeCode ||
      this.serviceFeeCode
  }

  public validateNow () {
    const isFormValid = this.$refs.productFeeForm?.validate()

    this.$emit('emit-product-fee-change', isFormValid)
  }

  private displayProductFee (feeAmount: number): string {
    return `$ ${feeAmount.toFixed(2)} Service fee`
  }

  private applyFilingFeesRules = [(v) => !!v || 'A statutory fee is required']

  private serviceFeeCodeRules = [(v) => !!v || 'A service fee is required']
  @Emit('update:updatedProductFee')
  private selectChange () {
    const accountFee: AccountFee = {
      product: this.productCode,
      applyFilingFees: this.applyFilingFees === 'true',
      serviceFeeCode: this.serviceFeeCode
    }
    return accountFee
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }
}
</script>
<style lang="scss" scoped>
.fee-form{
  width: 100%
}
</style>
