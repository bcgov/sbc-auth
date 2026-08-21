<template>
  <v-container class="vendor-linking-login-card">
    <v-row justify="center">
      <v-col
        cols="12"
        class="text-center"
      >
        <h1 class="mb-8">
          {{ $t('vendorLinkingLoginTitle') }}
        </h1>
        <div class="vendor-linking-login-card-content mx-auto text-left">
          <VendorLinkingWarningAlert
            data-test="vendor-linking-login-alert"
            :title="$t('vendorLinkingLoginAlertTitle')"
            :body="$t('vendorLinkingLoginAlertBody')"
            :note="$t('vendorLinkingLoginAlertNote')"
          />
          <v-card
            flat
            outlined
            class="vendor-linking-login-card-panel"
          >
            <v-img
              src="~sbc-common-components/src/assets/img/BCReg_Generic_Login_image.jpg"
              max-height="260"
              class="mb-4"
              :alt="$t('vendorLinkingLoginImageAlt')"
            />
            <v-btn
              large
              block
              color="primary"
              class="font-weight-bold mb-4"
              data-test="vendor-linking-continue-bcsc"
              @click="redirectToSignin('bcsc')"
            >
              <v-icon
                left
                size="20"
              >
                mdi-account-card-details-outline
              </v-icon>
              {{ $t('vendorLinkingContinueBcsc') }}
            </v-btn>
            <v-btn
              large
              block
              outlined
              color="primary"
              data-test="vendor-linking-continue-bceid"
              @click="redirectToSignin('bceid')"
            >
              <v-icon
                left
                size="20"
              >
                mdi-two-factor-authentication
              </v-icon>
              {{ $t('vendorLinkingContinueBceid') }}
            </v-btn>
            <p class="vendor-linking-login-card-bceid-hint text-center mt-2 mb-0">
              {{ $t('vendorLinkingBceidHint') }}
            </p>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, getCurrentInstance } from '@vue/composition-api'
import ConfigHelper from '@/util/config-helper'
import { Pages } from '@/util/constants'
import VendorLinkingWarningAlert from '@/components/auth/vendor-linking/VendorLinkingWarningAlert.vue'
import { buildSigninPath } from '@/util/vendor-connection-util'

export default defineComponent({
  name: 'VendorLinkingLoginCard',
  components: {
    VendorLinkingWarningAlert
  },
  props: {
    vendorAccountId: {
      type: String,
      required: true
    },
    returnUrl: {
      type: String,
      required: true
    }
  },
  setup (props) {
    const instance = getCurrentInstance()

    const redirectToSignin = (idpHint: string) => {
      const confirmUrl = `${ConfigHelper.getSelfURL()}/${Pages.VENDOR_LINKING}/confirm` +
        `?vendorAccountId=${props.vendorAccountId}&returnUrl=${encodeURIComponent(props.returnUrl)}`
      instance.proxy.$router.push(buildSigninPath(idpHint, confirmUrl))
    }

    return {
      redirectToSignin
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.vendor-linking-login-card {
  h1 {
    font-size: 1.875rem;
    line-height: 2.25rem;
    font-weight: 700;
    color: $gray9;
    text-align: center;
  }
}

.vendor-linking-login-card-content {
  max-width: 28rem;
}

.vendor-linking-login-card-panel {
  padding: 1.5rem;
  border-color: $gray3;
  border-radius: 6px;

  ::v-deep .v-btn {
    height: 44px;
    padding: 0.625rem 1.1875rem !important;
    border-radius: 6px;
    font-size: 1rem;

    .v-icon--left {
      margin-right: 0.625rem !important;
    }
  }

  ::v-deep .v-btn.primary {
    background-color: #1669bb !important;

    &:hover {
      background-color: rgba(22, 105, 187, 0.75) !important;
    }
  }

  ::v-deep .v-btn.v-btn--outlined.primary--text {
    border-color: #1669bb !important;
    color: #1669bb !important;

    &:hover {
      background-color: rgba(22, 105, 187, 0.1) !important;
    }
  }
}

.vendor-linking-login-card-bceid-hint {
  font-size: 0.875rem;
  color: $gray6;
}
</style>
