<template>
  <div>
    <template>
      <v-card
        outlined
        hover
        class="product-card py-8 px-5 mb-4 elevation-1"
        :class="[ {'processing-card' : isSelected}]"
        :data-test="`div-product-${productDetails.description}`"
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
                :data-test="`check-product-${productDetails.description}`"
                @change="selecThisProduct"
                :key="Math.random()"
              >
                <template v-slot:label>
                  <div class="ml-2">
                    <h3 class="title font-weight-bold product-title mt-n1">{{productDetails.description}}</h3>
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
              :data-test="`btn-productDetails-${productDetails.description}`"
              text
              @click="expand()"
            >

              <span v-if="isexpandedView">Read Less <v-icon meduim color="primary">mdi-chevron-up</v-icon></span>
              <span v-else>Read More <v-icon meduim color="primary">mdi-chevron-down</v-icon></span>
            </v-btn>
          </header>

          <div class="product-card-contents ml-9">
            <v-expand-transition>
              <div v-if="isexpandedView" >
                <p v-if="$te(productLabel.details)"  v-html="$t(productLabel.details)"/>
                  <component
                    v-if="isTOSNeeded"
                    :key="productTOS.id"
                    :is="productTOS.component"
                    v-bind="productTOS.props"
                    v-on="productTOS.events"
                    :ref="productTOS.ref"
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

// import { productStatus } from '@/util/constants'

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
  public isLoading : boolean = false
  public abcd:boolean = false

  public productSelected:boolean = false
public newproductSelected = 'tes'
  $refs: {
    tosForm: HTMLFormElement
  }

  @Watch('isSelected')
  onisSelectedChange (newValue:boolean) {
    // setting check box
    this.productSelected = newValue
  }

  get productLabel () {
    const { code } = this.productDetails
    const subTitle = `${code && code.toLowerCase()}CodeSubtitle` || ''
    const details = `${code && code.toLowerCase()}CodeDescription` || ''

    return { subTitle, details }
  }

  // if TOS needed will inject component
  // in future can use different components for different product
  get productTOS () {
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

  get isTOSNeeded () {
    // move this to constant file if API is not returning flag
    return this.productDetails.code.includes('VS')
  }

  public mounted () {
    this.productSelected = this.isSelected
  }

  @Emit('toggle-product-details')
  public expand () {
    return this.isexpandedView ? '' : this.productDetails.code
  }

  public tosChanged (termsAccepted:boolean) {
    this.termsAccepted = termsAccepted
    this.selecThisProduct()
  }
  // // this function will only used when we have to show TOS (in product and service dashboard)
  @Emit('set-selected-product')
  public selecThisProduct () {
    let forceRemove = false
    if (this.isTOSNeeded && !this.termsAccepted) {
      if (!this.isexpandedView) {
        this.expand()
      }
      this.productSelected = false
      forceRemove = true
    }
    return { ...this.productDetails, forceRemove }
  }
}
</script>

<style lang="scss" scoped>
.form__btns {
  display: flex;
  flex-direction: row;
  justify-content: flex-end;
  align-items: center;
  margin-top: 2rem;

  .v-btn {
    width: 6rem;
  }
}

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

.product-icon-container {
  flex: 0 0 auto;
}
.label-color {
  color:  rgba(0,0,0,.87) !important;
}
.pad-form-container {
  max-width: 75ch;
}
.terms-error{
  color: var(--v-error-base) !important;
  font-size: 16px;
  font-weight: bold;
  display: flex;
}
.error-color{
  color: var(--v-error-base) !important;
}
</style>
