<template>
  <div>
    <v-card
      v-if="!productDetails.hidden"
      outlined
      hover
      class="product-card py-8 px-5 mb-4 elevation-1"
      :class="[ {'processing-card' : isSelected}]"
      :data-test="`div-product-${productDetails.code}`"
    >
      <div>
        <header class="d-flex align-center">
          <div
            v-if="hasDecisionNotBeenMade && !isBasicAccountAndPremiumProduct"
            class="pr-8"
            data-test="div-decision-not-made-product"
          >
            <v-checkbox
              :key="Math.random()"
              v-model="productSelected"
              class="product-check-box ma-0 pa-0"
              hide-details
              :data-test="`check-product-${productDetails.code}`"
              @change="selecThisProduct"
            >
              <template #label>
                <div class="ml-2">
                  <h3
                    class="title font-weight-bold product-title mt-n1"
                    :data-test="productDetails.code"
                  >
                    {{ productDetails.description }}
                    <v-tooltip
                      v-if="productPremTooltipText(productDetails.code)"
                      class="pa-2"
                      content-class="tooltip"
                      color="grey darken-4"
                      max-width="350px"
                      top
                    >
                      <template #activator="{ on }">
                        <span
                          v-if="productDetails.premiumOnly"
                          class="product-title-info"
                          v-on="on"
                        >
                          (<span class="underline-dotted">requires Premium Account</span>)
                        </span>
                      </template>
                      <div class="py-3">
                        <span>{{ productPremTooltipText(productDetails.code) }}</span>
                      </div>
                    </v-tooltip>
                    <span
                      v-else-if="productDetails.premiumOnly"
                      class="product-title-info"
                    > (requires Premium Account)</span>
                    <span class="product-title-badge ml-2 mt-n2"> {{ productBadge(productDetails.code) }}</span>
                  </h3>
                  <p
                    v-if="$te(productLabel.subTitle)"
                    v-sanitize="$t(productLabel.subTitle)"
                  />
                </div>
              </template>
            </v-checkbox>
          </div>
          <div
            v-else
            class="d-flex align-center pr-8"
            data-test="div-decision-made-product"
          >
            <v-icon
              :color="productLabel.decisionMadeColorCode"
              class="mr-2"
            >
              {{ productLabel.decisionMadeIcon }}
            </v-icon>
            <div class="ml-2 label-color">
              <h3
                class="title font-weight-bold product-title mt-n1"
                :data-test="productDetails.code"
              >
                {{ productDetails.description }}
                <v-tooltip
                  v-if="productPremTooltipText(productDetails.code)"
                  class="pa-2"
                  content-class="tooltip"
                  color="grey darken-4"
                  max-width="350px"
                  top
                >
                  <template #activator="{ on }">
                    <span
                      v-if="productDetails.premiumOnly"
                      class="product-title-info"
                      v-on="on"
                    >
                      (<span class="underline-dotted">requires Premium Account</span>)
                    </span>
                  </template>
                  <div class="py-3">
                    <span>{{ productPremTooltipText(productDetails.code) }}</span>
                  </div>
                </v-tooltip>
                <span
                  v-else-if="productDetails.premiumOnly"
                  class="product-title-info"
                > (requires Premium Account)</span>
                <span class="product-title-badge ml-2 mt-n2"> {{ productBadge(productDetails.code) }}</span>
              </h3>
              <p
                v-if="$te(productLabel.subTitle)"
                v-sanitize="$t(productLabel.subTitle)"
              />
            </div>
          </div>
          <v-btn
            large
            depressed
            color="primary"
            width="120"
            class="font-weight-bold ml-auto"
            :aria-label="`Select  ${productDetails.description}`"
            :data-test="`btn-productDetails-${productDetails.code}`"
            text
            @click="expand()"
          >
            <span
              v-if="isexpandedView"
              :data-test="`span-readless-${productDetails.code}`"
            >Read Less<v-icon
              meduim
              color="primary"
            >mdi-chevron-up</v-icon></span>
            <span
              v-else
              :data-test="`span-readmore-${productDetails.code}`"
            >Read More<v-icon
              meduim
              color="primary"
            >mdi-chevron-down</v-icon></span>
          </v-btn>
        </header>
        <div class="product-card-contents ml-9">
          <!-- Product Content Slot -->
          <slot name="productContentSlot" />

          <v-expand-transition>
            <div
              v-if="isexpandedView"
              :data-test="`div-expanded-product-${productDetails.code}`"
            >
              <p
                v-if="$te(productLabel.details)"
                v-sanitize="$t(productLabel.details)"
                class="mb-0"
              />
              <p
                v-if="$te(productLabel.note)"
                v-sanitize="$t(productLabel.note)"
                class="mb-0"
              />
              <component
                :is="productFooter.component"
                v-if="isTOSNeeded"
                :key="productFooter.id"
                v-bind="productFooter.props"
                :ref="productFooter.ref"
                v-display-mode="hasDecisionNotBeenMade ? false : viewOnly"
                v-on="productFooter.events"
              />
              <div v-if="showProductFee">
                <v-divider class="my-6" />
                <!-- This links to ProductFeeViewEdit. -->
                <ProductFee
                  :orgProduct="orgProduct"
                  :orgProductFeeCodes="orgProductFeeCodes"
                  :isProductActionLoading="isProductActionLoading"
                  :isProductActionCompleted="isProductActionCompleted"
                  @save:saveProductFee="saveProductFee"
                />
              </div>
              <v-label class="theme--light">
                <P class="mt-2">
                  Supported payment method:
                </P>
                <v-chip
                  v-for="method in paymentMethods"
                  :key="method"
                  small
                  label
                  class="mr-2 font-weight-bold"
                >
                  <v-icon>{{ paymentTypeIcon[method] }}</v-icon>{{ paymentTypeLabel[method] }}
                </v-chip>
              </v-label>
            </div>
          </v-expand-transition>
        </div>
        <div />
      </div>
    </v-card>
  </div>
