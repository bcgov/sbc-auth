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
        <header class="d-flex">
          <div
            v-if="!hideCheckbox"
            class="pr-8"
            data-test="div-decision-not-made-product"
          >
            <v-checkbox
              :key="Math.random()"
              v-model="productSelected"
              class="product-check-box ma-0 pa-0"
              hide-details
              :data-test="`check-product-${productDetails.code}`"
              @change="selectThisProduct"
            >
              <template #label>
                <div class="ml-2 product-card-contents">
                  <h3
                    class="title font-weight-bold product-title mt-n1"
                    :data-test="productDetails.code"
                  >
                    {{ productDescription(productDetails.code, productDetails.description) }}
                    <span class="product-title-badge ml-2 mt-n2"> {{ productBadge(productDetails.code) }}</span>
                  </h3>
                  <p
                    v-if="$te(productLabel.subTitle)"
                    v-sanitize="$t(productLabel.subTitle)"
                    class="mt-2"
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
                <span class="product-title-badge ml-2 mt-n2"> {{ productBadge(productDetails.code) }}</span>
              </h3>
              <p
                v-if="$te(productLabel.subTitle)"
                v-sanitize="$t(productLabel.subTitle)"
                class="mt-2"
              />
            </div>
          </div>
          <v-btn
            large
            depressed
            color="primary"
            width="120"
            class="font-weight-bold ml-auto mt-6"
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
        <div class="product-card-contents ml-10">
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
              />
              <p v-if="$te(productLabel.link)">
                <v-btn
                  large
                  depressed
                  color="primary"
                  class="font-weight-bold pl-0"
                  text
                  :href="$t(productLabel.link)"
                  target="_blank"
                  rel="noopener"
                  tag="a"
                >
                  <span>Visit Information Page</span>
                  <span class="mdi mdi-open-in-new" />
                </v-btn>
              </p>

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
            </div>
          </v-expand-transition>
        </div>
        <div class="ml-10 mt-2">
          <v-label>
            <P
              v-if="paymentMethods.length > 0"
              class="product-card-contents"
            >
              Supported payment methods:
            </P>
            <v-chip
              v-for="method in paymentMethods"
              :key="method"
              x-small
              label
              class="mr-2 font-weight-bold product-payment-icons py-3 my-1"
            >
              <v-icon class="mr-1">
                {{ paymentTypeIcon[method] }}
              </v-icon>{{ paymentTypeLabel[method] }}
            </v-chip>
          </v-label>
          <div v-if="showProductFee">
            <v-divider class="my-4" />
            <!-- This links to ProductFeeViewEdit. -->
            <ProductFee
              :orgProduct="orgProduct"
              :orgProductFeeCodes="orgProductFeeCodes"
              :isProductActionLoading="isProductActionLoading"
              :isProductActionCompleted="isProductActionCompleted"
              @save:saveProductFee="saveProductFee"
            />
          </div>
          <div>
            <v-expand-transition>
              <v-alert
                v-if="showPaymentMethodNotSupported"
                class="mt-6 mb-4 alert-item alert-inner"
                :icon="false"
                prominent
                outlined
                type="warning"
              >
                <div class="alert-inner mb-0">
                  <v-icon
                    medium
                  >
                    mdi-alert
                  </v-icon>
                  <p class="alert__info mb-0 pl-3">
                    <strong>Payment Method Not Supported:</strong> This product is not supported by your current payment
                    method. Please choose a different payment type to use this product.
                  </p>
                </div>
              </v-alert>
            </v-expand-transition>
          </div>
        </div>
        <div />
      </div>
    </v-card>
  </div>
</template>

