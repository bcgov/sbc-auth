<template>
  <v-container class="view-container">
    <div class="view-header flex-column mb-10">
      <h1 class="view-header__title" data-test="account-settings-title">Create a BC Registries Account</h1>
      <p class="mt-3 mb-0">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at porttitor sem. Aliquam erat volutpat. <span class="lb">Donec placerat nisl magna, et faucibus arcu condimentum sed.</span></p>
    </div>
    <div>
      <v-row>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card flat outlined hover class="account-card text-center px-10 pt-9 pb-12 elevation-2 d-flex"
            @click="selectBCSCAuth()"
            :class="{'active': authType == 'BCSC'}"
            >
            <div class="account-type d-flex flex-column">
              <div class="account-type__icon mb-6">
                <v-icon>mdi-map-marker</v-icon>
              </div>
              <div class="account-type__title mb-6">
                I am a resident <span class="lb">of British Columbia</span>
              </div>
              <div class="account-type__details mb-6">
                Residents of British Columbia can use their government-issued identitification or BC Services Card to verify their identity
              </div>
              <div>
                <a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/log-in-with-card/mobile-card" target="_blank">Learn more about the BC Services card</a>
              </div>
              <!-- State Button (Create Account) -->
              <div class="mt-9 mb-2">
                <v-btn large :outlined="authType != 'BCSC'" block depressed color="primary" class="font-weight-bold">
                   {{ authType == 'BCSC' ? 'SELECTED' : 'SELECT' }}
                </v-btn>
              </div>
              <div class="notary-link">
                <router-link class="caption" to="/extraprov-info">Verify with a notary instead</router-link>
              </div>
            </div>
          </v-card>
        </v-col>
        <v-col class="d-flex align-stretch" sm="12" md="6">
          <v-card flat outlined hover class="account-card text-center px-10 pt-9 pb-12 elevation-2 d-flex"
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
              <div class="mt-9 mb-2">
                <v-btn large :outlined="authType != 'BCEID'" block depressed color="primary" class="font-weight-bold">
                  {{ authType == 'BCEID' ? 'SELECTED' : 'SELECT' }}
                </v-btn>
              </div>
            </div>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </v-container>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue } from 'vue-property-decorator'
import { User } from '@/models/user'
import { VueConstructor } from 'vue'

@Component({
  name: 'Home',
  components: {
  }
})

export default class CreatAccountAuthMethods extends Vue {
  private authType = ''

  private selectBCSCAuth () {
    this.authType = 'BCSC'
  }

  private selectBCEIDAuth () {
    this.authType = 'BCEID'
  }
}
</script>

<style lang="scss" scoped>
  @import "$assets/scss/theme.scss";

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

    &:hover {
      border-color: var(--v-primary-base) !important;
    }

    &.active {
      box-shadow: 0 0 0 2px inset var(--v-primary-base), 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12) !important;
    }
  }

  .v-icon {
    color: var(--v-grey-lighten1) !important;
  }

  .active .v-icon {
    color: var(--v-primary-base) !important;
  }

  .theme--light.v-card.v-card--outlined.active {
    border-color: var(--v-primary-base);
  }

  .account-type {
    flex: 1 1 auto;
  }

  .account-type__icon {
    flex: 0 0 auto;
  }

  .account-type__icon .v-icon {
    font-size: 3rem !important;
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
