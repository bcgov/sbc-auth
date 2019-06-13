<template>
  <div class="paybc">
    <iframe :src="VUE_APP_PAYBC_REDIRECT_URL" ref="iframeContent" style="display: none"></iframe>
    <v-form ref="form" lazy-validation>
      <v-expand-transition>
        <div class="paybc__alert-container" v-show="redirectError">
          <v-alert :value="true" color="error" icon="warning">{{redirectError}}</v-alert>
        </div>
      </v-expand-transition>
      <div class="paybc__row"></div>
      <div class="paybc__row"></div>
      <div class="paybc__row paybc__form-btns">
        <v-btn class="pay-btn" @click="redirectTo" color="primary" large>
          <v-progress-circular :indeterminate="true" size="20" width="2" v-if="showSpinner"></v-progress-circular>
          <span>{{showSpinner ? 'Paying' : 'File and Pay'}}</span>
          <v-icon dark right v-if="!showSpinner">arrow_forward</v-icon>
        </v-btn>
      </div>
    </v-form>
  </div>
</template>

<script lang='ts'>
import PaybcServices from '@/services/paybc.services'
import IframeServices from '@/services/iframe.services'
export default {
  name: 'Paybc',

  data: () => ({
    show1: false,
    showSpinner: false,
    noPasscodeDialog: false,
    redirectError: '',
    valid: false,
    // cudnt find a better way to expose env variables in template
    VUE_APP_PAYBC_REDIRECT_URL: process.env.VUE_APP_PAYBC_REDIRECT_URL
  }),

  computed: {},
  beforeMount () {
    this.redirectTo()
  },
  methods: {
    redirectTo () {
      PaybcServices.get_paybc_url('123456789')
        .then(response => {
          if (response.data.error) {
            this.redirectError = this.$t('redirectFailedMessage')
          } else if (response.data.paybc_url) {
            debugger
            this.showSpinner = true
            IframeServices.emit(
              this.$refs.iframeContent.contentWindow,
              response.data.paybc_url
            )
            sessionStorage.name = response.data.paybc_url
            setTimeout(() => {
              window.location.href = response.data.paybc_url
            }, 500)
          }
        })
        .catch(response => {
          this.redirectError = this.$t('redirectFailedMessage')
        })
    }
  }
}
</script>

<style lang='stylus' scoped>
@import '../assets/styl/theme.styl';

.paybc__row {
  margin-top: 1rem;
}

.paybc__form-btns {
  margin-top: 2rem;
  display: flex;
}

.v-btn {
  margin: 0;
}

.v-btn.pay-btn {
  font-weight: 700;
}

.v-input {
  max-width: 25rem;
}

.paybc__alert-container {
  margin-bottom: 2rem;
}

.v-alert {
  margin: 0;
}

@media (max-width: 600px) {
  .paybc__form-btns {
    flex-flow: column nowrap;
  }

  .v-btn.pay-btn {
    width: 100%;
  }
}

@media (min-width: 960px) {
  .v-btn.recovery-btn {
    font-size: 0.875rem;
  }
}

// Contact List
.contact-list {
  margin-top: 1.5rem;
  padding: 0;
  font-weight: 500;
  list-style-type: none;
}

.contact-list__row {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.contact-list__row .v-icon {
  vertical-align: middle;
  margin-top: -0.2rem;
  margin-right: 1.25rem;
}

.contact-list__row + .contact-list__row {
  margin-top: 0.5rem;
}

// Passcode Dialog
.v-dialog {
  margin: 2rem;
}

.v-card__title {
  padding: 1.25rem 1.5rem;
  color: $BCgovFontColorInverted;
  background: $BCgovBlue5;
  font-size: 1.5em;
  font-weight: 400;
}

.v-card__text {
  padding: 1.5rem;
  font-weight: 300;
}
</style>
