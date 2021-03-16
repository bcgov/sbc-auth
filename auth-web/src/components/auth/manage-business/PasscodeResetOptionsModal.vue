<template>
    <v-dialog
    v-model="isDialogOpen"
    max-width="800"
    :persistent="true"
    data-test="dialog-remove-business-options">
        <v-card>
            <v-card-title data-test="dialog-header">Remove Business
                <v-btn
                icon
                @click="close()"
                class="font-weight-bold"
                >
                    <v-icon>mdi-close</v-icon>
                </v-btn>

            </v-card-title>
            <v-card-text data-test="text-remove-business-options" class="d-flex flex-column">
                <p class="mb-7">{{ $t('removeBusinessOptionModalSubTitle') }}</p>
                <v-radio-group
                hide-details
                v-model="isResetPasscode"
                class="d-flex flex-column flex-grow-1 flex-shrink-0 font mt-1 pl-3"
                >
                    <v-radio
                    :value="true"
                    data-test="resetPasscode"
                    class="font"
                    >
                        <template v-slot:label>
                            <span class="font text--primary"><span class="font-weight-bold">Reset my passcode </span>and remove business</span>
                        </template>
                    </v-radio>
                    <ul class="mb-7 ml-7" data-test="text-reset-passcode-summary" v-html="resetPasscodeSummary"/>
                    <v-expand-transition v-if="isResetPasscode === true">
                        <v-form class="ma-7" ref="passcodeResetEmailForm" id="passcodeResetEmailForm">
                            <v-text-field
                            filled
                            label="Email Address"
                            req
                            persistent-hint
                            :rules="emailRules"
                            v-model="emailAddress"
                            >
                            </v-text-field>
                            <v-text-field
                            filled
                            label="Confirm Email Address"
                            req
                            persistent-hint
                            :error-messages="emailMustMatch()"
                            v-model="confirmedEmailAddress"
                            >
                            </v-text-field>
                        </v-form>
                    </v-expand-transition>
                    <v-radio
                    :value="false"
                    data-test="donotResetPasscode"
                    >
                        <template v-slot:label>
                            <span class="font text--primary"><span class="font-weight-bold">Do not reset my passcode </span>and remove business</span>
                        </template>
                    </v-radio>
                    <ul class="mb-7 ml-7" data-test="text-donot-reset-passcode-summary" v-html="donotResetPasscodeSummary"/>
                </v-radio-group>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn large @click="confirmPasscodeResetOptions()" color="primary" data-test="btn-reset-passcode">Remove</v-btn>
                <v-btn large @click="close()" data-test="btn-close-generate-passcode-dialog">Close</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import CommonUtils from '@/util/common-util'

@Component({
})
export default class PasscodeResetOptionsModal extends Vue {
    private isResetPasscode: boolean = false
    private isDialogOpen: boolean = false
    private emailAddress = ''
    private confirmedEmailAddress = ''
    private emailRules = CommonUtils.emailRules()

    $refs: {
    passcodeResetEmailForm: HTMLFormElement
  }

    private emailMustMatch (): string {
      return (this.emailAddress === this.confirmedEmailAddress) ? '' : 'Email addresses must match'
    }

    private get resetPasscodeSummary (): string {
      return this.$t('removeBusinessOptionModalResetPasscode').toString()
    }

    private get donotResetPasscodeSummary (): string {
      return this.$t('removeBusinessOptionModalDonotResetPasscode').toString()
    }

    public open () {
      this.isDialogOpen = true
    }

    public close () {
      this.isDialogOpen = false
    }

    private isFormValid (): boolean {
      return this.$refs.passcodeResetEmailForm?.validate() && !this.emailMustMatch()
    }

    private confirmPasscodeResetOptions () {
      if (this.isResetPasscode) {
        if (this.isFormValid()) {
          this.$emit('confirm-passcode-reset-options', this.emailAddress)
        }
      } else {
        this.$emit('confirm-passcode-reset-options', null)
      }
    }
}
</script>
