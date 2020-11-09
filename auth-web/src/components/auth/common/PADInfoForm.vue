<template>
  <div>
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
      <fieldset>
        <legend class="mb-4">Banking Information</legend>
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
              v-mask="'####'"
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
              v-mask="'############'"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-row>
          <v-col class="pt-6 pl-6 pb-0">
            <div class="terms-container">
              <TermsOfUseDialog
                :isAlreadyAccepted="isTermsOfServiceAccepted"
                @terms-acceptance-status="isTermsAccepted"
              ></TermsOfUseDialog>
            </div>
          </v-col>
        </v-row>
        <v-row v-if="isAcknowledgeNeeded">
          <v-col class="pt-2 pl-6 pb-0">
            <v-checkbox
              class="acknowledge-checkbox"
              v-model="isAcknowledged"
              @change="emitPreAuthDebitInfo"
            >
              <template v-slot:label>
                {{acknowledgementLabel}}
              </template>
            </v-checkbox>
          </v-col>
        </v-row>
      </fieldset>
    </v-form>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
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
      'currentOrgPADInfo'
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
  private readonly currentOrgPADInfo!: PADInfo
  private readonly setCurrentOrganizationPADInfo!: (padInfo: PADInfo) => void
  private transitNumber: string = ''
  private institutionNumber: string = ''
  private accountNumber: string = ''
  private isTOSAccepted: boolean = false
  private isAcknowledged: boolean = false

  $refs: {
    preAuthDebitForm: HTMLFormElement,
  }

  private transitNumberRules = [
    v => !!v || 'Transit Number is required',
    v => (v.length === 5) || 'Transit Number should be 5 digits'
  ]

  private institutionNumberRules = [
    v => !!v || 'Institution Number is required',
    // TODO: change to 3 once get the confirmation from CAS
    v => (v.length === 4) || 'Institution Number should be 3 digits'
  ]

  private accountNumberRules = [
    v => !!v || 'Account Number is required',
    v => (v.length >= 7 && v.length <= 12) || 'Account Number should be between 7 to 12 digits'
  ]

  private mounted () {
    const padInfo: PADInfo = (Object.keys(this.padInformation).length) ? this.padInformation : this.currentOrgPADInfo
    this.transitNumber = padInfo?.bankTransitNumber || ''
    this.institutionNumber = padInfo?.bankInstitutionNumber || ''
    this.accountNumber = padInfo?.bankAccountNumber || ''
    this.isTOSAccepted = padInfo?.isTOSAccepted || false
    this.$nextTick(() => {
      if (this.isTOSAccepted) {
        this.isPreAuthDebitFormValid()
      }
    })
  }

  private get isTermsOfServiceAccepted () {
    return (Object.keys(this.padInformation).length) ? this.padInformation.isTOSAccepted : this.currentOrgPADInfo?.isTOSAccepted
  }

  private get padInfoSubtitle () {
    return (this.isChangeView)
      ? 'Services will continue to be billed to the linked BC Online account until the mandatory (3) day confirmation period has ended.'
      : 'This account will not be able to perform any transactions until the mandatory (3) day confirmation period has ended.'
  }

  private get acknowledgementLabel () {
    return (this.isChangeView)
      ? 'I understand that services will continue to be billed to the linked BC Online account until the mandatory (3) day confirmation period has ended.'
      : 'I understand that this account will not be able to perform any transactions until the mandatory (3) day confirmation period for pre-authorized debit has ended.'
  }

  @Emit()
  private emitPreAuthDebitInfo () {
    const padInfo: PADInfo = {
      bankTransitNumber: this.transitNumber,
      bankInstitutionNumber: this.institutionNumber,
      bankAccountNumber: this.accountNumber,
      isTOSAccepted: this.isTOSAccepted,
      isAcknowledged: this.isAcknowledged
    }
    this.isPreAuthDebitFormValid()
    this.setCurrentOrganizationPADInfo(padInfo)
    return padInfo
  }

  @Emit()
  private isPreAuthDebitFormValid () {
    const acknowledge = (this.isAcknowledgeNeeded) ? this.isAcknowledged : true
    return (this.$refs.preAuthDebitForm?.validate() && this.isTOSAccepted && acknowledge) || false
  }

  private isTermsAccepted (isAccepted) {
    this.isTOSAccepted = isAccepted
    this.emitPreAuthDebitInfo()
  }
}
</script>

<style lang="scss" scoped>
  .terms-container {
    height: 2rem;
  }

  .acknowledge-checkbox {
    ::v-deep {
      .v-input__slot {
        align-items: flex-start;
      }
    }
  }
</style>
