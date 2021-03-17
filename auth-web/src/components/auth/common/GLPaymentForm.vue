<template>
  <div>
    <template >
      <p class="mb-9">
        General Ledger codes for the account that is issued by the Finance department of the Ministry
      </p>

    </template>
    <v-form ref="GlInfoForm">
      <section>
        <header class="mb-4 d-flex align-content-center">
          <div data-test="pad-info-form-title" class="mr-1 font-weight-bold">General Ledger Information</div>
        </header>
        <v-row>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Client Code"
              filled
              hint="3 characters"
              persistent-hint
              :rules="clientCodeRules"
              v-model="clientCode"
              @change="emitGLInfo"
              v-mask="'###'"
              data-test="input-client-code"
            ></v-text-field>
          </v-col>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Responsibility Center"
              filled
              hint="5 characters"
              persistent-hint
              :rules="responsiblityCenterRules"
              v-model="responsiblityCenter"
              @change="emitGLInfo"
              v-mask="'#####'"
              data-test="input-responsiblityCenter"
            ></v-text-field>
          </v-col>
            <v-col cols="4" class="py-0">
            <v-text-field
              label="Account Number"
              filled
              hint="5 characters"
              persistent-hint
              :rules="accountNumberRules"
              v-model="accountNumber"
              @change="emitGLInfo"
              data-test="input-accountNumber"
              v-mask="'#####'"
            ></v-text-field>
          </v-col>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Standard Object"
              filled
              hint="4 characters"
              persistent-hint
              :rules="standardObjectRules"
              v-model="standardObject"
              data-test="input-standardObject"
              v-mask="'####'"
              @change="emitGLInfo"
              >
            ></v-text-field>
          </v-col>
            <v-col cols="8" class="py-0">
            <v-text-field
              label="Project"
              filled
              hint="7 characters"
              persistent-hint
              :rules="projectRules"
              v-model="project"
              @change="emitGLInfo"
              data-test="input-project"
              v-mask="'#######'"
              >
            ></v-text-field>
          </v-col>
        </v-row>
      </section>
    </v-form>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Mixins, Prop, Vue } from 'vue-property-decorator'
import { GLInfo } from '@/models/Organization'
import { mask } from 'vue-the-mask'
import { namespace } from 'vuex-class'
const OrgModule = namespace('org')

@Component({
  directives: {
    mask
  }
})
export default class GLPaymentForm extends Vue {
  @OrgModule.State('currentOrgGLInfo') private currentOrgGLInfo!: GLInfo[]
  @OrgModule.State('currentOrganization') private currentOrganization!: any
  @OrgModule.Mutation('setCurrentOrganizationGLInfo') private setCurrentOrganizationGLInfo!: (glInfo: GLInfo) => void

  @Prop({ default: () => ({} as GLInfo) }) glInformation: any
  private clientCode: string = ''
  private responsiblityCenter: string = ''
  private accountNumber: string = ''
  private standardObject: string = ''
  private project: string = ''

  $refs: {
    GlInfoForm: HTMLFormElement,
  }

  public clientCodeRules = [
    v => !!v || 'Client Code is required',
    v => (v.length >= 3) || 'Client Code should be of 3 digits'
  ]

  public responsiblityCenterRules = [
    v => !!v || 'Responsibility Center is required',
    v => (v.length === 5) || 'Responsibility Center should be 5 digits'
  ]

  public accountNumberRules = [
    v => !!v || 'Account Number is required',
    v => (v.length === 5) || 'Account Number should be 5 digits'
  ]

  public standardObjectRules = [
    v => !!v || 'Standard Object is required',
    v => (v.length === 4) || 'Standard Object should be 4 digits'
  ]
  public projectRules = [
    v => !!v || 'Project is required',
    v => (v.length === 7) || 'Project should be 7 digits'
  ]

  // setup basic details on mount
  public mounted () {
    const glInfo: GLInfo = (Object.keys(this.glInformation).length) ? this.glInformation : this.currentOrgGLInfo
    this.clientCode = glInfo?.clientCode || ''
    this.responsiblityCenter = glInfo?.responsiblityCenter || ''
    this.accountNumber = glInfo?.accountNumber || ''
    this.standardObject = glInfo?.standardObject || ''
    this.project = glInfo?.project || ''
    // this.isGlInfoFormValid()
  }

  // setting value to store
  // @Emit()
  public async emitGLInfo () {
    const glInfo: GLInfo = {
      clientCode: this.clientCode,
      responsiblityCenter: this.responsiblityCenter,
      accountNumber: this.accountNumber,
      standardObject: this.standardObject,
      project: this.project
    }
    this.isGlInfoFormValid()
    this.setCurrentOrganizationGLInfo(glInfo)
    return glInfo
  }

  // emit to enable next button
  @Emit()
  private isGlInfoFormValid () {
    return this.$refs.GlInfoForm?.validate() || false
  }
}
</script>
