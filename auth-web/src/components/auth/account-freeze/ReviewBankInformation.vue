import { AccessType } from '@/util/constants'
<template>
  <div>
    <p class="mb-4">Please review your pre-authorized debit information. If anything is wrong please edit your information.</p>
    <v-row class="mb-12 pb-12">
      <v-col md="10">
        <PADInfoForm
          :padInformation="padInfo"
          @is-pre-auth-debit-form-valid="isPADValid"
          @emit-pre-auth-debit-info="getPADInfo"
          :isAcknowledgeNeeded="false"
          :isTOSNeeded="false"
          :key="refreshPAD"
        ></PADInfoForm>
      </v-col>
    </v-row>
    <v-divider></v-divider>
    <v-row>
      <v-col
        cols="12"
        class="mt-5 pb-0 d-inline-flex"
      >
        <v-btn
          large
          depressed
          color="default"
          @click="goBack"
        >
          <v-icon left class="mr-2 ml-n2">mdi-arrow-left</v-icon>
          <span>Back</span>
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn
          large
          color="primary"
          @click="goNext"
          :disabled="!padValid"
        >
          <span>Next</span>
          <v-icon class="ml-2">mdi-arrow-right</v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { CreateRequestBody, OrgPaymentDetails, Organization, PADInfo } from '@/models/Organization'
import { mapActions, mapMutations, mapState } from 'vuex'
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
      'updateOrg'
    ])
  }
})
export default class ReviewBankInformation extends Mixins(Steppable) {
  private readonly currentOrganization!: Organization
  private readonly updateOrg!: (requestBody: CreateRequestBody) => Promise<Organization>
  private readonly getOrgPayments!: () => any
  private padInfo: PADInfo = {} as PADInfo
  private padValid: boolean = false
  private refreshPAD = 0
  private orgPadInfo: PADInfo = {} as PADInfo

  private async mounted () {
    const orgPayments: OrgPaymentDetails = await this.getOrgPayments()
    // eslint-disable-next-line no-console
    console.log(orgPayments)
    const cfsAccount = orgPayments?.cfsAccount
    this.padInfo.bankAccountNumber = cfsAccount?.bankAccountNumber
    this.padInfo.bankInstitutionNumber = cfsAccount?.bankInstitutionNumber
    this.padInfo.bankTransitNumber = cfsAccount?.bankTransitNumber
    // eslint-disable-next-line no-console
    // console.log(this.orgPadInfo)
    // this.padInfo = { ...this.orgPadInfo }
    this.padInfo.isTOSAccepted = !!(cfsAccount?.bankAccountNumber && cfsAccount?.bankInstitutionNumber && cfsAccount?.bankTransitNumber)
    this.refreshPAD++
  }

  private async goNext () {
    // eslint-disable-next-line no-console
    console.log(this.orgPadInfo, this.padInfo)
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
      this.stepForward()
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error(error)
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
}
</script>
