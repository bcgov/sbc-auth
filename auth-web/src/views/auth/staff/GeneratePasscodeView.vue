<template>
 <v-dialog v-model="isDialogOpen" max-width="800" :persistent="true">
    <v-card>
      <v-card-title data-test="title-generate-passcode">Generate Passcode</v-card-title>
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
        <v-form class="flex-grow-1 flex-shrink-0" style="min-height: 5em; max-height: 100%;" ref="generatePasscodeForm" id="generatePasscodeForm">
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
            >
            </v-text-field>
            <v-btn
            color="primary"
            class="remove-btn mt-0"
            depressed
            @click="removeEmailAddress(index)"
            :data-test="getIndexedTag('btn-remove-passcode-emailAddress', index)"
            >Remove</v-btn>
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
        <v-btn large @click="close()">Close</v-btn>
      </v-card-actions>
    </v-card>
 </v-dialog>
</template>
<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import _ from 'lodash'

@Component({
})
export default class GeneratePasscodeView extends Vue {
  private isDialogOpen = false
  private emailAddresses: object[] = [{
    value: ''
  }]

  $refs: {
    generatePasscodeForm: HTMLFormElement
  }

  public open () {
    this.isDialogOpen = true
  }

  private get isThereEmailsToSend (): boolean {
    return !!_.find(this.emailAddresses, function (emailAddress) { return emailAddress.value !== '' })
  }

  private isFormValid (): boolean {
    return !!this.isThereEmailsToSend && this.$refs.generatePasscodeForm.validate()
  }

  public close () {
    this.isDialogOpen = false
  }

  private emailRules = [
    v => !!v || 'Email address is required',
    v => {
      const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
      return pattern.test(v) || 'Valid email is required'
    }
  ]

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
.v-input {
  display: inline-block;
  width: 20rem;
}

::v-deep {
  .v-input__append-outer {
    margin-top: 0 !important;
  }

  .remove-btn {
    margin-left: 0.25rem;
    width: 7rem;
    min-height: 54px;
    vertical-align: top;
    font-weight: bold;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
}
</style>
