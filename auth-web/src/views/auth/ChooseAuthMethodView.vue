<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-9">
      <h1 class="view-header__title" data-test="account-settings-title">In order to create a BC Registries account, <span class="lb">we need to verify your identity.</span></h1>
      <p class="mt-5 mb-0">There are two ways you can verify your identity to create a BC Registries account.</p>
    </div>
    <div>
      <v-row>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card flat outlined hover class="account-card text-center pa-10 elevation-2 d-flex"
            @click="selectBCSCAuth()"
            :class="{'active': authType == 'BCSC'}"
            >
            <div class="account-type d-flex flex-column">
              <div class="account-type__icon mb-8">
                <v-icon>mdi-map-marker</v-icon>
              </div>
              <div class="account-type__title mb-6">
                I am a resident <span class="lb">of British Columbia</span>
              </div>
              <div class="account-type__details mb-6">
                Residents of British Columbia can use their government-issued BC Services Card to verify their identity
              </div>
              <div class="mb-10">
                <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bcservicescardapp/setup" target="_blank">Learn more about the BC Services card</a>
              </div>
              <!-- State Button (Create Account) -->
              <div class="mb-4">
                <v-btn large depressed block color="primary" class="font-weight-bold" :outlined="authType != 'BCSC'">
                   {{ authType == 'BCSC' ? 'SELECTED' : 'SELECT' }}
                </v-btn>
              </div>
              <div class="notary-link">
                <router-link class="caption"  v-on:click.native="linkToNext" to="/nonbcsc-info">Verify with a notary instead</router-link>
              </div>
            </div>
          </v-card>
        </v-col>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card flat outlined hover class="account-card text-center pa-10 elevation-2 d-flex"
            @click="selectBCEIDAuth()"
            :class="{'active': authType == 'BCEID'}"
            >
            <div class="account-type d-flex flex-column">
              <div class="account-type__icon mb-6">
                <v-icon>mdi-map-marker-off</v-icon>
              </div>
              <div class="account-type__title mb-6">
                I am not a resident <span class="lb">of British Columbia</span>
              </div>
              <div class="account-type__details mb-6">
                Non-BC residents must log into the BC Registries with a registered BCeID account, and verify their identity by a notarized affidavit.
              </div>
              <!-- State Button (Create Account) -->
              <div class="mb-4">
                <v-btn large depressed block color="primary" class="font-weight-bold" :outlined="authType != 'BCEID'">
                  {{ authType == 'BCEID' ? 'SELECTED' : 'SELECT' }}
                </v-btn>
              </div>
            </div>
          </v-card>
        </v-col>
        <v-col sm="12" class="py-0" v-if="!disableGovnAccountCreation">
          <v-checkbox
          color="primary"
          class="py-0 mt-2 align-checkbox-label--top"
          v-model="isGovN"
        >
          <template v-slot:label>
            I am a government agency (other than BC provincial)
          </template>
        </v-checkbox>
        </v-col>
      </v-row>
    </div>
    <v-divider class="mb-6 mt-1"></v-divider>
    <div class="form__btns d-flex mt-8">
      <v-btn
        large
        color="grey lighten-2"
        class="font-weight-bold"
        to="/home"
      >
        <v-icon class="mr-2">
          mdi-arrow-left
        </v-icon>
        Back to home
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn
        large
        color="primary"
        class="next-btn font-weight-bold"
        :disabled="authType ==''"
        @click="goNext()"
      >
        Next
        <v-icon class="ml-2">
          mdi-arrow-right
        </v-icon>
      </v-btn>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { LDFlags, LoginSource, Pages, SessionStorageKeys } from '@/util/constants'
import ConfigHelper from '@/util/config-helper'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { mapGetters } from 'vuex'

@Component({
  computed: {
    ...mapGetters('auth', [
      'isAuthenticated',
      'currentLoginSource'
    ])
  }
})

export default class ChooseAuthMethodView extends Vue {
  private readonly isAuthenticated!: boolean
  private readonly currentLoginSource!: string
  private authType = ''
  private isGovN = false

  private get disableGovnAccountCreation (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.DisableGovNAccountCreation) || false
  }

  private selectBCSCAuth () {
    this.authType = LoginSource.BCSC
  }

  private selectBCEIDAuth () {
    this.authType = LoginSource.BCEID
  }

  private linkToNext () {
    ConfigHelper.addToSession(SessionStorageKeys.GOVN_USER, this.isGovN)
    ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'false')
  }

  private goNext () {
    ConfigHelper.addToSession(SessionStorageKeys.GOVN_USER, this.isGovN)
    // TODO might need to set some session variables
    switch (this.authType) {
      case LoginSource.BCEID:
        ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'true')
        this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}/${Pages.SETUP_ACCOUNT_NON_BCSC_INSTRUCTIONS}`)
        window.scrollTo(0, 0)
        break
      case LoginSource.BCSC:
        ConfigHelper.addToSession(SessionStorageKeys.ExtraProvincialUser, 'false') // this flag shouldnt be used for bcsc users.still setting the right value
        if (this.isAuthenticated) {
          if (this.currentLoginSource === LoginSource.BCEID) {
            this.$router.push(`/${Pages.SETUP_ACCOUNT_NON_BCSC}`)
          } else {
            this.$router.push(`/${Pages.CREATE_ACCOUNT}`)
          }
        } else {
          this.$router.push(`/signin/bcsc/${Pages.CREATE_ACCOUNT}`)
        }
        break
    }
  }
}
</script>

<style lang="scss" scoped>
  .view-container {
    max-width: 60rem;
  }

  .col {
    padding: 1rem !important;
  }

  .account-card {
    display: flex;
    flex-direction: column;
    position: relative;
    background-color: #ffffff !important;
    transition: all ease-out 0.2s;

    &:hover {
      border-color: var(--v-primary-base) !important;

      .v-icon {
        color: var(--v-primary-base) !important;
      }
    }

    &.active {
      box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
    }
  }

  .theme--light.v-card.v-card--outlined.active {
    border-color: var(--v-primary-base);
  }

  .account-card .v-icon {
    color: var(--v-grey-lighten1) !important;
    font-size: 3rem !important;
  }

  .account-card.active .v-icon {
    color: var(--v-primary-base) !important;
  }

  .account-type {
    flex: 1 1 auto;
  }

  .account-type__icon {
    flex: 0 0 auto;
  }

  .account-type__title {
    flex: 0 0 auto;
    line-height: 1.75rem;
    font-size: 1.5rem;
    font-weight: 700;
  }

  .account-type__details {
    flex: 1 1 auto;
  }

  .notary-link {
    position: absolute;
    left: 0;
    bottom: 1.5rem;
    width: 100%;
  }

  .lb {
    display: block;
  }
</style>
