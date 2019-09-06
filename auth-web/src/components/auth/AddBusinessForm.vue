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
        ></v-text-field>
      </div>
      <div class="passcode-form__row passcode-form__form-btns">
        <v-btn class="cancel-btn" @click="cancel" color="secondary" large>
          <span>Cancel</span>
        </v-btn>
        <v-btn class="sign-in-btn" @click="addBusiness" color="primary" large>
          <span>Add Business</span>
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
  VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
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
        // still need to call login as we need to verify if businessNumber and passCode are correct.
        const loginResponse = await this.businessStore.login({ businessNumber: this.businessNumber, passCode: this.passcode })

        // attempt to add business
        await this.businessStore.addBusiness({ businessNumber: this.businessNumber, passCode: this.passcode })

        // emit event to let parent know business added
        this.$emit('add-success')
      } catch (exception) {
        if (exception.response && exception.response.status === 401) {
          this.$emit('add-failed-invalid-code')
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

.passcode-form__row{
  margin-top: 1rem;
  justify-content: space-between;
}

.passcode-form__form-btns{
  margin-top: 2rem;
  display: flex;
}

.v-btn{
  margin: 0;
}

.v-btn.recovery-btn{
  margin-right: auto;
  padding-right: 0.7rem;
  padding-left: 0.7rem;
  text-decoration: underline;
  font-size: 1rem;
}

.v-btn.sign-in-btn{
  font-weight: 700;
}

.v-input{
  max-width: 25rem;
}

.passcode-form__alert-container{
  margin-bottom: 2rem;
}

.v-alert{
  margin: 0;
}

@media (max-width: 600px){
  .passcode-form__form-btns{
    flex-flow: column nowrap
  }

  .v-btn.recovery-btn{
    order: 1;
    margin-top: 0.5rem;
    margin-left: auto;
  }

  .v-btn.sign-in-btn{
    width: 100%
  }
}

@media (min-width: 960px){
  .v-btn.recovery-btn{
    font-size: 0.875rem
  }
}

// Contact List
.contact-list{
  margin-top: 1.5rem;
  padding: 0;
  font-weight: 500;
  list-style-type: none;
}

.contact-list__row{
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.contact-list__row .v-icon {
    vertical-align: middle;
    margin-top: -0.2rem;
    margin-right: 1.25rem;
}

.contact-list__row + .contact-list__row{
  margin-top: 0.5rem
}

// Passcode Dialog
.v-dialog{
  margin: 2rem
}

.v-card__title{
  padding: 1.25rem 1.5rem;
  color: $BCgovFontColorInverted;
  background: $BCgovBlue5;
  font-size: 1.5em;
  font-weight: 400;
}

.v-card__text{
  padding: 1.5rem;
  font-weight: 300;
}
</style>
