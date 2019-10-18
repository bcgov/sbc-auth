<template>
  <div class="passcode-form">
    <v-form ref="form" lazy-validation>
      <v-expand-transition>
        <div class="passcode-form__alert-container" v-show="validationError">
          <v-alert
            :value="true"
            color="error"
            icon="warning"
          >{{validationError}}
          </v-alert>
        </div>
      </v-expand-transition>
      <div class="passcode-form__row">
        <v-text-field
          filled
          label="Enter your Incorporation Number"
          hint="Example: CP1234567"
          req
          persistent-hint
          :rules="entityNumRules"
          v-model="businessNumber"
        ></v-text-field>
      </div>
      <div class="passcode-form__row">
        <v-text-field
          :append-icon="showPasscode ? 'visibility' : 'visibility_off'"
          :type="showPasscode ? 'text' : 'password'"
          @click:append="showPasscode = !showPasscode"
          filled
          label="Enter your Passcode"
          hint="Passcode must be exactly 9 digits"
          persistent-hint
          :rules="entityPasscodeRules"
          :maxlength="9"
          v-model="passcode"
          autocomplete="off"
        ></v-text-field>
      </div>
      <div class="form__btns mt-8">
        <v-btn depressed large color="primary" @click="addBusiness">
          <span>Add Business</span>
        </v-btn>
        <v-btn depressed large color="default" class="ml-2" @click="cancel">
          <span>Cancel</span>
        </v-btn>
      </div>
    </v-form>

  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import { Component, Prop, Emit } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import BusinessModule from '../../store/modules/business'
import configHelper from '../../util/config-helper'

@Component
export default class AddBusinessForm extends Vue {
  $refs: {
    form: HTMLFormElement
  }
  showPasscode = false
  validationError = ''
  entityNumRules = [
    v => !!v || 'Incorporation Number is required'
  ]
  entityPasscodeRules = [
    v => !!v || 'Passcode is required',
    v => v.length >= 9 || 'Passcode must be exactly 9 digits'
  ]
  businessStore = getModule(BusinessModule, this.$store)

  businessNumber: string = ''
  passcode: string = ''

  private isFormValid (): boolean {
    return this.$refs.form.validate()
  }

  private redirectToNext (): void {
    // transition to business contact UI
    this.$router.push('/main')
  }

  async addBusiness () {
    if (this.isFormValid()) {
      try {
        // attempt to add business
        await this.businessStore.addBusiness({ businessNumber: this.businessNumber, passCode: this.passcode })

        // emit event to let parent know business added
        this.$emit('add-success')
      } catch (exception) {
        if (exception.response && exception.response.status === 401) {
          this.$emit('add-failed-invalid-code')
        } else if (exception.response && exception.response.status === 404) {
          this.$emit('add-failed-no-entity')
        }
      } finally {
        this.resetForm()
      }
    }
  }

  @Emit()
  cancel () {}

  resetForm () {
    this.businessNumber = ''
    this.passcode = ''
    this.$refs.form.resetValidation()
  }
}
</script>

<style lang="scss" scoped>
@import '../../assets/scss/theme.scss';

  .form__btns {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
  }
</style>
