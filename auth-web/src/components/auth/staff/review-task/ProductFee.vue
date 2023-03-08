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
import { computed, defineComponent, onMounted, reactive, ref, toRefs } from '@vue/composition-api'
import OrgModule from '@/store/modules/org'
import { ProductStatus } from '@/util/constants'
import { useStore } from 'vuex-composition-helpers'

// FUTURE: remove this in vue 3
interface ProductFeeState {
  accountFeesDTO: AccountFeeDTO[]
}

export default defineComponent({
  name: 'ProductFee',
  emits: ['emit-product-fee-change'],
  props: {
    tabNumber: {
      type: Number,
      default: null
    },
    title: {
      type: String,
      default: 'Product Fee'
    },
    canSelect: Boolean
  },
  setup (props, { emit }) {
    const store = useStore()
    const orgState = store.state.org as OrgModule
    const orgProductFeeCodes = computed<OrgProductFeeCode[]>(() => orgState.orgProductFeeCodes)
    const orgProducts = computed<OrgProduct[]>(() => orgState.productList)
    const accountFees = computed<AccountFee[]>(() => orgState.currentAccountFees)
    const setCurrentAccountFees = (accountFees: AccountFee[]): Promise<void> =>
      store.dispatch('org/setCurrentAccountFees', accountFees)

    const state: ProductFeeState = reactive<ProductFeeState>({
      accountFeesDTO: []
    }) as ProductFeeState

    // Create a DTO array so as to map applyFilingFees(boolean) value to string for v-select
    const applyFilingFeesValues = [
      {
        text: 'Yes',
        value: 'true'
      },
      {
        text: 'No',
        value: 'false'
      }
    ]

    // Didn't include this in reactive, not sure if it will bind to the markup.
    const productFeeForm = ref<HTMLFormElement>()

    onMounted(() => {
      if (!accountFees.value.length) {
        // prepopulate the array with the subscribed products
        orgProducts.value.forEach((orgProduct: OrgProduct) => {
          if (orgProduct.subscriptionStatus === ProductStatus.ACTIVE) {
            const accountFeeDTO: AccountFeeDTO = {
              product: orgProduct.code
            }
            state.accountFeesDTO.push(accountFeeDTO)
          }
        })
      } else {
        // Map account fees details to accountFeesDTO so as to display in v-select
        state.accountFeesDTO = JSON.parse(JSON.stringify(accountFees.value))
        state.accountFeesDTO.map((accountFee:AccountFeeDTO) => {
          accountFee.applyFilingFees = accountFee.applyFilingFees.toString()
        })
      }
    })

    const validateNow = () => {
      const isFormValid = productFeeForm?.value.validate()
      emit('emit-product-fee-change', isFormValid)
    }

    const displayProductName = (productCode: string): string => {
      return orgProducts.value.find(orgProduct => orgProduct.code === productCode)?.description
    }

    const displayProductFee = (feeAmount: number): string => {
      return `$ ${feeAmount.toFixed(2)} Service fee`
    }

    const applyFilingFeesRules = [
      v => !!v || 'A statutory fee is required'
    ]

    const serviceFeeCodeRules = [
      v => !!v || 'A service fee is required'
    ]

    const selectChange = () : void => {
      // Wait till next DOM render to emit event so that we capture form validation
      // Map back to AccountFees to store
      const accountFees: AccountFee[] = []
      state.accountFeesDTO.forEach((accountFeeDTO: AccountFeeDTO) => {
        const accountFee: AccountFee = {
          product: accountFeeDTO.product,
          applyFilingFees: accountFeeDTO.applyFilingFees === 'true',
          serviceFeeCode: accountFeeDTO.serviceFeeCode
        }
        accountFees.push(accountFee)
      })
      setCurrentAccountFees(accountFees)
    }

    const getIndexedTag = (tag, index): string => {
      return `${tag}-${index}`
    }

    // Only allow $1.05 and $0 service fee code for ESRA aka Site Registry.
    const getOrgProductFeeCodesForProduct = (productCode: string) => {
      return orgProductFeeCodes.value?.filter((fee) => ['TRF03', 'TRF04'].includes(fee.code) || productCode !== 'ESRA')
    }

    return {
      applyFilingFeesValues,
      validateNow,
      displayProductName,
      displayProductFee,
      applyFilingFeesRules,
      serviceFeeCodeRules,
      selectChange,
      getIndexedTag,
      getOrgProductFeeCodesForProduct,
      productFeeForm,
      ...toRefs(state)
    }
  }
})
</script>
