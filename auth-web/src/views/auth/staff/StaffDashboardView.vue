<template>
  <v-container class="view-container">
    <div class="view-header flex-column">
      <h1 class="view-header__title">
        Staff Dashboard
      </h1>
      <p class="mt-3 mb-0">
        Search for businesses and manage BC Registries accounts
      </p>
    </div>

    <v-row
      class="ma-0 mb-4"
      no-gutters
    >
      <v-col
        v-can:VIEW_LAUNCH_TITLES.hide
        class="pr-2"
        cols="6"
      >
        <v-card
          class="srch-card"
          flat
          style="height: 100%;"
        >
          <div>
            <h2>Business Registry</h2>
            <v-row
              class="mt-4"
              no-gutters
            >
              <v-col
                class="mr-5"
                cols="auto"
              >
                <v-btn
                  class="srch-card__link px-0"
                  color="primary"
                  :ripple="false"
                  small
                  text
                  @click="goToManageBusiness()"
                >
                  My Staff Business Registry
                  <v-icon
                    class="ml-1"
                    size="20"
                  >
                    mdi-chevron-right-circle-outline
                  </v-icon>
                </v-btn>
              </v-col>
              <v-col>
                <v-btn
                  class="srch-card__link px-0"
                  color="primary"
                  :href="registrySearchUrl"
                  :ripple="false"
                  small
                  target="blank"
                  text
                >
                  Business Search
                  <v-icon
                    class="ml-1"
                    size="20"
                  >
                    mdi-chevron-right-circle-outline
                  </v-icon>
                </v-btn>
              </v-col>
            </v-row>
            <p class="mb-5 mt-4">
              Find a business or filing number:
            </p>
          </div>

          <v-expand-transition>
            <div v-show="errorMessage">
              <v-alert
                type="error"
                icon="mdi-alert-circle"
                class="mb-0"
              >
                {{ errorMessage }} <strong>{{ searchedIdentifierNumber }}</strong>
              </v-alert>
            </div>
          </v-expand-transition>

          <v-form
            ref="searchIdentifierForm"
            @submit.prevent="search"
          >
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  id="txtSearchIdentifier"
                  v-model="searchIdentifier"
                  filled
                  dense
                  req
                  persistent-hint
                  label="Incorporation, registration or filing number"
                  hint="Example: “BC1234567”, “CP1234567”, “FM1234567” or “123456”"
                  :rules="searchIdentifierRules"
                  @blur="formatSearchIdentifier()"
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
          <IncorporationSearchResultView
            :isVisible="canViewIncorporationSearchResult"
            :affiliatedOrg="affiliatedOrg"
          />
        </v-card>
      </v-col>

      <v-col
        v-can:VIEW_LAUNCH_TITLES.hide
        class="pl-2"
        cols="6"
      >
        <PPRLauncher />
      </v-col>
    </v-row>

    <!-- Director search -->
    <v-card
      v-if="canViewAccounts"
      flat
      class="mb-4 pa-8"
    >
      <StaffAccountManagement />
    </v-card>

    <!-- Continuation Applications -->
    <v-card
      v-can:VIEW_CONTINUATION_AUTHORIZATION_REVIEWS.hide
      flat
      class="mb-4 pa-8"
    >
      <ContinuationApplications />
    </v-card>

    <!-- GL Codes -->
    <BaseVExpansionPanel
      v-if="canViewGLCodes"
      title="General Ledger Codes"
      style="z-index: 0;"
      class="mb-4"
    >
      <template #content>
        <GLCodesListView />
      </template>
    </BaseVExpansionPanel>

    <!-- Transactions -->
    <BaseVExpansionPanel
      v-if="canViewAllTransactions"
      class="mb-4"
      title="Transaction Records"
    >
      <template #content>
        <Transactions
          class="mt-5 pa-0 pr-2"
          :extended="true"
          :showCredit="false"
          :showExport="false"
        />
      </template>
    </BaseVExpansionPanel>

    <!-- EFT -->
    <v-card
      v-if="canViewEFTPayments"
      class="mb-4 pa-8"
    >
      <v-row
        align="center"
        justify="space-between"
      >
        <v-col class="grow">
          <header>
            <h2 class="mb-0">
              Electronic Funds Transfers Received Payments
            </h2>
            <p class="mt-3 mb-0">
              Manage received EFTs
            </p>
          </header>
        </v-col>
        <v-col cols="auto">
          <v-btn
            id="EFT-button"
            class="mt-0 mr-4 font-weight-regular"
            color="primary"
            outlined
            dark
            large
            @click="navigateToManageEFT()"
          >
            <span>Manage EFT Payments</span>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>

    <v-card
      v-if="canSearchFAS && isFasDashboardEnabled"
      class="mb-4 pa-8"
    >
      <v-row
        align="center"
        justify="space-between"
      >
        <v-col class="grow">
          <header>
            <h2 class="mb-0">
              Fee Accounting System
            </h2>
            <p class="mt-3 mb-0">
              Search and manage routing slips
            </p>
          </header>
        </v-col>
        <v-col cols="auto">
          <v-btn
            id="FAS-button"
            class="mt-0 mr-4 font-weight-regular"
            color="primary"
            outlined
            dark
            large
            @click="navigateToFasDashboard()"
          >
            <span>Manage Routing Slips</span>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>

    <!-- Email Safe List -->
    <BaseVExpansionPanel
      v-if="isDevOrTest"
      v-can:VIEW_LAUNCH_TITLES.hide
      info="Please contact #registries-ops to add or remove email addresses from the safe list."
      title="Safe Email List (DEV/TEST)"
    >
      <template #content>
        <v-container>
          <p>Add to Safe Email List</p>
          <v-form
            ref="form"
            class="mt-3"
          >
            <v-row>
              <v-col cols="8">
                <v-text-field
                  v-model="emailToAdd"
                  filled
                  label="Email"
                  class="ml-2"
                />
              </v-col>
              <v-col cols="4">
                <v-btn
                  large
                  depressed
                  color="primary"
                  @click="addEmail"
                >
                  <span>Add</span>
                </v-btn>
              </v-col>
            </v-row>
          </v-form>
        </v-container>
        <SafeEmailView ref="safeEmailView" />
      </template>
    </BaseVExpansionPanel>

    <!-- Feature Launch Tiles: ie Involuntary Dissolution, Document Record Service -->
    <v-row
      v-can:VIEW_LAUNCH_TITLES.hide
    >
      <v-col
        v-for="tile in launchTileConfig"
        :key="tile.title"
        cols="6"
      >
        <LaunchTile :tileConfig="tile" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { BaseVExpansionPanel, LaunchTile } from '@/components'
