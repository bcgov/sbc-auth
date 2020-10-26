<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-6">
      <h2 class="view-header__title" data-test="account-settings-title">
        Payment Methods
      </h2>
      <p class="mt-3 payment-page-sub">
        Manage your pre-authorized debit payments for this account.
      </p>
    </div>
    <PaymentMethods
      v-if="selectedPaymentMethod"
      :currentOrgType="savedOrganizationType"
      :currentOrganization="currentOrganization"
      :currentSelectedPaymentMethod="selectedPaymentMethod"
      @payment-method-selected="setSelectedPayment"
    ></PaymentMethods>
    <v-divider class="my-10"></v-divider>
     <v-row>
      <v-col class="py-0 d-inline-flex">
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          class="save-continue-button mr-2 font-weight-bold"
          @click="save"
          data-test="save-button"
          :disabled="!selectedPaymentMethod"
        >
          Save
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import { Account } from '@/util/constants'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import OrgModule from '@/store/modules/org'
import { Organization } from '@/models/Organization'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    PaymentMethods
  },
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationPaymentType'
    ]),
    ...mapActions('org', [
      'getOrgPayments'
    ])
  }
})
export default class AccountPaymentMethods extends Mixins(AccountChangeMixin) {
  private readonly setCurrentOrganizationPaymentType!: (paymentType: string) => void
  private readonly getOrgPayments!: () => any
  private readonly currentOrganization!: Organization
  private savedOrganizationType: string = ''
  private selectedPaymentMethod: string = ''

  private setSelectedPayment (payment) {
    this.selectedPaymentMethod = payment
  }

  private async mounted () {
    this.setAccountChangedHandler(await this.initialize)
    await this.initialize()
  }

  private async initialize () {
    this.savedOrganizationType =
      ((this.currentOrganization?.orgType === Account.PREMIUM) && !this.currentOrganization?.bcolAccountId)
        ? Account.UNLINKED_PREMIUM : this.currentOrganization.orgType
    const orgPayments = await this.getOrgPayments()
    this.selectedPaymentMethod = orgPayments?.paymentMethod || ''
  }

  private save () {
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
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
