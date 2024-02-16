<template>
  <ModalDialog
    ref="passcodeResetOptionsDialog"
    max-width="800"
    :isPersistent="true"
    :showCloseIcon="true"
    :showIcon="false"
    title="Remove Business"
    data-test="dialog-passcode-reset-options"
  >
    <template #text>
      <p class="mb-7">
        {{ $t('removeBusinessOptionModalSubTitle') }}
      </p>
      <v-radio-group
        v-model="isResetPasscode"
        hide-details
        class="d-flex flex-column flex-grow-1 flex-shrink-0 font mt-1 pl-3"
      >
        <v-radio
          :value="true"
          data-test="resetPasscode"
          class="font"
        >
          <template #label>
            <span class="font text--primary"><span class="font-weight-bold">Reset my passcode </span>and remove business</span>
          </template>
        </v-radio>
        <ul
          class="mb-7 ml-7"
          data-test="text-reset-passcode-summary"
          v-html="$t('removeBusinessOptionModalResetPasscode')"
        />
        <v-expand-transition v-if="isResetPasscode === true">
          <v-form
            id="passcodeResetEmailForm"
            ref="passcodeResetEmailForm"
            class="ma-7"
          >
            <v-text-field
              v-model="emailAddress"
              filled
              label="Email Address"
              req
              persistent-hint
              :rules="emailRules"
            />
            <v-text-field
              v-model="confirmedEmailAddress"
              filled
              label="Confirm Email Address"
              req
              persistent-hint
              :error-messages="emailMustMatch()"
            />
          </v-form>
        </v-expand-transition>
        <v-radio
          :value="false"
          data-test="donotResetPasscode"
        >
          <template #label>
            <span class="font text--primary"><span class="font-weight-bold">Do not reset my passcode </span>and remove business</span>
          </template>
        </v-radio>
        <ul
          class="mb-7 ml-7"
          data-test="text-donot-reset-passcode-summary"
          v-html="$t('removeBusinessOptionModalDonotResetPasscode')"
        />
      </v-radio-group>
    </template>
    <template #actions>
      <v-spacer />
      <v-btn
        large
        color="primary"
        data-test="btn-reset-passcode"
        @click="confirmPasscodeResetOptions()"
      >
        Remove
      </v-btn>
      <v-btn
        large
        data-test="btn-close-generate-passcode-dialog"
        @click="close()"
      >
        Close
      </v-btn>
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
export default class PasscodeResetOptionsModal extends Vue {
  isResetPasscode: boolean = false
  emailAddress = ''
  confirmedEmailAddress = ''
  emailRules = CommonUtils.emailRules()

  $refs: {
    passcodeResetEmailForm: HTMLFormElement,
    passcodeResetOptionsDialog: InstanceType<typeof ModalDialog>
  }

  emailMustMatch (): string {
    return (this.emailAddress === this.confirmedEmailAddress) ? '' : 'Email addresses must match'
  }

  public open () {
    this.$refs.passcodeResetOptionsDialog.open()
  }

  public close () {
    this.$refs.passcodeResetOptionsDialog.close()
  }

  private isFormValid (): boolean {
    return this.$refs.passcodeResetEmailForm?.validate() && !this.emailMustMatch()
  }

  confirmPasscodeResetOptions () {
    if (this.isResetPasscode) {
      if (this.isFormValid()) {
        this.$emit('confirm-passcode-reset-options', this.emailAddress)
      }
    } else {
      this.$emit('confirm-passcode-reset-options')
    }
  }
}
</script>
