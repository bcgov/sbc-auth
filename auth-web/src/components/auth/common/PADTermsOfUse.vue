<template>
  <div>
    <v-fade-transition>
      <div class="loading-container" v-if="!termsContent">
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="termsContent"
        />
      </div>
    </v-fade-transition>
    <!-- Prototype Content -->
    <!-- This will need to be moved to the API -->
    <div class="terms-container">
      <!-- <h3>
        Business Pre-Authorized Debit Terms and Conditions Agreement BC Registries and Online Services
      </h3> -->
      <section>
        <header>
          In this agreement:
        </header>
        <p>
          “the biller” refers to “Her Majesty the Queen in Right of the Province of British Columbia as represented by the Minister of Citizen’s Services - BC Registry and Online Services (Prov of BC);
        </p>
        <p>
          “the payor” refers to the Premium Account Subscriber of the BC Registry Service as defined in the BC Registry Terms and Conditions of Agreement (the “BC Registry Terms”); and</p>
        <p>
          unless defined herein, capitalized terms in this agreement will have the meaning as set out in BC Registry Terms.
        </p>
      </section>
      <section>
      <header>
        The payor acknowledges or understands:
      </header>
      <ol>
        <li>
          That this authorization is provided for the benefit of the biller and our financial institution, and is provided in consideration of the Payor’s Financial Institution agreeing to process debits (PADs) against the bank account as indicated in the biller’s PAD application webform and in accordance with the rules of <a href="www.payments.ca" target="_blank">Payments Canada</a>.
        </li>
        <li>
          Ticking the acceptance box on the biller’s PAD application webform will be considered equivalent to my signature and will constitute valid authorization for the processing financial institution to debit the payor’s account as identified in the biller’s PAD application webform (the “Payor’s Bank Account”).
        </li>
        <li>
          This authority will remain in effect until the biller has received written communication from the payor of cancellation or changes relating to the Payor’s Bank Account.
        </li>
        <li>
          The payor may cancel this PAD agreement at any time with written notification to the biller. Written notification of changes or cancellation must be received at least 10 business days prior to the next online order or withdrawal. Notification must be in writing and sent either through the biller’s BC Registry website or by mail to the address provided below. A sample cancellation form or more information on my right to cancel a PAD Agreement can be obtained at my financial institution or by visiting <a href="www.payments.ca" target="_blank">www.payments.ca</a>.
        </li>
        <li>
          That cancellation of this agreement by the payor or the biller:
          <ol type="a">
            <li>
              will result in the suspension of the payors’ Premium Account Subscriber account Access until the payor takes action to authorize another payment method; and
            </li>
            <li>
              does not cancel any amount owed for the Service received prior to cancellation.
            </li>
          </ol>
        </li>
        <li>
          Correspondence regarding this agreement will be sent to the payor at the email address associated with the payor’s Premium Subscriber Account (the “Payor’s Email Address”). The payor agrees that any communication sent by the biller to that email address will be deemed to have been received by the payor and acknowledges that it is the payor’s responsibility to notify the biller as soon as possible of changes to the Payor’s Email Address.
        </li>
        <li>
          <strong>The biller notification of enrollment or cancellation of this Pre-Authorized Debit Agreement to the Payor is being reduced from 15 calendar days to 3 calendar days in accordance with the H1 rule of Payments Canada.  Notification will be delivered electronically to the Payor’s Email Address.</strong>
        </li>
        <li>
          The payor has certain recourse rights if any debit does not comply with the terms of this business PAD agreement (for example, the right to receive reimbursement for any PAD that is not authorized or is not consistent with terms and conditions of this PAD Agreement). To obtain a form for reimbursement or for more information on recourse rights, contact your financial institution or visit <a href="www.payments.ca" target="_blank">www.payments.ca</a>.
        </li>
        <li>
          Any payment dishonoured by the payor’s financial institution may result in a dishonoured banking instrument service fee, as prescribed by the Minister of Finance, being applied to the payor’s Premium Account Subscriber account.  The biller is not responsible for any additional service fees charged by your financial institution.
        </li>
        <li>
          In the event of a dishonoured payment, the biller reserves the right to suspend the payor’s Access until the payor has taken action to re-activate Access by paying any outstanding Fees and dishonoured banking instrument service fees by credit card.
        </li>
        <li>
          Due to a delay in payment processing, the biller may subsequently suspend the payor’s Access after a payor has taken action to re-activate Access if another PAD is dishonoured in the intervening period.
        </li>
        <li>
          The amount of the daily (excludes weekends and holidays) withdrawal is variable and dependent on the total daily Transactions charged to the payors’ Premium Account Subscriber’s account by Team Members who are authorized to order BC Registry Services.
        </li>
        <li>
          <strong>The standard 10 calendar day pre-notification period for the sporadic and variable pre-authorized withdrawals will be reduced to 1-2 business days.</strong>
        </li>
        <li>
          The biller will provide PAD pre-notification 1-2 business days prior to the withdrawal date. This notification will confirm the amount and estimated date of the pre-authorized withdrawal, will provide a list of all services ordered & other account adjustments and will be delivered electronically to the Payor’s Email Address.
        </li>
        <li>
          Your financial institution is not responsible for verifying whether payment has been issued in accordance with the particulars of this agreement.
        </li>
      </ol>
      </section>
      <section>
        <header>
          <strong>Payor Authorization:</strong>
        </header>
        <p>
          I have read, understood and agree to the terms and conditions of the Business Pre-Authorized Debit Terms and Conditions for BC Registry Services
        </p>
        <p>
          I confirm, I am an authorized representative for the payor and authorized signatory on the account to be debited under this agreement.
        </p>
        <p>
          I authorize the biller to withdraw funds from the bank account as indicated above I entered on the biller’s PAD application webform as per the terms and conditions of this agreement.
        </p>
        <p>
          Dated: Month Day, Year
        </p>
      </section>
    </div>
    <!--
    <div v-html="termsContent" class="terms-container"></div>
    -->
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import CommonUtils from '@/util/common-util'
import { TermsOfUseDocument } from '@/models/TermsOfUseDocument'
import { User } from '@/models/user'
import documentService from '@/services/document.services.ts'

