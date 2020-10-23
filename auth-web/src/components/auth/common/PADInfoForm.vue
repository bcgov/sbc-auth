<template>
  <div>
    <h4>Banking Information</h4>
    <v-form ref="preAuthDebitForm">
      <v-row>
        <v-col cols="6">
          <v-text-field
            label="Transit Number"
            filled
            hint="5 digits"
            persistent-hint
            :rules="transitNumberRules"
            v-model="transitNumber"
            @change="emitPreAuthDebitInfo"
            v-mask="'#####'"
            dense
          ></v-text-field>
        </v-col>
        <v-col cols="6">
          <v-text-field
            label="Institution Number"
            filled
            hint="3 digits"
            persistent-hint
            :rules="institutionNumberRules"
            v-model="institutionNumber"
            @change="emitPreAuthDebitInfo"
            v-mask="'###'"
            dense
          ></v-text-field>
        </v-col>
        <v-col cols="12" class="pt-0">
          <v-text-field
            label="Account Number"
            filled
            hint="7 to 12 digits"
            persistent-hint
            :rules="accountNumberRules"
            v-model="accountNumber"
            @change="emitPreAuthDebitInfo"
            v-mask="'############'"
            dense
          ></v-text-field>
        </v-col>
      </v-row>
      <TermsOfUseDialog
        @terms-acceptance-status="isTermsAccepted"
      ></TermsOfUseDialog>
    </v-form>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { mapMutations, mapState } from 'vuex'
import TermsOfUseDialog from '@/components/auth/common/TermsOfUseDialog.vue'
import { mask } from 'vue-the-mask'

@Component({
  directives: {
    mask
  },
  components: {
    TermsOfUseDialog
  }
})
export default class PADInfoForm extends Vue {
  @Prop({ default: {} }) padInformation: any
  private transitNumber: string = ''
  private institutionNumber: string = ''
  private accountNumber: string = ''
  private isTOSAccepted: boolean = false

  $refs: {
    preAuthDebitForm: HTMLFormElement,
  }

  private transitNumberRules = [
    v => !!v || 'Transit Number is required',
    v => (v.length === 5) || 'Transit Number should be 5 digits'
  ]

  private institutionNumberRules = [
    v => !!v || 'Institution Number is required',
    v => (v.length === 3) || 'Institution Number should be 3 digits'
  ]

  private accountNumberRules = [
    v => !!v || 'Account Number is required',
    v => (v.length >= 7 && v.length <= 12) || 'Account Number should be between 7 to 12 digits'
  ]

  private mounted () {
    this.transitNumber = this.padInformation?.transitNumber || ''
    this.institutionNumber = this.padInformation?.institutionNumber || ''
    this.accountNumber = this.padInformation?.accountNumber || ''
  }

  @Emit()
  private emitPreAuthDebitInfo () {
    return {
      transitNumber: this.transitNumber,
      institutionNumber: this.institutionNumber,
      accountNumber: this.accountNumber
    }
  }

  private isTermsAccepted (isAccepted) {
    this.isTOSAccepted = isAccepted
  }
}
</script>