</template>

<script lang="ts">
import { AccountFee, OrgProduct, OrgProductFeeCode } from '@/models/Organization'
import { DisplayModeValues, Product as ProductEnum, ProductStatus } from '@/util/constants'
import { PropType, computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { paymentTypeIcon, paymentTypeLabel } from '@/resources/display-mappers'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ProductFee from '@/components/auth/common/ProductFeeViewEdit.vue'
import ProductTos from '@/components/auth/common/ProductTOS.vue'

const TOS_NEEDED_PRODUCT = ['VS']

export default defineComponent({
  name: 'Product',
  components: {
    ProductTos,
    ProductFee
  },
  props: {
    productDetails: { default: null as OrgProduct },
    activeSubProduct: { default: null as OrgProduct },
    orgProduct: { default: null as AccountFee },
    orgProductFeeCodes: { type: Array as PropType<OrgProductFeeCode[]>, default: () => [] },
    isProductActionLoading: { type: Boolean, default: false },
    isProductActionCompleted: { type: Boolean, default: false },
    userName: { type: String, default: '' },
    orgName: { type: String, default: '' },
    isSelected: { type: Boolean, default: false },
    isexpandedView: { type: Boolean, default: false },
    isAccountSettingsView: { type: Boolean, default: false },
    isBasicAccount: { type: Boolean, default: false },
    canManageProductFee: { type: Boolean, default: false },
    paymentMethods: { type: Array as PropType<string[]>, default: () => [] }
  },
  setup (props, { emit }) {
    const state = reactive({
      count: 0,
      termsAccepted: false,
      productSelected: props.isSelected,
      viewOnly: DisplayModeValues.VIEW_ONLY,
      showProductFee: computed(() => {
        return props.canManageProductFee && props.orgProduct && props.orgProduct.product
      }),
      isTOSNeeded: computed(() => {
        return TOS_NEEDED_PRODUCT.includes(props.productDetails.code)
      })
    })

    onMounted(() => {
      state.productSelected = props.isSelected
    })

    watch(() => props.isSelected, (newValue) => {
      state.productSelected = newValue
    })

    const isBasicAccountAndPremiumProduct = computed(() => {
      return props.isBasicAccount && props.productDetails.premiumOnly
    })

    const productLabel = computed(() => {
      let { code } = props.productDetails
      let subTitle = `${code?.toLowerCase()}CodeSubtitle`
      let details = `${code?.toLowerCase()}CodeDescription`
      let note = `${code?.toLowerCase()}CodeNote`
      let decisionMadeIcon = null
      let decisionMadeColorCode = null

      if (props.isAccountSettingsView) {
        const status = props.productDetails.subscriptionStatus
        switch (status) {
          case ProductStatus.ACTIVE: {
            subTitle = `${code?.toLowerCase()}CodeActiveSubtitle`
            decisionMadeIcon = 'mdi-check-circle'
            decisionMadeColorCode = 'success'
            break
          }
          case ProductStatus.REJECTED: {
            subTitle = `${code?.toLowerCase()}CodeRejectedSubtitle`
            decisionMadeIcon = 'mdi-close-circle'
            decisionMadeColorCode = 'error'
            break
          }
          case ProductStatus.PENDING_STAFF_REVIEW: {
            subTitle = 'productPendingSubtitle'
            decisionMadeIcon = 'mdi-clock-outline'
            break
          }
          default: {
            break
          }
        }
        if (isBasicAccountAndPremiumProduct.value) {
          subTitle = `${code?.toLowerCase()}CodeUnselectableSubtitle`
          decisionMadeIcon = 'mdi-minus-box'
        }
        // Swap subtitle and details for sub-product specific content
        if (props.productDetails.code === ProductEnum.MHR && props.activeSubProduct?.subscriptionStatus === ProductStatus.ACTIVE) {
          subTitle = `mhrQsCodeActiveSubtitle`
          details = `${props.activeSubProduct.code?.toLowerCase()}CodeDescription`
          note = ''
        }
      }
      return { subTitle, details, decisionMadeIcon, decisionMadeColorCode, note }
    })

    const hasDecisionNotBeenMade = computed(() => {
      // returns true if create account flow
      if (!props.isAccountSettingsView) {
        return true
      }
      if (([ProductStatus.NOT_SUBSCRIBED] as Array<string>).includes(props.productDetails.subscriptionStatus)) {
        return true
      }
      state.termsAccepted = true
      return false
    })

    function expand () {
      const productCode = props.isexpandedView ? '' : props.productDetails.code
      // emit selected product code to controll expand all product
      emit('toggle-product-details', productCode)
      return productCode
    }

    function selecThisProduct (event, emitFromTos = false) {
      let forceRemove = false
      // expand if tos needed
      // as per new requirment, show expanded when user tries to click checkbox and not accepted TOS.
      // need to collapse on uncheck. Since both are using same function emitFromTos will be true when
      // click happend from TOS check box. then no need to collapse
      if (state.isTOSNeeded && !state.termsAccepted) {
        if (!emitFromTos) { // expand and collapse on click if click is not coming from TOS
          expand()
        }
        state.productSelected = false
        // wait till user approve TOS or remove product selection from array if tos not accepted
        forceRemove = true
      }
      emit('set-selected-product', { ...props.productDetails, forceRemove })
    }

    function saveProductFee (data) {
      emit('save:saveProductFee', data)
    }

    function tosChanged (termsAccepted: boolean) {
      state.count++
      state.termsAccepted = termsAccepted
      // force select when tos accept
      selecThisProduct(undefined, true)// no need to collaps on TOS accept
    }

    // if TOS needed will inject component
    // in future can use different components for different product
    const productFooter = computed(() => {
      return {
        id: 'tos',
        component: ProductTos,
        props: {
          userName: props.userName,
          orgName: props.orgName,
          isTOSAlreadyAccepted: state.termsAccepted
        },
        events: { 'tos-status-changed': tosChanged },
        ref: 'tosForm'
      }
    })

    function productBadge (code: string) {
      return LaunchDarklyService.getFlag(`product-${code}-status`)
    }

    function productPremTooltipText (code: string) {
      return LaunchDarklyService.getFlag(`product-${code}-prem-tooltip`)
    }

    return {
      ...toRefs(state),
      productLabel,
      paymentTypeIcon,
      isBasicAccountAndPremiumProduct,
      expand,
      selecThisProduct,
      productBadge,
      productPremTooltipText,
      productFooter,
      saveProductFee,
      hasDecisionNotBeenMade,
      paymentTypeLabel
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
.product-card {
  transition: all ease-out 0.2s;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.selected {
    box-shadow: 0 0 0 2px inset var(--v-primary-base),
                0 3px 1px -2px rgba(0,0,0,.2),
                0 2px 2px 0 rgba(0,0,0,.14),
                0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
  &.processing-card{
    border-color: var(--v-primary-base) !important;
  }
}

.theme--light.v-card.v-card--outlined.selected {
  border-color: var(--v-primary-base);
}

.label-color {
    color: rgba(0,0,0,.6) !important;
}

.product-title-info {
  color: $gray7;
  font-size: 1.125rem;
  font-weight: normal;
}

.product-title-badge {
  color: $BCgovBlue5;
  font-size: 0.875rem;
  letter-spacing: -0.25px;
  position: absolute;
  white-space: nowrap;
}

.underline-dotted {
  border-bottom: dotted;
}

.v-tooltip__content:before {
    content: ' ';
    position: absolute;
    bottom: -20px;
    left: 50%;
    margin-left: -10px;
    width: 20px;
    height: 20px;
    border-width: 10px 10px 10px 10px;
    border-style: solid;
    border-color: var(--v-grey-darken4) transparent transparent transparent;
  }

</style>
