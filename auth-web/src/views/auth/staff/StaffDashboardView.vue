<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">Staff Dashboard</h1>
      <p class="mt-3 mb-0">
        Search for businesses and manage BC Registries accounts
      </p>
    </div>

    <v-row class="ma-0 mb-4" no-gutters>
      <v-col class="pr-2" cols="6">
        <v-card class="srch-card" flat style="height: 100%;">
          <div>
            <h2>Business Registry</h2>
            <v-row class="mt-4" no-gutters>
              <v-col class="mr-5" cols="auto">
                <v-btn class="srch-card__link px-0" color="primary" :ripple="false" small text @click="goToManageBusiness()">
                  My Staff Business Registry
                  <v-icon class="ml-1" size="20">mdi-chevron-right-circle-outline</v-icon>
                </v-btn>
              </v-col>
              <v-col>
                <v-btn class="srch-card__link px-0" color="primary" :href="registrySearchUrl" :ripple="false" small target="blank" text>
                  Business Search
                  <v-icon class="ml-1" size="20">mdi-chevron-right-circle-outline</v-icon>
                </v-btn>
              </v-col>
            </v-row>
            <p class="mb-5 mt-4">
              Find an existing business to manage:
            </p>
          </div>

          <v-expand-transition>
            <div v-show="errorMessage">
              <v-alert type="error" icon="mdi-alert-circle" class="mb-0"
                >{{ errorMessage }} <strong>{{ searchedBusinessNumber }}</strong>
              </v-alert>
            </div>
          </v-expand-transition>

          <v-form ref="searchBusinessForm" v-on:submit.prevent="search">
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  filled dense req persistent-hint
                  label="Incorporation Number or Registration Number"
                  hint="Example: BC1234567, CP1234567 or FM1234567"
                  @blur="formatBusinessIdentifier()"
                  :rules="businessIdentifierRules"
                  v-model="businessIdentifier"
                  id="txtBusinessNumber"
                />
              </v-col>
              <v-col cols="auto">
                <v-btn
                  color="primary"
                  class="search-btn mt-0"
                  type="submit"
                  depressed
                  :disabled="!isFormValid()"
                  :loading="searchActive"
                >
                  <span>Search</span>
                </v-btn>
              </v-col>
            </v-row>
          </v-form>

          <template>
            <IncorporationSearchResultView
              :isVisible="canViewIncorporationSearchResult"
              :affiliatedOrg="affiliatedOrg"
            ></IncorporationSearchResultView>
          </template>
        </v-card>
      </v-col>
      <v-col class="pl-2" cols="6">
        <PPRLauncher />
      </v-col>
    </v-row>

    <!-- Director search -->
    <v-card flat class="mb-4 pa-8" v-if="canViewAccounts">
      <StaffAccountManagement></StaffAccountManagement>
    </v-card>

    <!-- GL Codes -->
    <v-card flat class="mb-4 pa-8" v-if="canViewGLCodes">
      <GLCodesListView />
    </v-card>

    <!-- FAS UI  -->
    <v-expansion-panels class="mb-4" accordion v-if="canSearchFAS && isFasDashboardEnabled">
      <v-expansion-panel class="pa-8">
        <v-expansion-panel-header class="px-0">
          <header>
            <h2 class="view-header__title">Fee Accounting System</h2>
            <p class="mt-3 mb-0">
              Search and manage routing slips
            </p>
          </header>
          <template v-slot:actions>
            <v-icon large>
              mdi-chevron-down
            </v-icon>
          </template>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
            <fas-search-component :isLibraryMode="true"/>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script lang="ts">
/* eslint-disable */
import { Component } from 'vue-property-decorator'
import { Business } from '@/models/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import IncorporationSearchResultView from '@/views/auth/staff/IncorporationSearchResultView.vue'
import { KCUserProfile } from 'sbc-common-components/src/models/KCUserProfile'
import { Organization } from '@/models/Organization'
import { LDFlags, Role } from '@/util/constants'
import StaffAccountManagement from '@/components/auth/staff/account-management/StaffAccountManagement.vue'
import PPRLauncher from '@/components/auth/staff/PPRLauncher.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import Vue from 'vue'
import { namespace } from 'vuex-class'

const OrgModule = namespace('org')
const BusinessModule = namespace('business')
const userModule = namespace('user')

