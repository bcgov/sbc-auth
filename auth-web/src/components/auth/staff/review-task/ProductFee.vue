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
              @change="serviceFeeCodeChange"
              :data-test="getIndexedTag('select-apply-filing-fees', index)"
              req
              />
            </v-col>
            <v-col
            cols="6"
            >
              <v-select
              filled
              label="Service fee"
              :rules="serviceFeeCodeRules"
              :items="orgProductFeeCodes"
              item-text="amount"
              item-value="code"
              v-model="accountFee.serviceFeeCode"
              @change="serviceFeeCodeChange"
              :data-test="getIndexedTag('select-service-fee-code', index)"
              req
              >
                <template slot="selection" slot-scope="data">
                  $ {{ data.item.amount }}
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
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { namespace } from 'vuex-class'

const orgModule = namespace('org')

@Component({})
export default class ProductFee extends Vue {
    @Prop({ default: null }) private tabNumber: number
    @orgModule.State('orgProductFeeCodes') public orgProductFeeCodes!: OrgProductFeeCode[]
    @orgModule.State('orgProducts') public orgProducts!: OrgProduct[]
    @Prop({ default: 'Product Fee' }) private title: string
    // TODO: Make this as state
    private accountFees: AccountFee[] = []
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
          const accountFeeDTO: AccountFeeDTO = {
            product: orgProduct.code
          }
          this.accountFeesDTO.push(accountFeeDTO)
        })
      } else {
        // Map account fees details to accountFeesDTO so as to display in v-select
        this.accountFeesDTO = JSON.parse(JSON.stringify(this.accountFees))
        this.accountFeesDTO.map((accountFee:AccountFeeDTO) => {
          accountFee.applyFilingFees = accountFee.applyFilingFees.toString()
        })
      }
    }

    private updated () {
      this.$refs.productFeeForm?.validate()
    }

    private displayProductName (productCode: string): string {
      return this.orgProducts?.find(orgProduct => orgProduct.code === productCode)?.name
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

    private serviceFeeCodeChange (): void {
      // Wait till next DOM render to emit event so that we capture form validation
      this.$nextTick(() => {
        const accountFees = JSON.parse(JSON.stringify(this.accountFeesDTO))
        accountFees.map((accountFee:AccountFee) => {
          if (accountFee.applyFilingFees) {
            accountFee.applyFilingFees = accountFee.applyFilingFees.toString() === 'true'
          }
        })
        const productFeeChangeObject = {
          accountFees: accountFees,
          isFormValid: this.$refs.productFeeForm?.validate()
        }
        this.$emit('emit-product-fee-change', productFeeChangeObject)
      })
    }

    private getIndexedTag (tag, index): string {
      return `${tag}-${index}`
    }
}
</script>
