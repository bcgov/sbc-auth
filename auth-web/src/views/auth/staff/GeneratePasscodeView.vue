<template>
  <ModalDialog
  max-width="680"
  :isPersistent="true"
  ref="generatePasscodeModal"
  :showCloseIcon="true"
  :showIcon="false"
  title="Generate Passcode"
  data-test="dialog-generate-passcode">
    <template v-slot:text>
      <p class="mb-7 mr-7">{{ $t('generatePasscodeText') }}</p>
      <v-form ref="generatePasscodeForm" id="generatePasscodeForm">
        <v-text-field
        filled
        label="Email Address"
        req
        persistent-hint
        :rules="emailRules"
        v-model="emailAddress"
        data-test="text-email-address"
        class="generate-passcode-input"
        >
        </v-text-field>
        <v-text-field
        filled
        label="Confirm Email Address"
        req
        persistent-hint
        :error-messages="emailMustMatch()"
        v-model="confirmedEmailAddress"
        data-test="text-confirm-email-address"
        class="generate-passcode-input"
        >
        </v-text-field>
      </v-form>
    </template>
    <template v-slot:actions>
      <v-spacer></v-spacer>
      <v-btn large @click="generate()" color="primary" data-test="btn-generate-passcode">Generate</v-btn>
      <v-btn large @click="close()" data-test="btn-close-generate-passcode-dialog">Close</v-btn>
    </template>
  </ModalDialog>
</template>
<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'

@Component({
  components: {
    ModalDialog
  }
})
export default class GeneratePasscodeView extends Vue {
  private emailAddress = ''
  private confirmedEmailAddress = ''
  private emailRules = CommonUtils.emailRules()

  $refs: {
    generatePasscodeForm: HTMLFormElement,
    generatePasscodeModal: ModalDialog
  }

  public open () {
    this.$refs.generatePasscodeModal.open()
  }

  private emailMustMatch (): string {
    return (this.emailAddress === this.confirmedEmailAddress) ? '' : 'Email addresses must match'
  }

  private isFormValid (): boolean {
    return this.$refs.generatePasscodeForm?.validate() && !this.emailMustMatch()
  }

  public close () {
    this.$refs.generatePasscodeModal.close()
  }

  private generate () {
    if (this.isFormValid()) {
    }
  }
}
</script>
<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
.generate-passcode-input{
    display: inline-block;
    width: 30rem;
}

.remove-btn {
    margin-left: 0.25rem;
    width: 7rem;
    height: 60px;
    vertical-align: top;
    font-weight: bold;
}
</style>
