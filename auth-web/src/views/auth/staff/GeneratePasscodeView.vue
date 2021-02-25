<template>
 <v-dialog v-model="isDialogOpen" max-width="800" :persistent="true" data-test="dialog-generate-passcode">
    <v-card>
      <v-card-title data-test="title-generate-passcode">Generate Passcode
        <v-btn
        icon
        @click="close()"
        data-test="btn-close-generate-passcode-dialog-title"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-card-text data-test="text-generate-passcode" class="d-flex flex-column">
        <div class="flex-grow-0 flex-shrink-1" style="min-height: 5em">
         <p class="mb-7">{{ $t('generatePasscodeText') }}:</p>
         <ul class="mb-7">
            <li>{{ $t('generatePasscodeSummaryFirstLine') }}</li>
            <li>{{ $t('generatePasscodeSummarySecondLine') }}</li>
            <li>{{ $t('generatePasscodeSummaryThirdLine') }}</li>
         </ul>
         <p>The new passcode will be sent to the email below:</p>
        </div>
        <v-form class="d-flex flex-column flex-grow-1 flex-shrink-0" style="min-height: 5em; max-height: 100%;" ref="generatePasscodeForm" id="generatePasscodeForm">
          <div v-for="(emailAddress, index) in emailAddresses" :key="index">
            <v-text-field
            filled
            label="Email Address"
            dense
            req
            :rules="emailRules"
            v-model="emailAddress.value"
            :id="getIndexedTag('emailAddress', index)"
            :data-test="getIndexedTag('input-passcode-emailAddress', index)"
            class="generate-passcode-input"
            >
            </v-text-field>
            <v-btn
            v-show="index > 0"
            icon
            class="mt-3 ml-1 remove-btn"
            @click="removeEmailAddress(index)"
            :data-test="getIndexedTag('btn-remove-passcode-emailAddress', index)"
            >
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </div>
        </v-form>
        <div>
          <v-btn text color="primary" @click="addEmailAddress()">
            <v-icon class="ml-n2">mdi-plus-box</v-icon>
            <span>Add another</span>
          </v-btn>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn large color="primary" :disabled="!isFormValid()" type="submit" form="generatePasscodeForm" data-test="btn-generate-passcode-send">Send</v-btn>
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
export default class GeneratePasscodeView extends Vue {
  private isDialogOpen: boolean = false
  private emailAddresses: any[] = [{
    value: ''
  }]
  private emailRules = CommonUtils.emailRules()

  $refs: {
    generatePasscodeForm: HTMLFormElement
  }

  public open () {
    this.isDialogOpen = true
  }

  private get isThereEmailsToSend (): boolean {
    return !!this.emailAddresses.find(address => address.value !== '')
  }

  private isFormValid (): boolean {
    return !!this.isThereEmailsToSend && this.$refs.generatePasscodeForm.validate()
  }

  public close () {
    this.isDialogOpen = false
  }

  private addEmailAddress () {
    this.emailAddresses.push({
      value: ''
    })
  }

  private removeEmailAddress (index: number) {
    this.emailAddresses.splice(index, 1)
  }

  private getIndexedTag (tag, index): string {
    return `${tag}-${index}`
  }

  private send () {
  }
}
</script>
<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
.generate-passcode-input{
    display: inline-block;
    width: 20rem;
}

.remove-btn {
    margin-left: 0.25rem;
    width: 7rem;
    height: 60px;
    vertical-align: top;
    font-weight: bold;
}
</style>