@Component({
  components: {
    GLCodesListView,
    SupportInfoCard,
    StaffAccountManagement,
    IncorporationSearchResultView,
    PPRLauncher
  }
})
export default class StaffDashboardView extends Vue {
  $refs: {
    searchBusinessForm: HTMLFormElement
  }

  @OrgModule.Action('getOrganizationForAffiliate')
  private getOrganizationForAffiliate!: () => Promise<Organization>

  @userModule.State('currentUser')
  private currentUser!: KCUserProfile

  @BusinessModule.Action('searchBusiness')
  private searchBusiness!: (businessIdentifier: string) => Promise<any>

  @BusinessModule.Action('resetCurrentBusiness')
  private resetCurrentBusiness!: () => Promise<any>

  @BusinessModule.State('currentBusiness')
  private currentBusiness!: Business

  @BusinessModule.Action('loadBusiness')
  private loadBusiness!: () => Promise<Business>

  // local variables
  protected businessIdentifier = ''
  protected searchedBusinessNumber = ''
  protected searchActive = false
  protected errorMessage = ''
  protected canViewIncorporationSearchResult = false
  protected affiliatedOrg = {}

  readonly businessIdentifierRules = [
    v => !!v || 'Incorporation Number or Registration Number is required',
    v => CommonUtils.validateIncorporationNumber(v) ||
      'Incorporation Number or Registration Number is not valid'
  ]

  get canViewAccounts (): boolean {
    return this.currentUser?.roles?.includes(Role.StaffViewAccounts)
  }

  get canViewGLCodes (): boolean {
    return this.currentUser?.roles?.includes(Role.ManageGlCodes)
  }

  get canSearchFAS (): boolean {
    return this.currentUser?.roles?.includes(Role.FasSearch)
  }

  get isFasDashboardEnabled (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableFasDashboard) || false
  }

  get showBusSearchlink (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.BusSearchLink) || false
  }

  get registrySearchUrl (): string {
    return ConfigHelper.getRegistrySearchUrl()
  }

  protected isFormValid(): boolean {
    return !!this.businessIdentifier && this.$refs.searchBusinessForm?.validate()
  }

  goToManageBusiness(): void {
    this.$router.push('/business')
  }

  protected async search() {
    if (this.isFormValid()) {
      this.searchActive = true

      try {
        // Search for business, action will set session storage
        await this.searchBusiness(this.businessIdentifier)
        this.errorMessage = ''
        await this.updateCurrentBusiness()
      } catch (exception) {
        this.searchedBusinessNumber = this.businessIdentifier
        this.resetCurrentBusiness()
        this.errorMessage = this.$t('noIncorporationNumberFound').toString()
        this.canViewIncorporationSearchResult = false
      } finally {
        this.searchActive = false
      }
    }
  }

  private async updateCurrentBusiness() {
    try {
      // Search for business, action will set session storage
      await this.loadBusiness()
      this.affiliatedOrg = await this.getOrganizationForAffiliate()
      this.canViewIncorporationSearchResult = true
    } catch (exception) {
      // eslint-disable-next-line no-console
      console.log('Error during search incorporations event!')
      this.canViewIncorporationSearchResult = false
      this.resetCurrentBusiness()
    }
  }

  protected formatBusinessIdentifier () {
    this.businessIdentifier =
      CommonUtils.formatIncorporationNumber(this.businessIdentifier)
  }
}
</script>

<style lang="scss" >
// importing FAS styles need no scope
@import '~fas-ui/src/assets/scss/search.scss';
</style>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
h2 {
  line-height: 1.5rem;
}

::v-deep {

  .search-btn {
    margin-left: 0.25rem;
    width: 7rem;
    min-height: 54px;
    vertical-align: top;
    font-weight: bold;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  .srch-card {
    padding: 30px;

    p {
      color: $gray7;
      font-size: 1rem;
      margin: 0;
    }

    &__link {

      .v-btn__content {
        font-size: 1rem;

        i {
          margin-top: 1px;
          opacity: 0.9;
        }
      }
    }

    &__link::before { background-color: white; }
  
    &__reg-srch-link {
      position: absolute;
      right: 32px;
      top: 20px;
    }
  }

  .v-expansion-panel-content__wrap {
    padding: 0px !important;
  }
  
  .v-input__append-outer {
    margin-top: 0 !important;
  }

  .v-text-field__details {
    margin: 0 !important;
  }
}
</style>
