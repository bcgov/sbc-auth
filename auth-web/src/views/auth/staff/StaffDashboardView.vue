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
              Find an existing business to manage:
            </p>
          </div>

          <v-expand-transition>
            <div v-show="errorMessage">
              <v-alert
                type="error"
                icon="mdi-alert-circle"
                class="mb-0"
              >
                {{ errorMessage }} <strong>{{ searchedBusinessNumber }}</strong>
              </v-alert>
            </div>
          </v-expand-transition>

          <v-form
            ref="searchBusinessForm"
            @submit.prevent="search"
          >
            <v-row no-gutters>
              <v-col>
                <v-text-field
                  id="txtBusinessNumber"
                  v-model="businessIdentifier"
                  filled
                  dense
                  req
                  persistent-hint
                  label="Incorporation Number or Registration Number"
                  hint="Example: BC1234567, CP1234567 or FM1234567"
                  :rules="businessIdentifierRules"
                  @blur="formatBusinessIdentifier()"
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

    <!-- GL Codes -->
    <v-card
      v-if="canViewGLCodes"
      flat
      class="mb-4 pa-8"
    >
      <GLCodesListView />
    </v-card>

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
      flat
      class="mb-4 pa-8"
    >
      <v-row
        align="center"
        justify="space-between"
      >
        <v-col class="grow">
          <header>
            <h2 class="mb-0">
              Electronic Funds Transfer Received
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
            @click="$router.push({ name: 'manage-shortnames' })"
          >
            <span>Manage EFT Payments</span>
          </v-btn>
        </v-col>
      </v-row>
    </v-card>

    <!-- FAS UI  -->
    <BaseVExpansionPanel
      v-if="canSearchFAS && isFasDashboardEnabled"
      info="Search and manage routing slips"
      title="Fee Accounting System"
      style="z-index: 0;"
      class="mb-4"
    >
      <!-- <template #content>
        <fas-search-component :isLibraryMode="true" />
      </template> -->
    </BaseVExpansionPanel>

    <!-- Email Safe List -->
    <BaseVExpansionPanel
      v-if="isDevOrTest"
      info="Please contact #registries-ops to add or remove email addresses from the safe list."
      title="Safe Email List (DEV/TEST)"
    >
      <template #content>
        <SafeEmailView />
      </template>
    </BaseVExpansionPanel>
  </v-container>
</template>

<script lang="ts">
import { ComputedRef, Ref, computed, defineComponent, reactive, ref, toRefs } from '@vue/composition-api'
import { Role, SessionStorageKeys } from '@/util/constants'
import { BaseVExpansionPanel } from '@/components'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import GLCodesListView from '@/views/auth/staff/GLCodesListView.vue'
import IncorporationSearchResultView from '@/views/auth/staff/IncorporationSearchResultView.vue'
import { Organization } from '@/models/Organization'
import PPRLauncher from '@/components/auth/staff/PPRLauncher.vue'
import SafeEmailView from '@/views/auth/staff/SafeEmailView.vue'
import StaffAccountManagement from '@/components/auth/staff/account-management/StaffAccountManagement.vue'
import { Transactions } from '@/components/auth/account-settings/transaction'
import { useBusinessStore } from '@/stores/business'
import { useOrgStore } from '@/stores/org'
import { useUserStore } from '@/stores/user'

// FUTURE: remove after vue 3 upgrade
interface StaffDashboardViewI {
  businessIdentifier: string
  searchedBusinessNumber: string
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
}

export default defineComponent({
  name: 'StaffDashboardView',
  components: {
    BaseVExpansionPanel,
    SafeEmailView,
    GLCodesListView,
    IncorporationSearchResultView,
    PPRLauncher,
    StaffAccountManagement,
    Transactions
  },
  setup (props, { root }) {
    const searchBusinessForm: Ref<HTMLFormElement> = ref(null)
    const businessStore = useBusinessStore()
    const orgStore = useOrgStore()
    const userStore = useUserStore()
    const currentOrganization = computed(() => orgStore.currentOrganization)
    const currentUser = computed(() => userStore.currentUser)

    const businessIdentifierRules = [
      v => !!v || 'Incorporation Number or Registration Number is required',
      v => CommonUtils.validateIncorporationNumber(v) || 'Incorporation Number or Registration Number is not valid'
    ]

    const localVars = (reactive({
      businessIdentifier: '',
      searchedBusinessNumber: '',
      searchActive: false,
      errorMessage: '',
      canViewIncorporationSearchResult: false,
      affiliatedOrg: {},
      canSearchFAS: computed((): boolean => currentUser.value?.roles?.includes(Role.FasSearch)),
      canViewAccounts: computed((): boolean => currentUser.value?.roles?.includes(Role.StaffViewAccounts)),
      canViewAllTransactions: computed((): boolean => currentUser.value?.roles?.includes(Role.ViewAllTransactions)),
      canViewGLCodes: computed((): boolean => currentUser.value?.roles?.includes(Role.ManageGlCodes)),
      canViewEFTPayments: computed((): boolean => currentUser.value?.roles?.includes(Role.ManageEft)),
      isFasDashboardEnabled: computed((): boolean => currentUser.value?.roles?.includes(Role.FasSearch)),
      showBusSearchlink: computed((): boolean => true),
      registrySearchUrl: computed((): string => ConfigHelper.getRegistrySearchUrl())
    }) as unknown) as StaffDashboardViewI

    const isFormValid = () => localVars.businessIdentifier && searchBusinessForm.value?.validate()

    const goToManageBusiness = () => root.$router.push(`/account/${currentOrganization.value?.id}/business`)

    const updateCurrentBusiness = async () => {
      try {
        // Search for business, action will set session storage
        await businessStore.loadBusiness()
        localVars.affiliatedOrg = await orgStore.getOrganizationForAffiliate()
        localVars.canViewIncorporationSearchResult = true
      } catch (exception) {
        // eslint-disable-next-line no-console
        console.log('Error during search incorporations event!')
        localVars.canViewIncorporationSearchResult = false
        businessStore.resetCurrentBusiness()
      }
    }

    const search = async () => {
      if (isFormValid()) {
        localVars.searchActive = true

        try {
          ConfigHelper.addToSession(SessionStorageKeys.BusinessIdentifierKey, localVars.businessIdentifier)
          localVars.errorMessage = ''
          await updateCurrentBusiness()
        } catch (exception) {
          localVars.searchedBusinessNumber = localVars.businessIdentifier
          businessStore.resetCurrentBusiness()
          // FUTURE: get this from t(noIncorporationNumberFound)
          // having trouble with composition version of $t in the build.
          localVars.errorMessage = 'No match found for Incorporation Number'
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

    const formatBusinessIdentifier = () => {
      localVars.businessIdentifier =
        CommonUtils.formatIncorporationNumber(localVars.businessIdentifier)
    }

    return {
      searchBusinessForm,
      businessIdentifierRules,
      isFormValid,
      goToManageBusiness,
      search,
      formatBusinessIdentifier,
      isDevOrTest,
      ...toRefs(localVars)
    }
  }
})
</script>

<style lang="scss" >
// importing FAS styles need no scope
@import '~/fas-ui/src/assets/scss/search.scss';
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
