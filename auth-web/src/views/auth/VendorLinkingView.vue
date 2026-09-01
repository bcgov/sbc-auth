<template>
  <v-container class="view-container">
    <template v-if="step === LinkStep.Loading">
      <v-row justify="center">
        <v-col
          cols="12"
          class="text-center"
        >
          <v-progress-circular
            indeterminate
            color="primary"
          />
        </v-col>
      </v-row>
    </template>

    <template v-else-if="step === LinkStep.SelectAccount">
      <v-row justify="center">
        <v-col
          cols="12"
          class="text-center"
        >
          <div class="vendor-linking-select-account-content mx-auto">
            <h1 class="text-left mb-10">
              {{ $t('vendorLinkingSelectAccountTitle') }}
            </h1>
            <p class="vendor-linking-select-account-heading text-left font-weight-bold mb-4">
              {{ $t('vendorLinkingSelectAccountHeading') }}
              <span class="font-weight-regular">({{ eligibleAccounts.length }})</span>
            </p>
            <p class="text-left mb-1">
              {{ $t('vendorLinkingSelectAccountBody') }}
            </p>
            <p class="text-left mb-6">
              <strong>{{ $t('vendorLinkingSelectAccountNoteLabel') }}</strong>
              {{ $t('vendorLinkingAccountSelectAlertNote') }}
            </p>

            <AccountSelectList
              v-if="eligibleAccounts.length > 0"
              :accounts="eligibleAccounts"
              :action-label="$t('vendorLinkingUseThisAccount')"
              @select="onAccountSelected"
            />
            <VendorLinkingWarningAlert
              v-else
              data-test="vendor-linking-no-eligible-accounts-alert"
              :body="$t('vendorLinkingNoEligibleAccountsAlert')"
            />

            <v-btn
              large
              outlined
              color="primary"
              class="mt-6"
              data-test="vendor-linking-create-account-button"
              @click="createAccount"
            >
              {{ $t('vendorLinkingCreateNewAccount') }}
              <v-icon right>
                mdi-chevron-right
              </v-icon>
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </template>

    <template v-else-if="step === LinkStep.Result">
      <v-row justify="center">
        <v-col
          cols="12"
          lg="8"
          class="text-center"
        >
          <template v-if="resultSuccess">
            <v-icon
              size="48"
              color="primary"
              class="mb-6"
            >
              mdi-check
            </v-icon>
            <h2 class="mb-4">
              {{ $t('vendorLinkingResultSuccessTitle') }}
            </h2>
            <p class="mb-1">
              {{ $t('vendorLinkingResultSuccessBody') }}
            </p>
            <p class="mb-10">
              {{ $t('vendorLinkingResultSuccessRedirect', { seconds: remainingSeconds }) }}
            </p>
            <v-btn
              large
              color="primary"
              data-test="vendor-linking-result-continue-now"
              @click="redirectNow"
            >
              {{ $t('vendorLinkingResultContinueNow') }}
            </v-btn>
          </template>
          <template v-else>
            <div class="vendor-linking-result-failure-box text-left mx-auto mb-6">
              <v-icon
                color="error"
                class="mr-2"
              >
                mdi-alert
              </v-icon>
              <span class="font-weight-bold">{{ failureTitle }}</span>
              <p class="mb-0 mt-1">
                {{ failureBody }}
              </p>
            </div>
          </template>
        </v-col>
      </v-row>
    </template>

    <template v-else-if="step === LinkStep.Error">
      <v-row justify="center">
        <v-col
          cols="12"
          lg="8"
          class="text-center"
        >
          <v-icon
            size="48"
            color="error"
            class="mb-6"
          >
            mdi-alert-circle-outline
          </v-icon>
          <h1>{{ $t('vendorLinkingErrorTitle') }}</h1>
          <p class="mt-8 mb-10">
            {{ $t('vendorLinkingErrorBody') }}
          </p>
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>

<script lang="ts">
import { MembershipType, OrgWithAddress } from '@/models/Organization'
import { Ref, computed, defineComponent, getCurrentInstance, onBeforeUnmount, onMounted, ref } from '@vue/composition-api'
import { useLinkingKeysStore, useOrgStore, useUserStore } from '@/stores'
import AccountSelectList from '@/components/auth/common/AccountSelectList.vue'
import CommonUtils from '@/util/common-util'
import { Pages } from '@/util/constants'
import UserService from '@/services/user.services'
import { UserSettings } from '@/models/user'
import VendorLinkingWarningAlert from '@/components/auth/vendor-linking/VendorLinkingWarningAlert.vue'
import { isValidVendorLinkingParams } from '@/util/vendor-connection-util'
import { normalizeError } from '@/util/error-util'

enum LinkStep {
  Loading = 'LOADING',
  SelectAccount = 'SELECT_ACCOUNT',
  Result = 'RESULT',
  Error = 'ERROR'
}

const ELIGIBLE_MEMBERSHIP_TYPES = new Set([MembershipType.Admin, MembershipType.Coordinator])
const RESULT_COUNTDOWN_SECONDS = 5
const REDIRECT_URL_INVALID_CODE = 'REDIRECT_URL_INVALID'

