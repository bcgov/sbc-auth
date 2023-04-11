<template>
  <div>
    <template >
      <p class="mb-9" v-if="canSelect">
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
              :rules="clientRules"
              v-model="client"
              @change="emitGLInfo"
              v-mask="'XXX'"
              data-test="input-client-code"
              :disabled="!canSelect"
            ></v-text-field>
          </v-col>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Responsibility Center"
              filled
              hint="5 characters"
              persistent-hint
              :rules="responsibilityCentreRules"
              v-model="responsibilityCentre"
              @change="emitGLInfo"
              v-mask="'XXXXX'"
              data-test="input-responsibilityCentre"
              :disabled="!canSelect"
            ></v-text-field>
          </v-col>
            <v-col cols="4" class="py-0">
            <v-text-field
              label="Account Number"
              filled
              hint="5 characters"
              persistent-hint
              :rules="serviceLineRules"
              v-model="serviceLine"
              @change="emitGLInfo"
              data-test="input-serviceLine"
              v-mask="'XXXXX'"
              :disabled="!canSelect"
            ></v-text-field>
          </v-col>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Standard Object"
              filled
              hint="4 characters"
              persistent-hint
              :rules="stobRules"
              v-model="stob"
              data-test="input-stob"
              v-mask="'XXXX'"
              @change="emitGLInfo"
              :disabled="!canSelect"
              >
            ></v-text-field>
          </v-col>
            <v-col cols="8" class="py-0">
            <v-text-field
              label="Project"
              filled
              hint="7 characters"
              persistent-hint
              :rules="projectCodeRules"
              v-model="projectCode"
              @change="emitGLInfo"
              data-test="input-projectCode"
              v-mask="'XXXXXXX'"
              :disabled="!canSelect"
              >
            ></v-text-field>
          </v-col>
        </v-row>
      </section>
    </v-form>
  </div>
</template>

<script lang="ts">
import { GLInfo } from '@/models/Organization'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
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
  @Prop({ default: true }) private canSelect: boolean

  private client: string = ''
  private responsibilityCentre: string = ''
  private serviceLine: string = ''
  private stob: string = ''
  private projectCode: string = ''

  $refs: {
    GlInfoForm: HTMLFormElement,
  }

  public clientRules = [
    v => !!v || 'Client Code is required',
    v => (v.length >= 3) || 'Client Code should be 3 characters'
  ]

  public responsibilityCentreRules = [
    v => !!v || 'Responsibility Center is required',
    v => (v.length === 5) || 'Responsibility Center should be 5 characters'
  ]

  public serviceLineRules = [
    v => !!v || 'Account Number is required',
    v => (v.length === 5) || 'Account Number should be 5 characters'
  ]

  public stobRules = [
    v => !!v || 'Standard Object is required',
    v => (v.length === 4) || 'Standard Object should be 4 characters'
  ]
  public projectCodeRules = [
    v => !!v || 'Project is required',
    v => (v.length === 7) || 'Project should be 7 characters'
  ]

  @Watch('currentOrgGLInfo')
  oncurrentOrgGLInfoChange (newGlInfo) {
    this.setGlInfo(newGlInfo)
  }

  // setup basic details on mount
  public mounted () {
    const glInfo: GLInfo = (Object.keys(this.glInformation).length) ? this.glInformation : this.currentOrgGLInfo
    this.setGlInfo(glInfo)
  }
  public updated () {
    this.isGlInfoFormValid()
  }

  public setGlInfo (glInfo) {
    this.client = glInfo?.client || ''
    this.responsibilityCentre = glInfo?.responsibilityCentre || ''
    this.serviceLine = glInfo?.serviceLine || ''
    this.stob = glInfo?.stob || ''
    this.projectCode = glInfo?.projectCode || ''
  }

  // setting value to store
  // @Emit()
  public async emitGLInfo () {
    const glInfo: GLInfo = {
      client: this.client,
      responsibilityCentre: this.responsibilityCentre,
      serviceLine: this.serviceLine,
      stob: this.stob,
      projectCode: this.projectCode
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
