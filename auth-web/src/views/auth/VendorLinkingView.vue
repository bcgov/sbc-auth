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
            <p class="text-left font-weight-bold mb-4">
              {{ $t('vendorLinkingSelectAccountHeading') }} ({{ eligibleAccounts.length }})
            </p>
            <p class="text-left mb-1">
              {{ $t('vendorLinkingSelectAccountBody') }}
            </p>
            <p class="text-left mb-6">
              <strong>{{ $t('vendorLinkingSelectAccountNoteLabel') }}</strong>
              {{ $t('vendorLinkingAccountSelectAlertNote') }}
            </p>

            <account-select-list
              v-if="eligibleAccounts.length > 0"
              :accounts="eligibleAccounts"
              :action-label="$t('vendorLinkingUseThisAccount')"
              @select="onAccountSelected"
            />
            <vendor-linking-warning-alert
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
            <p class="mb-10">
              {{ $t('vendorLinkingResultSuccessBody', { seconds: remainingSeconds }) }}
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
            <v-btn
              v-if="resultErrorCode !== REDIRECT_URL_INVALID_CODE"
              large
              color="primary"
              data-test="vendor-linking-result-return"
              @click="redirectNow"
            >
              {{ $t('vendorLinkingResultReturnToProvider') }}
            </v-btn>
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
import { Component, Prop, Vue } from 'vue-property-decorator'
import { MembershipType, OrgWithAddress } from '@/models/Organization'
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

@Component({
  components: {
    AccountSelectList,
    VendorLinkingWarningAlert
  }
})
export default class VendorLinkingView extends Vue {
  @Prop({ default: '' }) vendorAccountId: string
  @Prop({ default: '' }) returnUrl: string

  readonly LinkStep = LinkStep
  readonly REDIRECT_URL_INVALID_CODE = REDIRECT_URL_INVALID_CODE

  step: LinkStep = LinkStep.Loading
  eligibleAccounts: OrgWithAddress[] = []
  selectedOrgId: number = null
  resultSuccess: boolean = false
  resultLinkingKey: string = ''
  resultErrorCode: string = ''
  remainingSeconds: number = RESULT_COUNTDOWN_SECONDS
  private countdownTimer: ReturnType<typeof setInterval> = null

  get failureTitle (): string {
    return this.resultErrorCode === REDIRECT_URL_INVALID_CODE
      ? this.$t('vendorLinkingResultFailureRedirectTitle').toString()
      : this.$t('vendorLinkingResultFailureGenericTitle').toString()
  }

  get failureBody (): string {
    return this.resultErrorCode === REDIRECT_URL_INVALID_CODE
      ? this.$t('vendorLinkingResultFailureRedirectBody').toString()
      : this.$t('vendorLinkingResultFailureGenericBody').toString()
  }

  beforeDestroy () {
    this.clearCountdown()
  }

  async mounted () {
    // Re-validated here, not just trusted from the landing page — a bookmarked or
    // back-navigated visit to this route bypasses the landing page's check entirely.
    if (!isValidVendorLinkingParams(this.vendorAccountId, this.returnUrl)) {
      this.step = LinkStep.Error
      return
    }
    try {
      await this.loadEligibleAccounts()
    } catch {
      this.step = LinkStep.Error
    }
  }

  private async loadEligibleAccounts (): Promise<void> {
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

    this.eligibleAccounts = candidates
      .filter((candidate) => ELIGIBLE_MEMBERSHIP_TYPES.has(candidate.membershipTypeCode))
      .map((candidate): OrgWithAddress => ({
        id: candidate.orgId,
        name: candidate.name,
        addressLine: CommonUtils.formatAddressLine(candidate.address)
      }))

    this.step = LinkStep.SelectAccount
  }

  private async onAccountSelected (orgId: number): Promise<void> {
    this.selectedOrgId = orgId
    this.step = LinkStep.Loading
    try {
      const record = await useLinkingKeysStore().createLinkingKey({
        orgId,
        vendorAccountId: Number(this.vendorAccountId),
        returnUrl: this.returnUrl
      })
      this.resultSuccess = true
      this.resultLinkingKey = record.linkingKey
      this.startCountdown()
    } catch (error) {
      const normalized = normalizeError(error)
      this.resultSuccess = false
      this.resultErrorCode = normalized.code || ''
    } finally {
      this.step = LinkStep.Result
    }
  }

  private startCountdown (): void {
    this.remainingSeconds = RESULT_COUNTDOWN_SECONDS
    this.countdownTimer = setInterval(() => {
      this.remainingSeconds -= 1
      if (this.remainingSeconds <= 0) {
        this.redirectNow()
      }
    }, 1000)
  }

  private clearCountdown (): void {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
      this.countdownTimer = null
    }
  }

  private redirectNow (): void {
    this.clearCountdown()
    window.location.replace(this.buildCallbackUrl())
  }

  private buildCallbackUrl (): string {
    const url = new URL(this.returnUrl)
    if (this.resultSuccess) {
      url.searchParams.set('linkingKey', this.resultLinkingKey)
      url.searchParams.set('accountId', String(this.selectedOrgId))
    }
    return url.toString()
  }

  private createAccount (): void {
    // Include full confirm path to continue linking after account creation
    const confirmPath = `/${Pages.VENDOR_LINKING}/confirm` +
      `?vendorAccountId=${this.vendorAccountId}&returnUrl=${encodeURIComponent(this.returnUrl)}`
    this.$router.push(`/${Pages.CREATE_ACCOUNT}?skipConfirmation=true&redirectToUrl=${encodeURIComponent(confirmPath)}`)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/scss/theme.scss';

.vendor-linking-select-account-content {
  max-width: 58rem;
}

.vendor-linking-result-failure-box {
  max-width: 32rem;
  padding: 1rem 1.25rem;
  background-color: $app-background-error;
  border: 1px solid $app-red;
  border-radius: 4px;
}
</style>