export default defineComponent({
  name: 'VendorLinkingView',
  components: {
    AccountSelectList,
    VendorLinkingWarningAlert
  },
  props: {
    vendorAccountId: {
      type: String,
      default: ''
    },
    returnUrl: {
      type: String,
      default: ''
    }
  },
  setup (props) {
    const instance = getCurrentInstance()

    const step: Ref<LinkStep> = ref(LinkStep.Loading)
    const eligibleAccounts: Ref<OrgWithAddress[]> = ref([])
    const selectedOrgId: Ref<number> = ref(null)
    const resultSuccess: Ref<boolean> = ref(false)
    const resultLinkingKey: Ref<string> = ref('')
    const resultErrorCode: Ref<string> = ref('')
    const remainingSeconds: Ref<number> = ref(RESULT_COUNTDOWN_SECONDS)
    let countdownTimer: ReturnType<typeof setInterval> = null

    const failureTitle = computed(() => {
      return resultErrorCode.value === REDIRECT_URL_INVALID_CODE
        ? instance.proxy.$t('vendorLinkingResultFailureRedirectTitle').toString()
        : instance.proxy.$t('vendorLinkingResultFailureGenericTitle').toString()
    })

    const failureBody = computed(() => {
      return resultErrorCode.value === REDIRECT_URL_INVALID_CODE
        ? instance.proxy.$t('vendorLinkingResultFailureRedirectBody').toString()
        : instance.proxy.$t('vendorLinkingResultFailureGenericBody').toString()
    })

    const clearCountdown = (): void => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
        countdownTimer = null
      }
    }

    const buildCallbackUrl = (): string => {
      const url = new URL(props.returnUrl)
      if (resultSuccess.value) {
        url.searchParams.set('linkingKey', resultLinkingKey.value)
        url.searchParams.set('accountId', String(selectedOrgId.value))
      }
      return url.toString()
    }

    const redirectNow = (): void => {
      clearCountdown()
      window.location.replace(buildCallbackUrl())
    }

    const startCountdown = (): void => {
      remainingSeconds.value = RESULT_COUNTDOWN_SECONDS
      countdownTimer = setInterval(() => {
        remainingSeconds.value -= 1
        if (remainingSeconds.value <= 0) {
          redirectNow()
        }
      }, 1000)
    }

    const loadEligibleAccounts = async (): Promise<void> => {
      const userStore = useUserStore()
      if (!userStore.currentUserAccountSettings?.length) {
        await userStore.getUserAccountSettings()
      }
      const settings: UserSettings[] = userStore.currentUserAccountSettings || []

      const orgStore = useOrgStore()
      const candidates = await Promise.all(settings.map(async (accountSetting) => {
        const orgId = Number.parseInt(accountSetting.id)
        const [address, membershipResponse] = await Promise.all([
          orgStore.getOrgAdminContact(orgId),
          UserService.getMembership(orgId)
        ])
        return { orgId, name: accountSetting.label, address, membershipTypeCode: membershipResponse?.data?.membershipTypeCode }
      }))

      eligibleAccounts.value = candidates
        .filter((candidate) => ELIGIBLE_MEMBERSHIP_TYPES.has(candidate.membershipTypeCode))
        .map((candidate): OrgWithAddress => ({
          id: candidate.orgId,
          name: candidate.name,
          addressLine: CommonUtils.formatAddressLine(candidate.address)
        }))

      step.value = LinkStep.SelectAccount
    }

    const onAccountSelected = async (orgId: number): Promise<void> => {
      selectedOrgId.value = orgId
      step.value = LinkStep.Loading
      try {
        const record = await useLinkingKeysStore().createLinkingKey({
          orgId,
          vendorAccountId: Number(props.vendorAccountId),
          returnUrl: props.returnUrl
        })
        resultSuccess.value = true
        resultLinkingKey.value = record.linkingKey
        startCountdown()
      } catch (error) {
        const normalized = normalizeError(error)
        resultSuccess.value = false
        resultErrorCode.value = normalized.code || ''
      } finally {
        step.value = LinkStep.Result
      }
    }

    const createAccount = (): void => {
      // Include full confirm path to continue linking after account creation
      const confirmPath = `/${Pages.VENDOR_LINKING}/confirm` +
        `?vendorAccountId=${props.vendorAccountId}&returnUrl=${encodeURIComponent(props.returnUrl)}`
      instance.proxy.$router.push(`/${Pages.CREATE_ACCOUNT}?skipConfirmation=true&redirectToUrl=${encodeURIComponent(confirmPath)}`)
    }

    onMounted(async () => {
      // Re-validated here, not just trusted from the landing page — a bookmarked or
      // back-navigated visit to this route bypasses the landing page's check entirely.
      if (!isValidVendorLinkingParams(props.vendorAccountId, props.returnUrl)) {
        step.value = LinkStep.Error
        return
      }
      try {
        await loadEligibleAccounts()
      } catch {
        step.value = LinkStep.Error
      }
    })

    onBeforeUnmount(() => {
      clearCountdown()
    })

    return {
      LinkStep,
      step,
      eligibleAccounts,
      resultSuccess,
      remainingSeconds,
      failureTitle,
      failureBody,
      onAccountSelected,
      redirectNow,
      createAccount
    }
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.vendor-linking-select-account-content {
  max-width: 58rem;
}

.vendor-linking-select-account-heading {
  color: $gray9;
}

.vendor-linking-result-failure-box {
  max-width: 32rem;
  padding: 1rem 1.25rem;
  background-color: $app-background-error;
  border: 1px solid $app-red;
  border-radius: 4px;
}
</style>
