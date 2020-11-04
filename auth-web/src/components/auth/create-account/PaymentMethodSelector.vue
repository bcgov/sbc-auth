<template>
  <div>
    <p class="payment-page-sub mb-9">
      {{pageSubTitle}}
    </p>
    <PaymentMethods
      :currentOrgType="currentOrganizationType"
      :currentOrganization="currentOrganization"
      :currentSelectedPaymentMethod="currentOrgPaymentType"
      @payment-method-selected="setSelectedPayment"
      @is-pad-valid="setPADValid"
    ></PaymentMethods>
    <v-divider class="my-10"></v-divider>
     <v-row>
      <v-col class="py-0 d-inline-flex">
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
        >
          <v-icon left class="mr-2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-2 font-weight-bold"
          @click="save"
          data-test="save-button"
          :disabled="!isEnableCreateBtn"
        >
          Create Account
        </v-btn>
        <ConfirmCancelButton
          showConfirmPopup="true"
        ></ConfirmCancelButton>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Account, PaymentTypes } from '@/util/constants'
import { Component, Emit, Mixins, Prop } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import ConfirmCancelButton from '@/components/auth/common/ConfirmCancelButton.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    ConfirmCancelButton,
    PaymentMethods
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentOrganizationType',
      'currentOrgPaymentType'
    ])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationPaymentType'
    ])
  }
})
export default class PaymentMethodSelector extends Mixins(Steppable) {
  private readonly setCurrentOrganizationPaymentType!: (paymentType: string) => void
  private readonly currentOrganization!: Organization
  private readonly currentOrganizationType!: string
  private readonly currentOrgPaymentType!: string
  private selectedPaymentMethod: string = ''
  private isPADValid: boolean = false

  private goBack () {
    this.stepBack()
  }

  private get pageSubTitle () {
    return (this.currentOrganizationType === Account.UNLINKED_PREMIUM)
      ? 'Set up your pre-authorized debit account to automatically make payments when they are due.'
      : 'Select the payment method for this account.'
  }

  private get isEnableCreateBtn () {
    return (this.selectedPaymentMethod === PaymentTypes.PAD)
      ? (this.selectedPaymentMethod && this.isPADValid) : !!this.selectedPaymentMethod
  }

  private setSelectedPayment (payment) {
    this.selectedPaymentMethod = payment
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
  }

  private setPADValid (isValid) {
    this.isPADValid = isValid
  }

  private save () {
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
    this.createAccount()
  }

  @Emit('final-step-action')
  private createAccount () {
  }
}
</script>

<style lang="scss" scoped>
.payment-card {
  background-color: var(--v-grey-lighten5) !important;
  transition: all ease-out 0.2s;

  &:hover {
    border-color: var(--v-primary-base) !important;
  }

  &.selected {
    box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
  }
}

.theme--light.v-card.v-card--outlined.selected {
  border-color: var(--v-primary-base);
}

.transparent-divider {
  border-color: transparent !important;
}
</style>
