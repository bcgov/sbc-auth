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
      :isChangeView="true"
      :isAcknowledgeNeeded="isAcknowledgeNeeded"
      @payment-method-selected="setSelectedPayment"
    ></PaymentMethods>
    <v-divider class="my-10"></v-divider>
    <div class="form__btns d-flex">
      <v-btn
        large
        class="save-btn"
        v-bind:class="{ 'disabled': isBtnSaved }"
        :color="isBtnSaved ? 'success' : 'primary'"
        :disabled="disableSaveBtn"
        @click="save"
      >
        <v-expand-x-transition>
          <v-icon v-show="isBtnSaved">mdi-check</v-icon>
        </v-expand-x-transition>
        <span class="save-btn__label">{{ (isBtnSaved) ? 'Saved' : 'Save' }}</span>
      </v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Account, Pages } from '@/util/constants'
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { CreateRequestBody, Member, MembershipType, Organization } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import OrgModule from '@/store/modules/org'
import PaymentMethods from '@/components/auth/common/PaymentMethods.vue'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    PaymentMethods
  },
  computed: {
    ...mapState('org', [
      'currentOrganization',
      'currentOrgPaymentType',
      'currentMembership'
    ])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationPaymentType'
    ]),
    ...mapActions('org', [
      'getOrgPayments',
      'updateOrg'
    ])
  }
})
export default class AccountPaymentMethods extends Mixins(AccountChangeMixin) {
  private readonly setCurrentOrganizationPaymentType!: (paymentType: string) => void
  private readonly getOrgPayments!: () => any
  private readonly updateOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  private readonly currentMembership!: Member
  private readonly currentOrganization!: Organization
  private readonly currentOrgPaymentType!: string
  private savedOrganizationType: string = ''
  private selectedPaymentMethod: string = ''
  private isBtnSaved = false
  private disableSaveBtn = false

  private setSelectedPayment (payment) {
    this.selectedPaymentMethod = payment
  }

  private async mounted () {
    this.setAccountChangedHandler(await this.initialize)
    await this.initialize()
  }

  private get isAcknowledgeNeeded () {
    return (this.selectedPaymentMethod !== this.currentOrgPaymentType)
  }

  private async initialize () {
    if (this.isPaymentViewAllowed) {
      this.savedOrganizationType =
      ((this.currentOrganization?.orgType === Account.PREMIUM) && !this.currentOrganization?.bcolAccountId)
        ? Account.UNLINKED_PREMIUM : this.currentOrganization.orgType
      const orgPayments = await this.getOrgPayments()
      this.selectedPaymentMethod = orgPayments?.paymentMethod || ''
    } else {
      // if the account switing happening when the user is already in the transaction page,
      // redirect to account info if its a basic account
      this.$router.push(`/${Pages.MAIN}/${this.currentOrganization.id}/settings/account-info`)
    }
  }

  private get isPaymentViewAllowed (): boolean {
    return (this.currentMembership.membershipTypeCode === MembershipType.Admin)
  }

  private async save () {
    this.isBtnSaved = false
    this.setCurrentOrganizationPaymentType(this.selectedPaymentMethod)
    const createRequestBody: CreateRequestBody = {
      paymentInfo: {
        paymentMethod: this.selectedPaymentMethod
      }
    }
    try {
      await this.updateOrg(createRequestBody)
      this.isBtnSaved = true
      this.initialize()
    } catch (error) {
      this.isBtnSaved = false
    }
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

.save-btn.disabled {
  pointer-events: none;
}
</style>
