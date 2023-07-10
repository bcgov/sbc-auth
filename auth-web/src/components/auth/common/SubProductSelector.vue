<template>
  <v-form
    id="sub-product-selector"
    class="pl-1 pr-3"
    ref="productSelectorFormRef"
  >
    <p>Select the access type you want (Required):</p>
    <v-radio-group
      hide-details
      v-model="selectedProduct"
      class="sub-product-radio-group"
    >
      <div
        v-for="subProduct in subProductConfig"
        :key="subProduct.type"
        class="sub-product-radio-wrapper ml-n9"
        :class="{'selected' : selectedProduct === subProduct.type }"
      >
        <v-divider />
        <v-radio
          class="sub-product-radio-btn mt-6 ml-9"
          :value="subProduct.type"
        >
          <template v-slot:label>
            <v-row no-gutters>
              <v-col cols="12">
                <v-label>{{ subProduct.label }}</v-label>
              </v-col>
              <v-col class="mt-1">
                <p>
                  <ul>
                    <li v-for="(bullet, index) in subProduct.productBullets" :key="index" class="bullet mt-2 ml-n1">
                      <span :class="{ 'font-weight-bold': isImportantBullet(subProduct, index) }">
                        {{ bullet }}
                      </span>
                    </li>
                  </ul>
                </p>
                <p v-if="subProduct.note" class="sub-product-note my-6 pr-3">
                  <strong>Note:</strong> <span v-html="subProduct.note"></span>
                </p>
              </v-col>
            </v-row>
          </template>
        </v-radio>
      </div>
    </v-radio-group>
  </v-form>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, watch } from '@vue/composition-api'
import { SubProductConfigIF } from '@/models/SubProductConfigIF'

export default defineComponent({
  name: 'SubProductSelector',
  emits: ['updateSubProduct'],
  props: {
    subProductConfig: {
      type: Array as () => Array<SubProductConfigIF>,
      default: []
    }
  },
  setup (props, { emit }) {
    const productSelectorRef = ref(null)
    const localState: any = reactive({
      selectedProduct: ''
    })

    const isImportantBullet = (subProduct: SubProductConfigIF, index: string|number) => {
      return subProduct.hasImportantBullet && index === subProduct.productBullets.length - 1
    }

    /** Emit the sub-product as it updates **/
    watch(() => localState.selectedProduct, (subProduct: string) => {
      emit('updateSubProduct', subProduct)
    })

    return {
      productSelectorRef,
      isImportantBullet,
      ...toRefs(localState)
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

.sub-product-note {
  font-size: 14px;
  line-height: 22px;
  cursor: default;
}

.selected {
  background-color: $app-background-blue;
}

::v-deep {
  a {
    color: $app-blue!important;
    text-decoration: underline;
  }
  .v-divider {
    border-color: $gray3!important;
  }
  .v-radio {
    align-items: unset;
  }
  .v-input .v-label {
    font-size: 16px;
    color: $gray9;
    font-weight: bold;
  }
  li {
    color: $gray7;
    font-size: 16px;
  }
}
</style>