import { ComputedRef, Ref, computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { LDFlags, Role, SessionStorageKeys } from '@/util/constants'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import ContinuationApplications from '@/components/auth/staff/continuation-application/ContinuationApplications.vue'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import IncorporationSearchResultView from '@/views/auth/staff/IncorporationSearchResultView.vue'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { LaunchTileConfigIF } from '@/models/common'
import { Organization } from '@/models/Organization'
import PPRLauncher from '@/components/auth/staff/PPRLauncher.vue'
import SafeEmailView from '@/views/auth/staff/SafeEmailView.vue'
import { SafeListEmailsRequestBody } from '@/models/Staff'
import StaffAccountManagement from '@/components/auth/staff/account-management/StaffAccountManagement.vue'
import StaffService from '@/services/staff.services'
import { Transactions } from '@/components/auth/account-settings/transaction'
import { useBusinessStore } from '@/stores/business'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

// FUTURE: remove after vue 3 upgrade
interface StaffDashboardViewI {
  searchIdentifier: string
  searchedIdentifierNumber: string
  searchActive: boolean
  errorMessage: string
  canViewIncorporationSearchResult: boolean
  affiliatedOrg: Organization
  canSearchFAS: ComputedRef<boolean>
  canViewAccounts: ComputedRef<boolean>
  canViewGLCodes: ComputedRef<boolean>
  isFasDashboardEnabled: ComputedRef<boolean>
  showBusSearchlink: ComputedRef<boolean>
  registrySearchUrl: ComputedRef<string>
  showDrsTile: ComputedRef<boolean>
  documentsUiUrl: string
  showInvoluntaryDissolutionTile: ComputedRef<boolean>
}

export default defineComponent({
  name: 'StaffDashboardView',
  components: {
    LaunchTile,
    BaseVExpansionPanel,
    SafeEmailView,
    GLCodesListView,
    IncorporationSearchResultView,
    PPRLauncher,
    StaffAccountManagement,
    ContinuationApplications,
    Transactions
  },
  setup (props, { root }) {
    const searchIdentifierForm: Ref<HTMLFormElement> = ref(null)
    const emailToAdd = ref(null)
    const safeEmailView = ref(null)
    const businessStore = useBusinessStore()
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)
    const currentUser = computed(() => userStore.currentUser)

    const searchIdentifierRules = [
      v => !!v || 'Incorporation, registration or filing number is required',
      v => CommonUtils.validateIncorporationNumber(v) || 'Incorporation, registration or filing number is not valid'
    ]

    const localVars = (reactive({
      affiliatedOrg: {},
      searchIdentifier: '',
      canSearchFAS: computed((): boolean => currentUser.value?.roles?.includes(Role.FasSearch)),
      canViewAccounts: computed((): boolean => currentUser.value?.roles?.includes(Role.StaffViewAccounts)),
      canViewAllTransactions: computed((): boolean => currentUser.value?.roles?.includes(Role.ViewAllTransactions)),
      canViewEFTPayments: computed((): boolean => currentUser.value?.roles?.includes(Role.ManageEft)),
      canViewGLCodes: computed((): boolean => currentUser.value?.roles?.includes(Role.ManageGlCodes)),
      isContactCentreStaff: computed(() => currentUser.value?.roles?.includes(Role.ContactCentreStaff)),
      canViewIncorporationSearchResult: false,
      errorMessage: '',
      isFasDashboardEnabled: computed((): boolean => currentUser.value?.roles?.includes(Role.FasSearch)),
      registrySearchUrl: computed((): string => ConfigHelper.getRegistrySearchUrl()),
      documentsUiUrl: computed((): string => ConfigHelper.getBcrosDocumentsUiURL()),
      searchActive: false,
      searchedIdentifierNumber: '',
      showBusSearchlink: computed((): boolean => true),
      showInvoluntaryDissolutionTile: computed((): boolean =>
        LaunchDarklyService.getFlag(LDFlags.EnableInvoluntaryDissolution) || false),
      showDrsTile: computed((): boolean => LaunchDarklyService.getFlag(LDFlags.EnableDRSLookup) || false)
    }) as unknown) as StaffDashboardViewI

    const isFormValid = () => localVars.searchIdentifier && searchIdentifierForm.value?.validate()

    const goToInvoluntaryDissolution = () => root.$router.push(`/staff/involuntary-dissolution`)

    const goToManageBusiness = () => root.$router.push(`/account/${currentOrganization.value?.id}/business`)

    const launchTileConfig: Array<LaunchTileConfigIF> = [
      {
        showTile: localVars.showInvoluntaryDissolutionTile,
        image: 'icon-involuntary-dissolution.svg',
        title: 'Involuntary Dissolution',
        description: 'Set up and manage automation for Involuntary Dissolution of businesses',
        action: () => { goToInvoluntaryDissolution() },
        actionLabel: 'Manage Involuntary Dissolution'
      },
      {
        showTile: localVars.showDrsTile,
        image: 'icon-drs.svg',
        title: 'Document Record Service',
        description: 'Use our document record service to create a new record or search for existing ones. To edit a ' +
          'record, simply search for and open the document record.',
        href: localVars.documentsUiUrl,
        actionLabel: 'Open'
      }
    ]

    const isFilingID = (identifier: string) => {
    // Check if the identifier contains only numeric characters
      return /^\d+$/.test(identifier)
    }

    const isTempBusiness = (identifier: string) => {
      return identifier.charAt(0).toUpperCase() === 'T'
    }

    const resetSearchState = () => {
      businessStore.resetCurrentBusiness()
      businessStore.resetFilingID()
    }

    const updateCurrentBusiness = async () => {
      try {
        // Search for business, action will set session storage
        await businessStore.loadBusiness()
        localVars.affiliatedOrg = await orgStore.getOrganizationForAffiliate()
        localVars.canViewIncorporationSearchResult = true
      } catch (exception) {
        localVars.errorMessage = exception?.message
        localVars.canViewIncorporationSearchResult = false
        businessStore.resetCurrentBusiness()
      }
    }

    const fetchFiling = async () => {
      try {
        await businessStore.loadFiling()
        localVars.affiliatedOrg = await orgStore.getOrganizationForAffiliate()
        localVars.canViewIncorporationSearchResult = true
      } catch (exception) {
        localVars.errorMessage = exception?.message
        localVars.canViewIncorporationSearchResult = false
        businessStore.resetFilingID()
      }
    }

    const search = async () => {
      resetSearchState()

      if (isFormValid()) {
        localVars.searchActive = true

        try {
          localVars.errorMessage = ''

          if (isFilingID(localVars.searchIdentifier)) {
            ConfigHelper.addToSession(SessionStorageKeys.FilingIdentifierKey, localVars.searchIdentifier)
            await fetchFiling()
          } else {
            ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, localVars.searchIdentifier)
          }

          const businessIdentifier = ConfigHelper.getFromSession(SessionStorageKeys.BusinessIdentifierKey)
          if (!isTempBusiness(businessIdentifier)) {
            await updateCurrentBusiness()
          }
        } catch (exception) {
          localVars.searchedIdentifierNumber = localVars.searchIdentifier
          businessStore.resetCurrentBusiness()
          // FUTURE: get this from t(noIncorporationNumberFound)
          // having trouble with composition version of $t in the build.
          localVars.errorMessage = 'No match found for business, registration or filing number'
          localVars.canViewIncorporationSearchResult = false
        } finally {
          localVars.searchActive = false
        }
      }
    }

    const isDevOrTest = computed(() =>
      window.location.href.includes('localhost') ||
      window.location.href.includes('dev.account') ||
      window.location.href.includes('test.account')
    )

    const formatSearchIdentifier = () => {
      if (!isFilingID(localVars.searchIdentifier)) {
        localVars.searchIdentifier = CommonUtils.formatIncorporationNumber(localVars.searchIdentifier)
      }
    }

    async function addEmail () {
      // Call the service method to add the email to the safe list
      try {
        const safeListEmailsRequestBody: SafeListEmailsRequestBody = {
          email: [emailToAdd.value]
        }
        await StaffService.addSafeEmail(safeListEmailsRequestBody)
        await safeEmailView.value.getSafeEmails()
        safeEmailView.value.showGeneralAlert(`Email ${emailToAdd.value} added successfully`, 'success')
        emailToAdd.value = ''
      } catch (error) {
        // eslint-disable-next-line no-console
        const errMsg = `Error adding ${emailToAdd.value}, ${error}`
        console.error(errMsg)
        safeEmailView.value.showGeneralAlert(errMsg, 'error')
      }
    }

    function navigateToFasDashboard () {
      window.location.href = `${ConfigHelper.getPayWebUrl()}?openFromAuth=true`
    }

    function navigateToManageEFT () {
      window.location.href = `${ConfigHelper.getPayWebUrl()}eft`
    }

    return {
      searchIdentifierRules,
      formatSearchIdentifier,
      goToInvoluntaryDissolution,
      goToManageBusiness,
      isDevOrTest,
      safeEmailView,
      isFormValid,
      isFilingID,
      search,
      searchIdentifierForm,
      emailToAdd,
      addEmail,
      launchTileConfig,
      navigateToFasDashboard,
      navigateToManageEFT,
      ...toRefs(localVars)
    }
  }
})
</script>

<style lang="scss" >
// importing FAS styles need no scope
@import '@/assets/scss/search.scss';
</style>

<style lang="scss" scoped>
h2 {
  line-height: 1.5rem;
}

::v-deep {

  .box-shadow {
    box-shadow: 0 3px 1px -2px rgba(0,0,0,.2),0 2px 2px 0 rgba(0,0,0,.14),0 1px 5px 0 rgba(0,0,0,.12);
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
