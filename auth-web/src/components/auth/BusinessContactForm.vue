<template>
  <div>
    <v-form ref="form" lazy-validation>
      <v-expand-transition>
        <div class="business-contact-form_alert-container" v-show="formError">
          <v-alert
            :value="true"
            color="error"
            icon="warning"
          >{{formError}}
          </v-alert>
        </div>
      </v-expand-transition>
    <div class="business-contact-form_row">
      <v-text-field
        box
        label="Email Address"
        req
        persistent-hint
        v-model="emailAddress"
      >
      </v-text-field>
    </div>
    <div class="business-contact-form_row">
      <v-text-field
        box
        label="Confirm Email Address"
        req
        persistent-hint
      >
      </v-text-field>
    </div>
    <div class="business-contact-form_row">
      <v-layout wrap>
        <v-flex xs6 class="mr-5">
          <v-text-field
            box
            label="Phone"
            persistent-hint
            v-model="phoneNumber"
          >
          </v-text-field>
        </v-flex>
        <v-flex xs3>
          <v-text-field
            box label="Extension"
            persistent-hint
            v-model="extension"
          >
          </v-text-field>
        </v-flex>
      </v-layout>
    </div>
    <div class="business-contact-form_row">
      <v-layout wrap>
        <v-spacer></v-spacer>
        <v-btn @click="save" color="primary" large>
          <span>Save and Continue</span>
        </v-btn>
        <v-btn class="mr-0" @click="skip" color="secondary" large>
          <span>Skip</span>
        </v-btn>
      </v-layout>
    </div>
    </v-form>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'
import BusinessModule from '../../store/modules/business'
import configHelper from '../../util/config-helper'

@Component
export default class BusinessContactForm extends Vue {
  private VUE_APP_COPS_REDIRECT_URL = configHelper.getValue('VUE_APP_COPS_REDIRECT_URL')
  private businessStore = getModule(BusinessModule)
  private emailAddress = ''
  private phoneNumber = ''
  private extension = ''

  private isFormValid (): boolean {
    return (this.$refs.form as Vue & { validate: () => boolean }).validate()
  }

  mounted () {
    const contact = this.businessStore.currentBusiness.contact1
    if (contact) {
      this.emailAddress = contact.emailAddress
      this.phoneNumber = contact.phoneNumber
      this.extension = contact.extension
    }
  }

  save () {
    if (this.isFormValid()) {
      // this.businessStore
    }
  }

  skip () {
    // Go directly to co-op UI without saving
    setTimeout(() => {
      window.location.href = this.VUE_APP_COPS_REDIRECT_URL
    }, 500)
  }
}
</script>

<style lang="stylus" scoped>
  @import '../../assets/styl/theme.styl';

  .business-contact-form_row
    margin-top 1rem

  .business-contact-form_alert-container
    margin-bottom 2rem

  .v-alert
    margin 0

  .v-btn
    font-weight: 700
</style>