<script lang="ts">
import { AccountFee, OrgProduct, OrgProductFeeCode } from '@/models/Organization'
import { DisplayModeValues, PaymentTypes, Product as ProductEnum, ProductStatus } from '@/util/constants'
import { PropType, computed, defineComponent, onMounted, reactive, toRefs, watch } from '@vue/composition-api'
import { paymentTypeIcon, paymentTypeLabel, productDisplay } from '@/resources/display-mappers'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ProductFee from '@/components/auth/common/ProductFeeViewEdit.vue'
import ProductTos from '@/components/auth/common/ProductTOS.vue'
import { useOrgStore } from '@/stores'

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
    canManageProductFee: { type: Boolean, default: false },
    disableWhileEditingPayment: { type: Boolean, default: false },
    isCreateAccount: { type: Boolean, default: false },
    paymentMethods: { type: Array as PropType<string[]>, default: () => [] }
  },
  setup (props, { emit }) {
    const orgStore = useOrgStore()
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
      }),
      paymentMethodSupported: computed(() => {
        const paymentMethod = orgStore.currentOrgPaymentType === PaymentTypes.CREDIT_CARD
          ? PaymentTypes.DIRECT_PAY : orgStore.currentOrgPaymentType
        return !orgStore.currentOrgPaymentType || props.paymentMethods.includes(paymentMethod)
      }),
      hasDecisionNotBeenMade: computed(() => {
        // returns true if create account flow
        if (!props.isAccountSettingsView) {
          return true
        }
        return ([ProductStatus.NOT_SUBSCRIBED] as Array<string>).includes(props.productDetails.subscriptionStatus)
      }),
      hideCheckbox: computed(() => {
        const decisionMadeStatus = [ProductStatus.PENDING_STAFF_REVIEW, ProductStatus.REJECTED]
        return (decisionMadeStatus as Array<string>).includes(props.productDetails.subscriptionStatus)
      }),
      // if TOS needed will inject component
      // in future can use different components for different product
      productFooter: computed(() => {
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
      }),
      productLabel: computed(() => {
        let { code } = props.productDetails
        let subTitle = `${code?.toLowerCase()}CodeSubtitle`
        let details = `${code?.toLowerCase()}CodeDescription`
        let link = `${code?.toLowerCase()}CodeDescriptionLink`
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
          // Swap subtitle and details for sub-product specific content
          if (props.productDetails.code === ProductEnum.MHR && props.activeSubProduct?.subscriptionStatus === ProductStatus.ACTIVE) {
            subTitle = `mhrQsCodeActiveSubtitle`
            details = `${props.activeSubProduct.code?.toLowerCase()}CodeDescription`
            note = ''
          }
        }
        return { subTitle, details, link, decisionMadeIcon, decisionMadeColorCode, note }
      }),
      showPaymentMethodNotSupported: false
    })

    onMounted(() => {
      state.productSelected = props.isAccountSettingsView ? !state.hasDecisionNotBeenMade : props.isSelected
    })

    watch(() => props.isSelected, (newValue) => {
      // Only products with TOS need to be watched, as it may cause a submit error if applied to other products
      if (TOS_NEEDED_PRODUCT.includes(props.productDetails.code)) {
        state.productSelected = newValue
      }
    })

    // Untested.
    watch(() => state.hasDecisionNotBeenMade, (newValue) => {
      if (!newValue) {
        state.termsAccepted = true
      }
    })

    function expand () {
      const productCode = props.isexpandedView ? '' : props.productDetails.code
      // emit selected product code to controll expand all product
      emit('toggle-product-details', productCode)
      return productCode
    }

    function selectThisProduct (event, emitFromTos = false) {
      if (props.disableWhileEditingPayment) {
        state.productSelected = !state.productSelected
        // Triggers error message, state change is ignored.
        emit('set-selected-product')
        return
      }
      const productSubscribed = props.productDetails.subscriptionStatus === ProductStatus.ACTIVE
      if (!props.isCreateAccount && !state.paymentMethodSupported && !productSubscribed) {
        state.productSelected = false
        state.showPaymentMethodNotSupported = true
        setTimeout(() => {
          state.showPaymentMethodNotSupported = false
        }, 4000)
        return
      }

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

      let addorRemoveProduct // false is remove product

      if (props.isAccountSettingsView && TOS_NEEDED_PRODUCT.includes(props.productDetails.code)) {
        addorRemoveProduct = state.termsAccepted // not checking state.productSelected because it hasn't been updated yet
      } else {
        addorRemoveProduct = state.productSelected
      }

      const checkTerms = TOS_NEEDED_PRODUCT.includes(props.productDetails.code) && !productSubscribed

      emit('set-selected-product', {
        ...props.productDetails,
        forceRemove,
        addProductOnAccountAdmin: props.isAccountSettingsView ? addorRemoveProduct : undefined,
        termsAccepted: checkTerms ? state.termsAccepted : undefined
      })
    }

    function saveProductFee (data) {
      emit('save:saveProductFee', data)
    }

    function tosChanged (termsAccepted: boolean) {
      state.count++
      state.termsAccepted = termsAccepted
      // force select when tos accept
      selectThisProduct(undefined, true)// no need to collapse on TOS accept
    }

    function productBadge (code: string) {
      return LaunchDarklyService.getFlag(`product-${code}-status`)
    }

    function productPremTooltipText (code: string) {
      return LaunchDarklyService.getFlag(`product-${code}-prem-tooltip`)
    }

    function productDescription (code: string, description: string) {
      return productDisplay[code] || description
    }

    return {
      ...toRefs(state),
      paymentTypeIcon,
      expand,
      selectThisProduct,
      productBadge,
      productPremTooltipText,
      saveProductFee,
      paymentTypeLabel,
      productDescription
    }
  }
})
</script>

<style lang="scss" scoped>
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
    border-width: 2px !important;
  }
}

.theme--light.v-card.v-card--outlined.selected {
  top: 0;
}

.product-card-contents {
  color: $gray7;
}

.product-card ::v-deep .v-input__slot {
    align-items: flex-start !important;
}

.product-payment-icons.v-chip.v-size--x-small.theme--light.v-chip:not(.v-chip--active){
  background-color: $app-lt-blue ;
  font-size: 12px;
  color: #212529;
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

  .alert-inner {
    .v-icon {
      color: $app-alert-orange;
    }
    background-color: $BCgovGold0 !important;
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    opacity: 1 !important;
  }
  .alert__info {
    flex: 1 1 auto;
    color: $TextColorGray;
  }
</style>
