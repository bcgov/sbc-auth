import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-10 font-weight-bold">
      Select a payment method to unlock your account
    </p>

    <v-alert
      v-if="errorText"
      type="error"
      class="mb-11"
    >
      <div v-html="errorText" />
    </v-alert>

    <v-row class="mb-6">
      <v-col
        class="card d-flex selected"
      >
        <input
          type="radio"
          class="radio ml-6 mr-12"
          checked
        >
        <div>
          <h2>Electronic Funds Transfer</h2>
          <p>
            Follow the <span class="link">payment instruction</span> to make a payment.
            Processing may take 2-5 business days after you paid.
            You will receive an email notification once your account is unlocked.
          </p>
        </div>
      </v-col>
    </v-row>
    <v-row class="mb-6">
      <v-col
        class="card d-flex"
      >
        <input
          type="radio"
          class="radio ml-6 mr-12"
        >
        <div>
          <h2>Credit Card</h2>
          <p>Unlock your account immediately by using credit card</p>
        </div>
      </v-col>
    </v-row>
    <v-divider />
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          data-test="btn-reviewbank-back"
          @click="goBack"
        >
          <v-icon
            left
            class="mr-2 ml-n2"
          >
            mdi-arrow-left
          </v-icon>
          <span data-test="back">Back</span>
        </v-btn>
        <v-spacer />
        <!-- :disabled="!padValid" -->
        <v-btn
          large
          color="primary"
          :loading="isLoading"
          data-test="btn-reviewbank-next"
          @click="goNext"
        >
          <span data-test="next">Next</span>
          <v-icon class="ml-2">
            mdi-arrow-right
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Mixins } from 'vue-property-decorator'
import { CreateRequestBody, OrgPaymentDetails, Organization, PADInfo, PADInfoValidation } from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import { PaymentTypes } from '@/util/constants'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'
import { useOrgStore } from '@/stores/org'

@Component({
  components: {
    PADInfoForm
  },
  computed: {
    ...mapState(useOrgStore, [
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions(useOrgStore, [
      'getOrgPayments',
      'updateOrg',
      'validatePADInfo'
    ])
  }
})
export default class ReviewBankInformation extends Mixins(Steppable) {
  private readonly currentOrganization!: Organization
  private readonly updateOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  private readonly validatePADInfo!: () => Promise<PADInfoValidation>
  private readonly getOrgPayments!: () => any
  private padInfo: PADInfo = {} as PADInfo
  private padValid: boolean = false
  private refreshPAD = 0
  private orgPadInfo: PADInfo = {} as PADInfo
  private isLoading: boolean = false
  private errorText: string = ''
  private isTouched:boolean = false

  private async mounted () {
    const orgPayments: OrgPaymentDetails = await this.getOrgPayments()
    const cfsAccount = orgPayments?.cfsAccount
    this.padInfo.bankAccountNumber = cfsAccount?.bankAccountNumber
    this.padInfo.bankInstitutionNumber = cfsAccount?.bankInstitutionNumber
    this.padInfo.bankTransitNumber = cfsAccount?.bankTransitNumber
    this.padInfo.isTOSAccepted = !!(cfsAccount?.bankAccountNumber && cfsAccount?.bankInstitutionNumber && cfsAccount?.bankTransitNumber)
    this.refreshPAD++
  }

  private async goNext () {
    // if no changes in any field, no need to update data, move to next screen
    if (!this.isTouched) {
      this.stepForward()
    } else {
      this.isLoading = true
      let isValid = this.isTouched ? await this.verifyPAD() : true
      if (isValid) {
        const createRequestBody: CreateRequestBody = {
          paymentInfo: {
            paymentMethod: PaymentTypes.PAD,
            bankTransitNumber: this.padInfo.bankTransitNumber,
            bankInstitutionNumber: this.padInfo.bankInstitutionNumber,
            bankAccountNumber: this.padInfo.bankAccountNumber
          }
        }
        try {
          await this.updateOrg(createRequestBody)
          this.isLoading = false
          this.stepForward()
        } catch (error) {
          // eslint-disable-next-line no-console
          console.error(error)
          this.isLoading = false
        }
      }
    }
  }

  private goBack () {
    this.stepBack()
  }

  private getPADInfo (padInfo: PADInfo) {
    this.padInfo = padInfo
  }

  private isPADValid (isValid) {
    this.padValid = isValid
  }

  // set on change of input
  private isPadInfoTouched (isTouched) {
    this.isTouched = isTouched
  }

  private async verifyPAD () {
    this.errorText = ''
    const verifyPad: PADInfoValidation = await this.validatePADInfo()
    if (!verifyPad) {
      // proceed to next step even if the response is empty
      return true
    }

    if (verifyPad?.isValid) {
      // proceed if PAD info is valid
      return true
    }
    this.isLoading = false
    this.errorText = 'Bank information validation failed'
    if (verifyPad?.message?.length) {
      let msgList = ''
      verifyPad.message.forEach((msg) => {
        msgList += `<li>${msg}</li>`
      })
      this.errorText = `<ul class="error-list">${msgList}</ul>`
    }
    return false
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/theme.scss';

.radio {
  transform: scale(1.5);
}

.card {
  // background: red;
  box-shadow: 0 2px 1px -1px rgba(0,0,0,.2),0 1px 1px 0 rgba(0,0,0,.14),0 1px 3px 0 rgba(0,0,0,.12)!important;
  border-radius: 4px;
  padding: 32px 20px!important;
  border: thin solid rgba(0,0,0,.12);
  cursor: pointer;
  transition: all 0.3s ease;
  &:hover {
    border-color: var(--v-primary-base)!important
  }
}
.selected {
  border-color: var(--v-primary-base)!important;
}
.link {
  color: var(--v-primary-base) !important;
  text-decoration: underline;
  cursor: pointer;
}
  ::v-deep .error-list {
    margin: 0;
    padding: 0;
    list-style-type: none;
  }
</style>
