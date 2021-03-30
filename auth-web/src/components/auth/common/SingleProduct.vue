<template>
  <div>
    <template>
      <v-card
        outlined
        hover
        class="product-card py-8 px-5 mb-4 elevation-1"
        :class="[{'px-8': icon === ''}, {'processing-card' : !isRRequesting}]"
        :data-test="`div-product-${productDetails.title}`"
      >
        <div>
          <header class="d-flex align-center">
            <div class="product-icon-container mt-n2 mr-2" v-if="!isRRequesting">
              <v-icon meduim color="primary">{{icon}}</v-icon>
            </div>
            <div class="pr-8 ">
              <h3 class="title font-weight-bold product-title mt-n1">{{productDetails.title}}</h3>
              <div>{{productDetails.subtitle}}</div>
            </div>
            <v-icon large v-if="isRequestNow"
            class="ml-auto"
            @click="requestNow()">mdi-close</v-icon>
            <v-btn
            v-else
              large
              depressed
              color="primary"
              width="120"
              class="font-weight-bold ml-auto"
              :outlined="!isApproved"
              :aria-label="`Select  ${productDetails.title}`"
              :data-test="`btn-productDetails-${productDetails.title}`"
              @click="requestNow()"
            >
              <span>{{label}}</span>
            </v-btn>
          </header>

          <div class="product-card-contents">
            <v-expand-transition>
              <div v-if="isRequestNow">
                <div class="pt-7 mb-7" >
                  <v-divider class="mb-7"></v-divider>
                  <p class="mb-7">The search and registration products are intended for the exclusive use of solicitors and notaries only.
                    Title Search companies approved by the Vital Statistics Agency may also be granted access to Wills Registry.
                  </p>
                  <h4>Terms of Service</h4>
                  <p> I confirm, I <strong>{{userName}}</strong> am an authorized prime admin for this account.<br />
                    I declare that this account <strong>{{orgName}}</strong> and all team members act as a solicitor, or title search company approved by the Vital Statistics agency.</p>
                </div>
                <v-checkbox
                color="primary"
                class="terms-checkbox align-checkbox-label--top ma-0 pa-0"
                hide-details
                v-model="termsAccepted"
                required
                data-test="check-termsAccepted"
                >
                  <template v-slot:label>
                    <span class="label-color ml-2">I have read, understood and agree to the
                      I confirm that the informtion above is all correct and this account act as a solicitor,
                      notary or title search company approved by the Vital Statistics agency.
                    </span>
                </template>
                </v-checkbox>

                <v-divider class="my-7"></v-divider>
                <div class="form__btns d-flex">
                  <v-btn
                    large
                    class="request-btn"
                    color="primary"
                    :disabled="isDisableSaveBtn"
                    @click="requestProduct"
                    :loading="isLoading"
                  >
                    <span class="save-btn__label">Request</span>
                  </v-btn>

                    <v-btn
                    large
                    class="request-cancel-btn ml-3"
                    color="gray"
                    @click="cancel"
                    :loading="isLoading"
                  >
                    <span class="save-btn__label">Cancel</span>
                  </v-btn>
                </div>
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
import { productStatus } from '@/util/constants'

@Component
export default class SingleProduct extends Vue {
  @Prop({ default: undefined }) productDetails: any
  @Prop({ default: '' }) userName: string
  @Prop({ default: '' }) orgName: string
  private isRequestNow: boolean = false
  private termsAccepted: boolean = false
  public isLoading : boolean = false
  public label = 'Reqeust'
  public icon = ''
  public isApproved = false
  public isPending = false
  public isRejected = false
  public isRRequesting = false

  @Watch('productDetails')
  onProductChange (newProd:any, oldProd:any) {
    this.setupProductDetails(newProd)
  }
  get isDisableSaveBtn () {
    return false
  }

  setupProductDetails (productDetails) {
    const { status } = productDetails

    if (status === productStatus.PENDING) {
      this.label = 'Pending'
      this.icon = 'mdi-clock-outline'
      this.isPending = true
    } else if (status === productStatus.REJECTED) {
      this.label = 'Rejected'
      this.icon = 'mdi-clock-outline'
      this.isRejected = true
    } else if (status === productStatus.APPROVED) {
      this.label = 'Approved'
      this.icon = 'mdi-check-circle'
      this.isApproved = true
    } else {
      this.isRRequesting = true
    }
  }

  public mounted () {
    this.setupProductDetails(this.productDetails)
  }

  public requestNow () {
    const { status } = this.productDetails
    // need to expand only if not already requested
    if (status === '' || status === productStatus.REQUEST) {
      this.isRequestNow = !this.isRequestNow
    }
  }

  @Emit('set-selected-product')
  public requestProduct () {
    return { product: this.productDetails, termsAccepted: this.termsAccepted }
  }
  cancel () {
    this.requestNow()
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
</style>