@Component({
  computed: {
    ...mapState('user', [
      'termsOfUse',
      'userProfile',
      'userHasToAcceptTOS'
    ])
  },
  methods: {
    ...mapActions('user', [
      'getTermsOfUse'
    ])
  }
})
export default class PADTermsOfUse extends Vue {
  private readonly getTermsOfUse!: (docType?: string) => TermsOfUseDocument
  private termsContent = ''
  protected readonly userProfile!: User
  protected readonly userHasToAcceptTOS!: boolean

  @Prop({ default: 'termsofuse' }) tosType: string

  async mounted () {
    const termsOfService = await this.getTermsOfUse(this.tosType)
    this.termsContent = termsOfService.content
    const hasLatestTermsAccepted = this.hasAcceptedLatestTos(termsOfService.versionId)
    if (!hasLatestTermsAccepted) {
      this.$emit('tos-version-updated')
    }
  }

  private hasAcceptedLatestTos (latestVersionId: string) {
    /*
    version id comes with a string prefix like d1 , d2... strip that , convert to number for comparison
    Or else 'd1' will be,l 'd2' . But 'd2' wont be less than ' d10 '!!!  '
    */

    const userTOS = this.userProfile?.userTerms?.termsOfUseAcceptedVersion

    if (!userTOS) {
      return true
    }
    const currentlyAcceptedTermsVersion = CommonUtils.extractAndConvertStringToNumber(userTOS)
    const latestVersionNumber = CommonUtils.extractAndConvertStringToNumber(latestVersionId)
    return (currentlyAcceptedTermsVersion > latestVersionNumber)
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';

// Terms and Conditions Container
$indent-width: 1rem;

.terms-container {
  p, li {
    margin: 1rem 0;
  }

  ol {
    margin-left: $indent-width;
  }

  li {
    padding-left: $indent-width;
  }

  h3 {
    max-width: 55ch;
  }

  section {
    margin-bottom: 2rem;
  }

  section:last-child {
    margin-bottom: 0;
  }

  section header {
    margin-bottom: 1rem;
    color: $gray9;
    font-size: 1rem;
    font-weight: 700;
  }

  section header > span {
    display: inline-block;
    width: $indent-width;
  }

  header + div {
    margin-left: 3.25rem;
  }

  section div > p {
    padding-left: $indent-width;
  }

  p {
    position: relative;
  }

  p + div {
    margin-left: $indent-width;
  }

  p > span {
    position: absolute;
    top: 0;
    left: 0;
  }
}
</style>
