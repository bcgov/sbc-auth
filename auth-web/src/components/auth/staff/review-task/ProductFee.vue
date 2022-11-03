<template>
  <section v-if="accountFeesDTO.length">
    <h2 class="mb-5">{{`${tabNumber !== null ?  `${tabNumber}. ` : ''}${title}`}}</h2>
    <p class="mb-9">{{ $t('productFeeSubTitle') }}</p>
    <v-form ref="productFeeForm" id="productFeeForm">
      <div v-for="(accountFee, index) in accountFeesDTO" v-bind:key="index">
        <h3 class="title font-weight-bold mt-n1">{{ displayProductName(accountFee.product) }}</h3>
        <v-row>
            <v-col
            cols="6"
            >
              <v-select
              filled
              label="Statutory fee"
              item-text="text"
              item-value="value"
              :items="applyFilingFeesValues"
              :rules="applyFilingFeesRules"
              v-model="accountFee.applyFilingFees"
              @change="selectChange"
              :data-test="getIndexedTag('select-apply-filing-fees', index)"
              req
              :disabled="!canSelect"
              />
            </v-col>
            <v-col
            cols="6"
            >
              <v-select
              filled
              label="Service fee"
              :rules="serviceFeeCodeRules"
              :items="getOrgProductFeeCodesForProduct(accountFee.product)"
              item-text="amount"
              item-value="code"
              v-model="accountFee.serviceFeeCode"
              @change="selectChange"
              :data-test="getIndexedTag('select-service-fee-code', index)"
              req
              :disabled="!canSelect"
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
      </div>
    </v-form>
  </section>
</template>

<script lang="ts">
import { AccountFee, AccountFeeDTO, OrgProduct, OrgProductFeeCode } from '@/models/Organization'
import { Component, Prop, Vue } from 'vue-property-decorator'
import { ProductStatus } from '@/util/constants'
import { namespace } from 'vuex-class'

const orgModule = namespace('org')

@Component({})
export default class ProductFee extends Vue {
    @Prop({ default: null }) private tabNumber: number
    @orgModule.State('orgProductFeeCodes') public orgProductFeeCodes!: OrgProductFeeCode[]
    @orgModule.State('productList') public orgProducts!: OrgProduct[]
    @orgModule.State('currentAccountFees') public accountFees!: AccountFee[]
    @orgModule.Mutation('setCurrentAccountFees') public setCurrentAccountFees!:(accountFees: AccountFee[]) =>void
    @Prop({ default: 'Product Fee' }) private title: string
    @Prop({ default: false }) private canSelect: boolean

    // Create a DTO array so as to map applyFilingFees(boolean) value to string for v-select
    private accountFeesDTO: AccountFeeDTO[] = []
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

    private mounted () {
      if (!this.accountFees.length) {
        // prepopulate the array with the subscribed products
        this.orgProducts.forEach((orgProduct: OrgProduct) => {
          if (orgProduct.subscriptionStatus === ProductStatus.ACTIVE) {
            const accountFeeDTO: AccountFeeDTO = {
              product: orgProduct.code
            }
            this.accountFeesDTO.push(accountFeeDTO)
          }
        })
      } else {
        // Map account fees details to accountFeesDTO so as to display in v-select
        this.accountFeesDTO = JSON.parse(JSON.stringify(this.accountFees))
        this.accountFeesDTO.map((accountFee:AccountFeeDTO) => {
          accountFee.applyFilingFees = accountFee.applyFilingFees.toString()
        })
      }
    }

    public validateNow () {
      const isFormValid = this.$refs.productFeeForm?.validate()

      this.$emit('emit-product-fee-change', isFormValid)
    }

    private displayProductName (productCode: string): string {
      return this.orgProducts?.find(orgProduct => orgProduct.code === productCode)?.description
    }

    private displayProductFee (feeAmount: number): string {
      return `$ ${feeAmount.toFixed(2)} Service fee`
    }

    private applyFilingFeesRules = [
      v => !!v || 'A statutory fee is required'
    ]

    private serviceFeeCodeRules = [
      v => !!v || 'A service fee is required'
    ]

    private selectChange (): void {
      // Wait till next DOM render to emit event so that we capture form validation
      // this.$nextTick(() => {
      // Map back to AccountFees to store
      const accountFees: AccountFee[] = []
      this.accountFeesDTO.forEach((accountFeeDTO: AccountFeeDTO) => {
        const accountFee: AccountFee = {
          product: accountFeeDTO.product,
          applyFilingFees: accountFeeDTO.applyFilingFees === 'true',
          serviceFeeCode: accountFeeDTO.serviceFeeCode
        }
        accountFees.push(accountFee)
      })
      this.setCurrentAccountFees(accountFees)
      // })
    }

    private getIndexedTag (tag, index): string {
      return `${tag}-${index}`
    }

    // Only allow $1.05 fee code for ESRA aka Site Registry.
    public getOrgProductFeeCodesForProduct (productCode: string) {
      return this.orgProductFeeCodes?.filter((fee) => fee.code === 'TRF03' || productCode !== 'ESRA')
    }
}
</script>
