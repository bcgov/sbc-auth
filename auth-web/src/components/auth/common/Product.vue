<template>
  <div>
    <template>
      <v-card
        outlined
        hover
        class="product-card py-8 px-5 mb-4 elevation-1"
        :class="[ {'processing-card' : isSelected}]"
        :data-test="`div-product-${productDetails.code}`"
      >
        <div>
          <header class="d-flex align-center">
            <div class="pr-8 ">
              <v-checkbox
                color="primary"
                class="align-checkbox-label--top ma-0 pa-0"
                hide-details
                v-model="productSelected"
                :indeterminate="isexpandedView && isTOSNeeded && !termsAccepted"
                :data-test="`check-product-${productDetails.code}`"
                @change="selecThisProduct"
                :key="Math.random()"
              >
                <template v-slot:label>
                  <div class="ml-2">
                    <h3 class="title font-weight-bold product-title mt-n1" :data-test="productDetails.code">{{productDetails.description}}</h3>
                    <p v-if="$te(productLabel.subTitle)" v-html="$t(productLabel.subTitle)"/>
                  </div>
              </template>
              </v-checkbox>
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

              <span v-if="isexpandedView" :data-test="`span-readless-${productDetails.code}`">Read Less<v-icon meduim color="primary">mdi-chevron-up</v-icon></span>
              <span :data-test="`span-readmore-${productDetails.code}`" v-else>Read More<v-icon meduim color="primary">mdi-chevron-down</v-icon></span>
            </v-btn>
          </header>

          <div class="product-card-contents ml-9">
            <v-expand-transition>
              <div v-if="isexpandedView" :data-test="`div-expanded-product-${productDetails.code}`">
                <p v-if="$te(productLabel.details)"  v-html="$t(productLabel.details)"/>
                <component
                  v-if="isTOSNeeded"
                  :key="productFooter.id"
                  :is="productFooter.component"
                  v-bind="productFooter.props"
                  v-on="productFooter.events"
                  :ref="productFooter.ref"
                />
              </div>
            </v-expand-transition>
          </div>
        </div>
      </v-card>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { OrgProduct } from '@/models/Organization'
import ProductTos from '@/components/auth/common/ProductTOS.vue'

const TOS_NEEDED_PRODUCT = ['VS']

@Component({
  components: {
    ProductTos
  }
})
export default class Product extends Vue {
  @Prop({ default: undefined }) productDetails: OrgProduct
  @Prop({ default: '' }) userName: string
  @Prop({ default: '' }) orgName: string
  @Prop({ default: false }) isSelected: boolean
  @Prop({ default: false }) isexpandedView: boolean

  private termsAccepted: boolean = false
  public productSelected:boolean = false

  $refs: {
    tosForm: HTMLFormElement
  }

  @Watch('isSelected')
  onisSelectedChange (newValue:boolean) {
    // setting check box
    this.productSelected = newValue
  }

  get productLabel () {
    // this is mapping product code with lang file.
    // lang file have subtitle and description with product code prefix.
    // eg: pprCodeSubtitle, pprCodeDescription
    const { code } = this.productDetails
    const subTitle = `${code && code.toLowerCase()}CodeSubtitle` || ''
    const details = `${code && code.toLowerCase()}CodeDescription` || ''
    return { subTitle, details }
  }

  get isTOSNeeded () {
    // check tos needed for product
    return TOS_NEEDED_PRODUCT.includes(this.productDetails.code)
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
    // need to collaps on uncheck. Since both are using same function emitFromTos will be true when click happend from TOS check box. then no need to collaps
    if (this.isTOSNeeded && !this.termsAccepted) {
      if (!emitFromTos) { // expand and collaps on click if click is not coming from TOS
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
        orgName: this.orgName
      },
      events: { 'tos-status-changed': this.tosChanged },
      ref: 'tosForm'
    }
  }
}
</script>

<style lang="scss" scoped>

.product-card {
  transition: all ease-out 0.2s;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.selected {
    box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
  &.processing-card{
    border-color: var(--v-primary-base) !important;
  }
}

.theme--light.v-card.v-card--outlined.selected {
  border-color: var(--v-primary-base);
}

</style>
