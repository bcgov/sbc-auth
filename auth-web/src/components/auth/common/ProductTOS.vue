<template>
  <div>
    <template>
      <div>
        <h4>Terms of Service</h4>
        <p> I confirm, I <strong>{{userName}}</strong> am an authorized prime admin for this account.<br />
          I declare that this account <strong>{{orgName}}</strong> and all team members act as a solicitor, or name search company approved by the Vital Statistics agency.
        </p>
      </div>
      <v-checkbox
        color="primary"
        class="terms-checkbox align-checkbox-label--top ma-0 pa-0"
        hide-details
        v-model="termsAccepted"
        required
        data-test="check-termsAccepted"
        @change="tosChanged"
      >
        <template v-slot:label>
          <span class="label-color ml-2">{{$t('willsRegistryTosIagree')}}</span>

      </template>
      </v-checkbox>
      <div class="terms-error mt-2" color="error" v-if="istosTouched && !termsAccepted">
        <v-icon color="error" class="error-color mr-1">mdi-alert-circle</v-icon>
        <span> Confirm to the terms to request</span>
      </div>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'

@Component
export default class ProductTOS extends Vue {
  @Prop({ default: '' }) userName: string
  @Prop({ default: '' }) orgName: string
  @Prop({ default: false }) isTOSAlreadyAccepted: boolean
  @Prop({ default: false }) isApprovalFlow: boolean
  private termsAccepted: boolean = false
  public istosTouched: boolean = false

  @Watch('isTOSAlreadyAccepted')
  onisTOSALreadyAcceptedChange (newTos:boolean, oldTos:boolean) {
    if (newTos !== oldTos) {
      this.termsAccepted = newTos
    }
  }

  public mounted () {
    this.termsAccepted = this.isTOSAlreadyAccepted
  }

  @Emit('tos-status-changed')
  public tosChanged () {
    this.istosTouched = true
    return this.termsAccepted
  }
}
</script>

<style lang="scss" scoped>
.label-color {
  color:  rgba(0,0,0,.87) !important;
}

.terms-error{
  color: var(--v-error-base) !important;
  font-size: 16px;
  font-weight: bold;
  display: flex;
}
.error-color{
  color: var(--v-error-base) !important;
}
</style>
