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
          data-test="business-identifier"
        ></v-text-field>
      </div>
      <div class="passcode-form__row">
        <v-text-field
          filled
          label="Enter your Passcode"
          hint="Passcode must be exactly 9 digits"
          persistent-hint
          :rules="entityPasscodeRules"
          :maxlength="9"
          v-model="passcode"
          autocomplete="off"
          data-test="business-passcode"
        ></v-text-field>
      </div>
      <div class="form__btns mt-8">
        <v-btn data-test="forgot-passcode-button" text color="primary" @click.stop="helpDialog = true">
          <v-icon small>mdi-open-in-new</v-icon>
          <span>I lost or forgot my passcode</span>
        </v-btn>
        <div>
          <v-btn data-test="add-business-button" large color="primary" @click="add">
            <span>Add Business</span>
          </v-btn>
          <v-btn data-test="cancel-button" large depressed color="default" class="ml-2" @click="cancel">
            <span>Cancel</span>
          </v-btn>
        </div>
      </div>
    </v-form>
    <v-dialog v-model="helpDialog" hide-overlay max-width="640">
      <v-card>
        <v-card-title>Need Assistance?</v-card-title>
        <v-card-text>
          <p class="mb-7">If you have not received your Access Letter from BC Registries, or have lost your Passcode, please contact us at:</p>
          <ul class="contact-info__list mb-7">
            <li>
              <span>Toll Free:</span>&nbsp;&nbsp;{{ $t('techSupportTollFree') }}
            </li>
            <li>
              <span>Phone:</span>&nbsp;&nbsp;{{ $t('techSupportPhone') }}
            </li>
            <li>
              <span>Email:</span>&nbsp;&nbsp;<a v-bind:href="'mailto:' + $t('techSupportEmail') + '?subject=' + $t('techSupportEmailSubject')">{{ $t('techSupportEmail') }}</a>
            </li>
          </ul>
          <div>
            <p class="mb-0"><strong>Hours of Operation:</strong><br>Monday to Friday, 8:30am - 4:30pm <span title="Pacific Standard Time">PST</span></p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn large color="primary" @click="helpDialog = false">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
  private validationError = ''
  private entityNumRules = [v => !!v || 'Incorporation Number is required']
  private entityPasscodeRules = [
    v => !!v || 'Passcode is required',
    v => v.length >= 9 || 'Passcode must be exactly 9 digits'
  ]
  private VUE_APP_COPS_REDIRECT_URL = ConfigHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private businessIdentifier: string = ''
  private passcode: string = ''
  private helpDialog = false

  $refs: {
    form: HTMLFormElement
  }

  private isFormValid (): boolean {
    return this.$refs.form.validate()
  }

  private redirectToNext (): void {
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
        } else {
          this.$emit('add-unknown-error')
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
    justify-content: space-between;
    align-items: center;
  }
</style>
