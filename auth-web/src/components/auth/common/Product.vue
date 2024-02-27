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
import { Component, Emit, Mixins, Prop, Watch } from 'vue-property-decorator'
import { DisplayModeValues, Product as ProductEnum, ProductStatus } from '@/util/constants'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ProductFee from '@/components/auth/common/ProductFeeViewEdit.vue'
import ProductTos from '@/components/auth/common/ProductTOS.vue'

const TOS_NEEDED_PRODUCT = ['VS']

@Component({
  components: {
    ProductTos,
    ProductFee
  }
})
export default class Product extends Mixins(AccountMixin) {
  @Prop({ default: undefined }) productDetails: OrgProduct
  @Prop({ default: undefined }) activeSubProduct: OrgProduct
  @Prop({ default: undefined }) orgProduct: AccountFee // product available for orgs
  @Prop({ default: undefined }) orgProductFeeCodes: OrgProductFeeCode // product
  @Prop({ default: false }) isProductActionLoading: boolean // loading
  @Prop({ default: false }) isProductActionCompleted: boolean // loading

  @Prop({ default: '' }) userName: string
  @Prop({ default: '' }) orgName: string
  @Prop({ default: false }) isSelected: boolean
  @Prop({ default: false }) isexpandedView: boolean
  @Prop({ default: false }) isAccountSettingsView: boolean // to confirm if the rendering is from AccountSettings view
  @Prop({ default: false }) isBasicAccount: boolean // to confirm if the current organization is basic and the product instance is premium only
  @Prop({ default: false }) canManageProductFee: boolean

  private termsAccepted: boolean = false
  public productSelected:boolean = false
  viewOnly = DisplayModeValues.VIEW_ONLY

  $refs: {
    tosForm: HTMLFormElement
  }

  @Watch('isSelected')
  onisSelectedChange (newValue:boolean) {
    // setting check box
    this.productSelected = newValue
  }
  get showProductFee () {
    return this.canManageProductFee && this.orgProduct && this.orgProduct.product
  }

  get productLabel () {
    // this is mapping product code with lang file.
    // lang file have subtitle and description with product code prefix.
    // eg: pprCodeSubtitle, pprCodeDescription
    // Also, returns check box icon and color if the product has been reviewed.
    let { code } = this.productDetails
    let subTitle = `${code?.toLowerCase()}CodeSubtitle`
    let details = `${code?.toLowerCase()}CodeDescription`
    let note = `${code?.toLowerCase()}CodeNote`
    let decisionMadeIcon = null
    let decisionMadeColorCode = null

    if (this.isAccountSettingsView) {
      const status = this.productDetails.subscriptionStatus
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
      if (this.isBasicAccountAndPremiumProduct) {
        subTitle = `${code?.toLowerCase()}CodeUnselectableSubtitle`
        decisionMadeIcon = 'mdi-minus-box'
      }
      // Swap subtitle and details for sub-product specific content
      if (this.productDetails.code === ProductEnum.MHR && this.activeSubProduct?.subscriptionStatus === ProductStatus.ACTIVE) {
        subTitle = `mhrQsCodeActiveSubtitle`
        details = `${this.activeSubProduct.code?.toLowerCase()}CodeDescription`
        note = ''
      }
    }
    return { subTitle, details, decisionMadeIcon, decisionMadeColorCode, note }
  }

  get isTOSNeeded () {
    // check tos needed for product
    return TOS_NEEDED_PRODUCT.includes(this.productDetails.code)
  }

  get isBasicAccountAndPremiumProduct () {
    return this.isBasicAccount && this.productDetails.premiumOnly
  }

  get hasDecisionNotBeenMade () {
    // returns true if create account flow
    if (!this.isAccountSettingsView) {
      return true
    }
    // returns true if product subscription status is unsubscribed and in account settings view
    if (([ProductStatus.NOT_SUBSCRIBED] as Array<string>).includes(this.productDetails.subscriptionStatus)) {
      return true
    }
    this.termsAccepted = true
    return false
  }

  public mounted () {
    this.productSelected = this.isSelected
  }

  @Emit('toggle-product-details')
  public expand () {
    // emit selected product code to controll expand all product
    return this.isexpandedView ? '' : this.productDetails.code
  }

  public tosChanged (termsAccepted:boolean) {
    this.termsAccepted = termsAccepted
    // force select when tos accept
    this.selecThisProduct(undefined, true)// no need to collaps on TOS accept
  }
  // // this function will only used when we have to show TOS (in product and service dashboard)

  // since event is first argument, we are using second to set emitFromTos
  @Emit('set-selected-product')
  // eslint-disable-next-line
  public selecThisProduct (event, emitFromTos:boolean = false) {

    let forceRemove = false
    // expand if tos needed
    // as per new requirment, show expanded when user tries to click checkbox and not accepted TOS.
    // need to collapse on uncheck. Since both are using same function emitFromTos will be true when
    // click happend from TOS check box. then no need to collapse
    if (this.isTOSNeeded && !this.termsAccepted) {
      if (!emitFromTos) { // expand and collapse on click if click is not coming from TOS
        this.expand()
      }
      this.productSelected = false
      // wait till user approve TOS or remove product selection from array if tos not accepted
      forceRemove = true
    }
    return { ...this.productDetails, forceRemove }
  }

  // if TOS needed will inject component
  // in future can use different components for different product
  get productFooter () {
    return {
      id: 'tos',
      component: ProductTos,
      props: {
        userName: this.userName,
        orgName: this.orgName,
        isTOSAlreadyAccepted: this.termsAccepted
      },
      events: { 'tos-status-changed': this.tosChanged },
      ref: 'tosForm'
    }
  }

  @Emit('save:saveProductFee')
  saveProductFee (data) {
    return data
  }

  public productBadge (code: string) {
    return LaunchDarklyService.getFlag(`product-${code}-status`)
  }

  public productPremTooltipText (code: string) {
    return LaunchDarklyService.getFlag(`product-${code}-prem-tooltip`)
  }
}
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
