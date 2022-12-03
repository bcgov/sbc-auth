<template>
  <div v-can:CHANGE_PAD_INFO.disable.card>
    <template v-if="isAcknowledgeNeeded">
      <p class="mb-6">
        The Canadian Payment Association requires a confirmation period
        of (3) days prior to your first pre-authorized debit deduction.
        The administrator of this account will receive a written confirmation
        of your pre-authorized debit agreement prior to the first deduction.
      </p>
      <p class="mb-10 font-weight-bold">
        {{padInfoSubtitle}}
      </p>
    </template>
    <v-form ref="preAuthDebitForm">
      <section>
        <header class="mb-4 d-flex align-content-center">
          <div data-test="pad-info-form-title" class="mr-1 font-weight-bold">Banking Information</div>
          <v-btn
            small
            icon
            color="primary"
            class="help-btn"
            aria-label="How to locate your banking information"
            @click.stop="bankInfoDialog = true"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
          </v-btn>
          <v-dialog
            v-model="bankInfoDialog"
            max-width="800"
          >
            <v-card>
              <v-card-title>
                <h2 class="title font-weight-bold">How to locate your account information</h2>
                <v-btn
                  icon
                  @click="bankInfoDialog = false"
                >
                  <v-icon>mdi-close</v-icon>
                </v-btn>
              </v-card-title>
              <v-card-text>
                <v-img src="../../../assets/img/cheque-sample.jpg" lazy-src></v-img>
                <ol class="my-4">
                  <li>Cheque number - not required</li>
                  <li>Transit (branch) number - 5 digits</li>
                  <li>Bank (institution) number - 3 digits</li>
                  <li>Bank account number - as shown on your cheque</li>
                </ol>
              </v-card-text>
            </v-card>
          </v-dialog>
        </header>
        <v-row>
          <v-col cols="6" class="py-0">
            <v-text-field
              label="Transit Number"
              filled
              hint="5 digits"
              persistent-hint
              :rules="transitNumberRules"
              v-model="transitNumber"
              @change="emitPreAuthDebitInfo"
              v-mask="'#####'"
              data-test="input-transitNumber"
            ></v-text-field>
          </v-col>
          <v-col cols="6" class="py-0">
            <v-text-field
              label="Institution Number"
              filled
              hint="3 digits"
              persistent-hint
              :rules="institutionNumberRules"
              v-model="institutionNumber"
              @change="emitPreAuthDebitInfo"
              v-mask="'###'"
              data-test="input-institutionNumber"
            ></v-text-field>
          </v-col>
          <v-col cols="12" class="py-0">
            <v-text-field
              label="Account Number"
              filled
              hint="7 to 12 digits"
              persistent-hint
              :rules="accountNumberRules"
              v-model="accountNumber"
              @change="emitPreAuthDebitInfo"
              data-test="input-accountNumber"
              v-mask="accountMask">
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row v-if="isAcknowledgeNeeded">
          <v-col class="pt-2 pl-6 pb-0">
            <v-checkbox
              hide-details
              class="align-checkbox-label--top"
              v-model="isAcknowledged"
              @change="emitPreAuthDebitInfo"
              data-test="check-isAcknowledged"
            >
              <template v-slot:label>
                {{acknowledgementLabel}}
              </template>
            </v-checkbox>
          </v-col>
        </v-row>
        <v-row v-if="isTOSNeeded">
          <v-col class="pt-6 pl-6">
            <div class="terms-container">
              <TermsOfUseDialog
                :isAlreadyAccepted="isTermsOfServiceAccepted"
                @terms-acceptance-status="isTermsAccepted"
                :tosType="'termsofuse_pad'"
                :tosHeading="'Business Pre-Authorized Debit Terms and Conditions Agreement BC Registries and Online Services'"
                :tosCheckBoxLabelAppend="'of the Business Pre-Authorized Debit Terms and Conditions for BC Registry Services'"
              ></TermsOfUseDialog>
            </div>
          </v-col>
        </v-row>
      </section>
    </v-form>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import { Account } from '@/util/constants'
import CommonUtils from '@/util/common-util'
import { PADInfo } from '@/models/Organization'
import TermsOfUseDialog from '@/components/auth/common/TermsOfUseDialog.vue'
import { mask } from 'vue-the-mask'

@Component({
  directives: {
    mask
  },
  components: {
    TermsOfUseDialog
  },
  computed: {
    ...mapState('org', [
      'currentOrgPADInfo',
      'currentOrganizationType'
    ])
  },
  methods: {
    ...mapMutations('org', [
      'setCurrentOrganizationPADInfo'
    ])
  }
})
export default class PADInfoForm extends Vue {
  @Prop({ default: () => ({} as PADInfo) }) padInformation: any
  @Prop({ default: false }) isChangeView: boolean
  @Prop({ default: true }) isAcknowledgeNeeded: boolean
  @Prop({ default: true }) isTOSNeeded: boolean
  @Prop({ default: false }) isInitialTOSAccepted: boolean
  @Prop({ default: false }) isInitialAcknowledged: boolean
  @Prop({ default: false }) clearOnEdit: boolean
  private readonly currentOrgPADInfo!: PADInfo
  private readonly currentOrganizationType!: string
  private readonly setCurrentOrganizationPADInfo!: (padInfo: PADInfo) => void
  private transitNumber: string = ''
  private institutionNumber: string = ''
  private accountNumber: string = ''
  private isTOSAccepted: boolean = false
  private isAcknowledged: boolean = false
  private isTouched: boolean = false
  private isStartedEditing: boolean = false
  private bankInfoDialog: boolean = false

