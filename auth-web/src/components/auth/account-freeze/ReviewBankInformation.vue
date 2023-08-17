import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-10">
      Please review your pre-authorized debit information. If anything is wrong please edit your information.
    </p>

    <v-alert
      v-if="errorText"
      type="error"
      class="mb-11"
    >
      <div v-html="errorText" />
    </v-alert>

    <v-row class="mb-12">
      <v-col
        md="10"
        class="py-0"
      >
        <PADInfoForm
          :key="refreshPAD"
          :padInformation="padInfo"
          :isAcknowledgeNeeded="false"
          :isTOSNeeded="false"
          :clearOnEdit="true"
          @is-pre-auth-debit-form-valid="isPADValid"
          @emit-pre-auth-debit-info="getPADInfo"
          @is-pad-info-touched="isPadInfoTouched"
        />
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
        <v-btn
          large
          color="primary"
          :disabled="!padValid"
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
import { mapActions, mapState } from 'vuex'
import PADInfoForm from '@/components/auth/common/PADInfoForm.vue'
import { PaymentTypes } from '@/util/constants'
import Steppable from '@/components/auth/common/stepper/Steppable.vue'

@Component({
  components: {
    PADInfoForm
  },
  computed: {
    ...mapState('org', [
      'currentOrganization'
    ])
  },
  methods: {
    ...mapActions('org', [
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
  ::v-deep .error-list {
    margin: 0;
    padding: 0;
    list-style-type: none;
  }
</style>
