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
          v-model="businessIdentifier"
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
        <v-btn depressed large color="primary" @click="add">
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
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { mapActions, mapMutations, mapState } from 'vuex'
import BusinessModule from '@/store/modules/business'
import ConfigHelper from '@/util/config-helper'
import { LoginPayload } from '@/models/business'
import { getModule } from 'vuex-module-decorators'

@Component({
  methods: {
    ...mapActions('business', ['addBusiness'])
  }
})
export default class AddBusinessForm extends Vue {
  private businessStore = getModule(BusinessModule, this.$store)
  private readonly addBusiness!: (loginPayload: LoginPayload) => void
  private showPasscode = false
  private validationError = ''
  private entityNumRules = [v => !!v || 'Incorporation Number is required']
  private entityPasscodeRules = [
    v => !!v || 'Passcode is required',
    v => v.length >= 9 || 'Passcode must be exactly 9 digits'
  ]
  private VUE_APP_COPS_REDIRECT_URL = ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private businessIdentifier: string = ''
  private passcode: string = ''

  $refs: {
    form: HTMLFormElement
  }

  private isFormValid (): boolean {
    return this.$refs.form.validate()
  }

  private redirectToNext (): void {
    // transition to business contact UI
    this.$router.push('/main')
  }

  async add () {
    if (this.isFormValid()) {
      try {
        // attempt to add business
        await this.addBusiness({ businessIdentifier: this.businessIdentifier, passCode: this.passcode })

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
    this.businessIdentifier = ''
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