  $refs: {
    preAuthDebitForm: HTMLFormElement,
  }

  private transitNumberRules = [
    v => !!v || 'Transit Number is required',
    v => (v.length >= 4) || 'Transit Number should be minimum of 4 digits'
  ]

  private institutionNumberRules = [
    v => !!v || 'Institution Number is required',
    v => (v.length === 3) || 'Institution Number should be 3 digits'
  ]

  private accountNumberRules = [
    v => !!v || 'Account Number is required',
    v => (v.length >= 7 && v.length <= 12) || 'Account Number should be between 7 to 12 digits'
  ]

  private accountMask = CommonUtils.accountMask()

  public constructor () {
    super()
    this.isAcknowledged = this.isInitialAcknowledged
  }

  private mounted () {
    const padInfo: PADInfo = (Object.keys(this.padInformation).length) ? this.padInformation : this.currentOrgPADInfo
    this.transitNumber = padInfo?.bankTransitNumber || ''
    this.institutionNumber = padInfo?.bankInstitutionNumber || ''
    this.accountNumber = padInfo?.bankAccountNumber || ''
    this.isTOSAccepted = this.isInitialTOSAccepted || (padInfo?.isTOSAccepted || false)
    this.setCurrentOrganizationPADInfo(padInfo)
    this.$nextTick(() => {
      if (this.isTOSAccepted) {
        this.isPreAuthDebitFormValid()
      }
    })
  }

  private get isTermsOfServiceAccepted () {
    if (this.isInitialTOSAccepted && !this.isStartedEditing) { // if TOS already accepted
      return true
    }
    return (Object.keys(this.padInformation).length) ? this.padInformation.isTOSAccepted : this.currentOrgPADInfo?.isTOSAccepted
  }

  private get padInfoSubtitle () {
    return (this.showPremiumPADInfo)
      ? 'Services will continue to be billed to the linked BC Online account until the mandatory (3) day confirmation period has ended.'
      : 'This account will not be able to perform any transactions until the mandatory (3) day confirmation period has ended.'
  }

  private get acknowledgementLabel () {
    // for Premium accounts, the label should mention that it will charge from BCOL till PAD is done.
    return (this.showPremiumPADInfo)
      ? 'I understand that services will continue to be billed to the linked BC Online account until the mandatory (3) day confirmation period has ended.'
      : 'I understand that this account will not be able to perform any transactions until the mandatory (3) day confirmation period for pre-authorized debit has ended.'
  }

  private get showPremiumPADInfo () {
    return this.isChangeView
  }

  @Emit()
  private async emitPreAuthDebitInfo () {
    if (!this.isStartedEditing) { // clear check needed only if user not started editing
      await this.formClear() // await till decide
    }

    const padInfo: PADInfo = {
      bankTransitNumber: this.transitNumber,
      bankInstitutionNumber: this.institutionNumber,
      bankAccountNumber: this.accountNumber,
      isTOSAccepted: this.isTOSAccepted,
      isAcknowledged: this.isAcknowledged
    }
    this.isPreAuthDebitFormValid()
    this.setCurrentOrganizationPADInfo(padInfo)
    this.isTouched = true
    this.isPadInfoTouched()
    return padInfo
  }

  formClear () {
    // Clearing form when user touch any field first time
    if (this.clearOnEdit && !this.isStartedEditing) {
      // setting edited value if edited first time
      const padInfo: PADInfo = (Object.keys(this.padInformation).length) ? this.padInformation : this.currentOrgPADInfo
      this.transitNumber = padInfo?.bankTransitNumber !== this.transitNumber ? this.transitNumber : ''
      this.institutionNumber = padInfo?.bankInstitutionNumber !== this.institutionNumber ? this.institutionNumber : ''
      this.accountNumber = /X/.test(this.accountNumber) ? '' : this.accountNumber // test account number contain X, then clear all else leave as it is
      // this.isAcknowledged = false
      this.isTOSAccepted = false
      this.isStartedEditing = true
    }
  }

  @Emit()
  private isPreAuthDebitFormValid () {
    const acknowledge = (this.isAcknowledgeNeeded) ? this.isAcknowledged : true
    const tosAccepted = (this.isTOSNeeded) ? this.isTOSAccepted : true
    return (this.$refs.preAuthDebitForm?.validate() && tosAccepted && acknowledge) || false
  }

  @Emit()
  private isPadInfoTouched () {
    return this.isTouched
  }

  private isTermsAccepted (isAccepted) {
    this.isTOSAccepted = isAccepted
    this.isTouched = true
    this.emitPreAuthDebitInfo()
  }
}
</script>

<style lang="scss" scoped>
  .align-checkbox-label--top {
    ::v-deep {
      .v-input__slot {
        align-items: flex-start;
      }
    }
  }

  .v-input--checkbox {
    color: var(--v-grey-darken4) !important;
  }

  ::v-deep {
    .v-input--checkbox .v-label {
      color: var(--v-grey-darken4) !important;
    }
  }

  .help-btn {
    margin-top: -2px;
  }
</style>
