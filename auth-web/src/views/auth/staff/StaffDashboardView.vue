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
        <v-card class="pa-8" flat style="height: 100%;">
          <div class="view-header flex-column mb-10">
            <h2 class="view-header__title">Search Entities</h2>
            <p class="mt-3 mb-0">
              Enter the Entity's Incorporation Number below to access their
              dashboard.
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
            <v-text-field
              filled
              label="Incorporation Number"
              hint="example: CP0001234"
              persistent-hint
              dense
              req
              @blur="incorpNumFormat"
              :rules="incorpNumRules"
              v-model="businessNumber"
              id="txtBusinessNumber"
            >
            </v-text-field>
            <v-btn
              color="primary"
              class="search-btn mt-0"
              type="submit"
              depressed
              :disabled="!isFormValid()"
              :loading="searchActive"
              >Search</v-btn
            >
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
      <GLCodesListView></GLCodesListView>
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
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
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
  @OrgModule.Action('getOrganizationForAffiliate')
  private getOrganizationForAffiliate!: () => Promise<Organization>

  @userModule.State('currentUser') private currentUser!: KCUserProfile

  @BusinessModule.Action('searchBusiness') private searchBusiness!: (
    businessIdentifier: string
  ) => Promise<any>
  @BusinessModule.Action('resetCurrentBusiness')
  private resetCurrentBusiness!: () => Promise<any>
  @BusinessModule.State('currentBusiness') private currentBusiness!: Business
  @BusinessModule.Action('loadBusiness') private loadBusiness!: () => Promise<
    Business
  >

  private businessNumber = ''
  private searchedBusinessNumber = ''
  private searchActive = false
  private errorMessage = ''
  private canViewIncorporationSearchResult: boolean = false
  private affiliatedOrg = {}

  private incorpNumRules = [
    v => !!v || 'Incorporation Number is required',
    v =>
      CommonUtils.validateIncorporationNumber(v) ||
      'Incorporation Number is invalid'
  ]

  $refs: {
    searchBusinessForm: HTMLFormElement
  }

  private get canViewAccounts (): boolean {
    return this.currentUser?.roles?.includes(Role.StaffViewAccounts)
  }

  private get canViewGLCodes (): boolean {
    return this.currentUser?.roles?.includes(Role.ManageGlCodes)
  }

  get canSearchFAS (): boolean {
    return this.currentUser?.roles?.includes(Role.FasSearch)
  }

  private isFormValid(): boolean {
    return !!this.businessNumber && this.$refs.searchBusinessForm.validate()
  }

  private clearError() {
    this.searchedBusinessNumber = ''
  }

  async search() {
    if (this.isFormValid()) {
      this.searchActive = true

      try {
        // Search for business, action will set session storage
        await this.searchBusiness(this.businessNumber)
        this.errorMessage = ''
        await this.updateCurrentBusiness()
      } catch (exception) {
        this.searchedBusinessNumber = this.businessNumber
        this.resetCurrentBusiness()
        this.errorMessage = this.$t('noIncorporationNumberFound').toString()
        this.canViewIncorporationSearchResult = false
      } finally {
        this.searchActive = false
      }
    }
  }

  async updateCurrentBusiness() {
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

  incorpNumFormat () {
    this.businessNumber = CommonUtils.formatIncorporationNumber(
      this.businessNumber
    )
  }

  gotToGLCodes() {
    this.$router.push('/glcodelist')
  }

  get isFasDashboardEnabled (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableFasDashboard) || false
  }
}
</script>
<style lang="scss" >
// importing FAS styles need no scope
@import '~fas-ui/src/assets/scss/search.scss';
</style>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';
.v-input {
  display: inline-block;
  width: 20rem;
}

::v-deep {
  .v-input__append-outer {
    margin-top: 0 !important;
  }

  .search-btn {
    margin-left: 0.25rem;
    width: 7rem;
    min-height: 54px;
    vertical-align: top;
    font-weight: bold;
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }
  .v-expansion-panel-content__wrap {
  padding: 0px !important;
  }
}
</style>
