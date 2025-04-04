<template>
  <div id="entity-management">
    <v-fade-transition>
      <div
        v-show="!!isLoading"
        class="loading-container grayed-out"
      >
        <v-progress-circular
          size="50"
          width="5"
          color="primary"
          :indeterminate="!!isLoading"
        />
      </div>
    </v-fade-transition>

    <v-container class="view-container justify">
      <div class="view-header align-center">
        <h1 class="view-header__title">
          {{ viewTitle }}<br>
          <span class="subtitle">{{ $t('myBusinessDashSubtitle') }}</span>
        </h1>
        <div class="view-header__actions">
          <v-tooltip
            top
            content-class="top-tooltip"
          >
            <template #activator="{ on: onGetStartedTooltip }">
              <v-btn
                id="get-started-button"
                class="mt-0 mr-4 font-weight-regular"
                color="primary"
                outlined
                dark
                large
                v-on="{ ...onGetStartedTooltip }"
                @click="onClickGoToNameRequest()"
              >
                <v-icon
                  small
                >
                  mdi-domain
                </v-icon>
                <span>Get Started with a B.C. Based Business</span>
              </v-btn>
            </template>
            <span id="tooltip">Go to Name Request to get started with a named or numbered business.</span>
          </v-tooltip>
        </div>
      </div>

      <ExpandableHelp
        class="mb-9"
        helpLabel="Help with Starting and Managing a Business"
      >
        <template #content>
          <StartNewBusinessHelp class="help-text" />
        </template>
      </ExpandableHelp>

      <SearchBusinessNameRequest
        ref="searchBusinessNameRequest"
        :orgId="orgId"
        :showManageBusinessDialog="showManageBusinessDialog"
        @add-success="showAddSuccessModal"
        @add-failed-invalid-code="showInvalidCodeModal($event)"
        @add-failed-no-entity="showEntityNotFoundModal()"
        @add-failed-passcode-claimed="showPasscodeClaimedModal()"
        @unknown-error="showUnknownErrorModal"
        @business-already-added="showBusinessAlreadyAdded($event)"
        @hide-manage-business-dialog="hideManageBusinessDialog()"
        @show-manage-business-dialog="showManageBusinessDialogForBusiness($event)"
        @on-business-identifier="businessIdentifier = $event"
        @add-success-nr="showAddSuccessModalNR"
        @add-nr-error="showNRErrorModal()"
        @add-failed-no-nr="showNRNotFoundModal()"
        @on-authorization-email-sent-close="onAuthorizationEmailSentClose($event)"
      />

      <AffiliatedEntityTable
        :loading="isLoading"
        :highlight-index="highlightIndex"
        @unknown-error="showUnknownErrorModal('business')"
        @remove-affiliation-invitation="removeAffiliationInvitation()"
        @remove-business="showConfirmationOptionsModal($event)"
        @business-unavailable-error="showBusinessUnavailableModal($event)"
        @resend-affiliation-invitation="resendAffiliationInvitation($event)"
        @show-manage-business-dialog="selectBusiness($event)"
      />

      <PasscodeResetOptionsModal
        ref="passcodeResetOptionsModal"
        data-test="dialog-passcode-reset-options"
        @confirm-passcode-reset-options="remove($event)"
      />

      <AuthorizationEmailSentDialog
        :isVisible="isAuthorizationEmailSentDialogVisible"
        :email="businessContactEmail"
        @open-help="openHelp"
        @close-dialog="onAuthorizationEmailSentClose"
      />

      <!-- Success Dialog -->
      <ModalDialog
        ref="successDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="720"
      />

      <!-- NR/IA removal confirm Dialog/A generic one -->
      <ModalDialog
        ref="removalConfirmDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="720"
        data-test="remove-confirm-dialog"
      >
        <template #icon>
          <v-icon
            large
            color="error"
          >
            mdi-alert-circle-outline
          </v-icon>
        </template>
        <template #actions>
          <v-btn
            large
            color="primary"
            data-test="dialog-ok-button"
            @click="primaryBtnHandler()"
          >
            {{ primaryBtnText }}
          </v-btn>
          <v-btn
            large
            data-test="dialog-ok-button"
            @click="secondaryBtnHandler()"
          >
            {{ secondaryBtnText }}
          </v-btn>
        </template>
      </ModalDialog>

      <HelpDialog
        ref="helpDialog"
        :helpDialogBlurb="helpDialogBlurb"
      />

      <!-- Error Dialog -->
      <ModalDialog
        ref="errorDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="720"
      >
        <template #icon>
          <v-icon
            large
            color="error"
          >
            mdi-alert-circle-outline
          </v-icon>
        </template>
        <template #actions>
          <v-btn
            large
            color="primary"
            data-test="dialog-ok-button"
            @click="close()"
          >
            Close
          </v-btn>
        </template>
      </ModalDialog>

      <!-- Link Expire Error Dialog -->
      <ModalDialog
        ref="linkExpireErrorDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="720"
      >
        <template #icon>
          <v-icon
            large
            color="error"
          >
            mdi-alert-circle-outline
          </v-icon>
        </template>
        <template #actions>
          <v-btn
            large
            outlined
            color="primary"
            data-test="dialog-ok-button"
            @click="closeLinkExpireErrorDialog()"
          >
            Return to My List
          </v-btn>
          <v-btn
            large
            color="primary"
            data-test="dialog-ok-button"
            @click="resendAffiliationInvitation()"
          >
            Re-send Authorization Email
          </v-btn>
        </template>
      </ModalDialog>

      <!-- Business Unavailable Dialog for unaffiliated business-->
      <ModalDialog
        ref="businessUnavailableDialog"
        class="business-unavailable-dialog"
        :title="dialogTitle"
        max-width="720"
        dialog-class="info-dialog"
        :showIcon="false"
        :showCloseIcon="true"
      >
        <template #text>
          <p>{{ dialogText }}</p>
          <p><br>Please contact us if you require assistance.</p>
          <br>
          <v-icon small>
            mdi-phone
          </v-icon>  Canada and U.S. Toll Free: <a href="tel:+1-877-526-1526">1-877-526-1526</a>
          <br>
          <v-icon small>
            mdi-phone
          </v-icon>  Victoria Office: <a href="tel:250-387-7848">250-387-7848</a>
          <br>
          <v-icon small>
            mdi-email
          </v-icon>  Email: <a href="mailto:BCRegistries@gov.bc.ca">BCRegistries@gov.bc.ca</a>
        </template>
        <template #actions>
          <v-btn
            large
            color="primary"
            data-test="dialog-ok-button"
            @click="closeBusinessUnavailableDialog()"
          >
            OK
          </v-btn>
        </template>
      </ModalDialog>

      <!-- Dialog for confirming business removal -->
      <ModalDialog
        ref="removedBusinessSuccessDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="720"
        :isPersistent="true"
      >
        <template #icon>
          <v-icon
            large
            color="primary"
          >
            mdi-check
          </v-icon>
        </template>
        <template #actions>
          <v-btn
            large
            color="primary"
            data-test="removed-business-success-button"
            @click="removedBusinessSuccessClose()"
          >
            Close
          </v-btn>
        </template>
      </ModalDialog>
      <!-- Message for successfully adding business or name request -->
      <v-snackbar
        id="success-nr-business-snackbar"
        v-model="showSnackbar"
        :timeout="timeoutMs"
        transition="fade"
      >
        {{ snackbarText }}
      </v-snackbar>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { CorpTypes, LoginSource, MagicLinkInvitationStatus, Pages } from '@/util/constants'
import { MembershipStatus, Organization, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapState } from 'pinia'
import { useAppStore, useBusinessStore, useOrgStore, useUserStore } from '@/stores'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import AccountMixin from '@/components/auth/mixins/AccountMixin.vue'
import { Action } from 'pinia-class'
import { Address } from '@/models/address'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import AffiliationInvitationService from '@/services/affiliation-invitation.services'
import AuthorizationEmailSentDialog from './AuthorizationEmailSentDialog.vue'
import { Base64 } from 'js-base64'
import { Business } from '@/models/business'
import BusinessService from '@/services/business.services'
import ConfigHelper from '@/util/config-helper'
import ExpandableHelp from '@/components/auth/common/ExpandableHelp.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import ManageBusinessDialog from '@/components/auth/manage-business/manage-business-dialog/ManageBusinessDialog.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import PasscodeResetOptionsModal from '@/components/auth/manage-business/PasscodeResetOptionsModal.vue'
import SearchBusinessNameRequest from './SearchBusinessNameRequest.vue'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import StartNewBusinessHelp from '@/components/auth/manage-business/StartNewBusinessHelp.vue'
import { UserSettings } from 'sbc-common-components/src/models/userSettings'
import { appendAccountId } from 'sbc-common-components/src/util/common-util'

@Component({
  components: {
    AffiliatedEntityTable,
    AuthorizationEmailSentDialog,
    ExpandableHelp,
    ManageBusinessDialog,
    ModalDialog,
    HelpDialog,
    PasscodeResetOptionsModal,
    SearchBusinessNameRequest,
    StartNewBusinessHelp
  },
  computed: {
    ...mapState(useOrgStore, ['currentOrgAddress', 'currentAccountSettings']),
    ...mapState(useUserStore, ['userProfile', 'currentUser'])
  },
  methods: {
    ...mapActions(useBusinessStore, ['searchBusinessIndex', 'getBusinessNameByIdentifier', 'searchNRIndex',
      'syncBusinesses', 'removeBusiness', 'createNumberedBusiness']),
    ...mapActions(useOrgStore, ['syncAddress'])
  }
})
export default class EntityManagement extends Mixins(AccountMixin, AccountChangeMixin, NextPageMixin) {
  @Prop({ default: '' }) readonly orgId: string
  @Prop({ default: '' }) readonly base64Token: string
  @Prop({ default: '' }) readonly base64OrgName: string
  @Action(useOrgStore) addOrgSettings!: (org: Organization) => Promise<UserSettings>
  // for template
  readonly CorpTypes = CorpTypes
  removeBusinessPayload = null
  dialogTitle = ''
  dialogText = ''
  isLoading: boolean = false // truthy
  businessIdentifier: string = null
  primaryBtnText = ''
  secondaryBtnText = ''
  primaryBtnHandler: () => void = undefined
  secondaryBtnHandler: () => void = undefined
  lastSyncBusinesses = 0
  showManageBusinessDialog = false
  isAuthorizationEmailSentDialogVisible = false
  businessContactEmail = ''
  snackbarText: string = null
  showSnackbar = false
  timeoutMs = 4000
  highlightRowIndex = NaN // for newly added NR or Business

  /** V-model for dropdown menus. */
  addAffiliationDropdown: boolean = false

  readonly searchBusinessIndex!: (identifier: string) => Promise<number>
  readonly getBusinessNameByIdentifier!: (identifier: string) => Promise<string | null>
  readonly searchNRIndex!: (identifier: string) => Promise<number>
  readonly syncBusinesses!: () => Promise<void>
  readonly removeBusiness!: (removeBusinessPayload: RemoveBusinessPayload) => Promise<void>
  readonly createNumberedBusiness!: ({ filingType, business }) => Promise<void>
  readonly currentOrgAddress!: Address
  readonly syncAddress!: () => Address
  highlightIndex = -1

  $refs: {
    successDialog: InstanceType<typeof ModalDialog>
    errorDialog: InstanceType<typeof ModalDialog>
    passcodeResetOptionsModal: PasscodeResetOptionsModal
    removedBusinessSuccessDialog: InstanceType<typeof ModalDialog>
    removalConfirmDialog: InstanceType<typeof ModalDialog>
    businessUnavailableDialog: InstanceType<typeof ModalDialog>
    linkExpireErrorDialog: InstanceType<typeof ModalDialog>
    helpDialog: InstanceType<typeof ModalDialog>
    searchBusinessNameRequest: SearchBusinessNameRequest
  }

  async mounted () {
    if (this.currentMembership === undefined) {
      this.$router?.push(`/${Pages.CREATE_ACCOUNT}`)
      return
    }
    // If pending approval on current account, redirect away
    if (this.currentMembership?.membershipStatus !== MembershipStatus.Active) {
      this.$router?.push(this.getNextPageUrl())
      return
    }
    // check if address info is complete
    const isNotAnonUser = this.currentUser?.loginSource !== LoginSource.BCROS
    if (isNotAnonUser) {
      // do it only if address is not already fetched.Or else try to fetch from DB
      if (!this.currentOrgAddress || Object.keys(this.currentOrgAddress).length === 0) {
        // sync and try again
        await this.syncAddress()
        if (!this.currentOrgAddress || Object.keys(this.currentOrgAddress).length === 0) {
          await this.$router?.push(`/${Pages.MAIN}/${this.orgId}/settings/account-info`)
          return
        }
      }
    }

    this.setAccountChangedHandler(this.setup)
    await this.setup()

    if (this.base64Token && this.base64OrgName) {
      const base64TokenObject = this.base64Token.split('.')[0]
      const decodedToken = Base64.decode(base64TokenObject)
      const token = JSON.parse(decodedToken)
      const legalName = Base64.decode(this.base64OrgName)
      await this.handleMagicLink(token, legalName)
    }
  }

  async handleMagicLink (token: any, legalName: string) {
    const currentOrgId = JSON.parse(sessionStorage.getItem(SessionStorageKeys.CurrentAccount)).id
    if (currentOrgId !== Number(this.orgId)) {
      this.setCurrentAccountSettings({
        id: Number(this.orgId),
        label: legalName,
        type: 'ACCOUNT',
        urlpath: '',
        urlorigin: ''
      })
      try {
        await this.syncOrganization(this.currentAccountSettings.id)
        await this.addOrgSettings(this.currentOrganization)
        await this.syncBusinessesAndToggleLoading()
        useAppStore().updateHeader()
        this.parseUrlAndAddAffiliation(token, legalName, this.base64Token)
        return
      } catch (error) {
        this.showAuthorizationErrorModal()
      }
    }
    await this.syncBusinessesAndToggleLoading()
    this.parseUrlAndAddAffiliation(token, legalName, this.base64Token)
  }

  // Function to parse the URL and extract the parameters, used for magic link email
  async parseUrlAndAddAffiliation (token: any, legalName: string, base64Token: string) {
    if (!this.$route.meta.checkMagicLink) {
      return
    }
    const identifier = token.businessIdentifier
    const invitationId = token.id
    this.businessIdentifier = token.businessIdentifier
    // grab business name from store
    const business = await this.getBusinessNameByIdentifier(token.businessIdentifier)
    try {
      // 1. Accept invitation
      const response = await AffiliationInvitationService.acceptInvitation(invitationId, base64Token)

      // 2. Adding magic link success
      if (response.status === 200) {
        this.showAddSuccessModalByEmail(identifier)
      }
    } catch (error) {
      console.log(error)
      // 3. Unauthorized
      if (error.response && error.response?.status === 401) {
        this.showAuthorizationErrorModal()
        return
      }
      // 4. Expired
      if (error.response && error.response?.status === 400 &&
        error.response?.data.code === MagicLinkInvitationStatus.EXPIRED_AFFILIATION_INVITATION) {
        this.showLinkExpiredModal(identifier)
        return
      }

      // 5. Already Added
      if (error.response && error.response?.status === 400 &&
        error.response?.data.code === MagicLinkInvitationStatus.ACTIONED_AFFILIATION_INVITATION) {
        this.showBusinessAlreadyAdded({ name: business, identifier })
        return
      }
      // 6. Error
      this.showMagicLinkErrorModal()
    }
  }

  async resendAffiliationInvitation (event = null) {
    let invitationId = ''

    if (this.base64Token && this.base64OrgName) {
      const base64TokenObject = this.base64Token.split('.')[0]
      const decodedToken = Base64.decode(base64TokenObject)
      const token = JSON.parse(decodedToken)
      invitationId = token.id
    }

    if (event?.affiliationInvites[0].businessIdentifier) {
      this.businessIdentifier = event?.affiliationInvites[0].businessIdentifier
    }

    try {
      const affiliationInvitationId = invitationId || event?.affiliationInvites[0].id
      await AffiliationInvitationService.updateInvitation(affiliationInvitationId)
      const contact = await BusinessService.getMaskedContacts(this.businessIdentifier)
      this.businessContactEmail = contact?.data?.email
      this.isAuthorizationEmailSentDialogVisible = true
    } catch (err) {
      this.showCreateAffiliationInvitationErrorDialog()
    }
  }

  get helpDialogBlurb (): string {
    return 'If you have not received your Access Letter from BC Registries, or have lost your Passcode, ' +
        'please contact us at:'
  }

  async syncBusinessesAndToggleLoading () {
    this.isLoading = true
    await this.syncBusinesses()
    this.isLoading = false
  }

  openHelp () {
    this.$refs.helpDialog.open()
  }

  async setup (): Promise<void> {
    // ensure syncBusinesses isn't already running
    if (this.isLoading === true) {
      return
    }

    // ensure syncBusinesses hasn't just been run
    if (Date.now() - this.lastSyncBusinesses < 2000) {
      return
    }

    await this.syncBusinessesAndToggleLoading()
    this.lastSyncBusinesses = Date.now()
  }

  get viewTitle (): string {
    return this.isSbcStaffAccount || this.isStaffAccount
      ? 'My Staff Business Registry'
      : 'My Business Registry'
  }

  onClickGoToNameRequest (): void {
    window.location.href = appendAccountId(ConfigHelper.getNameRequestUrl())
  }

  showManageBusinessDialogForBusiness (business: Business) {
    this.businessIdentifier = business.businessIdentifier
    this.showManageBusinessDialog = true
  }

  selectBusiness (business: Business) {
    const event = { name: business.name, identifier: business.businessIdentifier, legalType: business.corpType?.code }
    this.$refs?.searchBusinessNameRequest.selectBusiness(event)
  }

  hideManageBusinessDialog () {
    this.showManageBusinessDialog = false
  }

  async showAddSuccessModal (businessIdentifier: string) {
    this.showManageBusinessDialog = false
    this.dialogTitle = 'Business Added'
    this.dialogText = 'You have successfully added a business'
    await this.syncBusinessesAndToggleLoading()
    this.highlightIndex = await this.searchBusinessIndex(businessIdentifier)
    this.snackbarText = businessIdentifier + ' was successfully added to your table.'
    this.showSnackbar = true
    setTimeout(() => {
      this.highlightIndex = -1
    }, 4000)
  }

  async showAddSuccessModalByEmail (businessIdentifier: string) {
    await this.syncBusinessesAndToggleLoading()
    this.highlightIndex = await this.searchBusinessIndex(businessIdentifier)
    this.snackbarText = 'You can now manage ' + businessIdentifier + '.'
    this.showSnackbar = true
    setTimeout(() => {
      this.highlightIndex = -1
    }, 4000)
  }

  async showAddSuccessModalNR (nameRequestNumber: string) {
    this.dialogTitle = 'Name Request Added'
    this.dialogText = 'You have successfully added a name request'
    await this.syncBusinessesAndToggleLoading()
    const nameRequestIndexResponse = await this.searchNRIndex(nameRequestNumber)

    this.snackbarText = `${nameRequestNumber} was successfully added to your table.`
    this.showSnackbar = true
    this.highlightIndex = nameRequestIndexResponse
    setTimeout(() => {
      this.highlightIndex = -1
    }, 4000)
  }

  async onAuthorizationEmailSentClose (businessIdentifier: string) {
    this.isAuthorizationEmailSentDialogVisible = false
    await this.syncBusinessesAndToggleLoading()
    // This function doesn't always have the businessIdentifier passed to it.
    const validBusinessIdentifier = businessIdentifier || this.businessIdentifier
    this.highlightIndex = await this.searchBusinessIndex(validBusinessIdentifier)
    this.snackbarText = 'Confirmation email sent, pending authorization.'
    this.showSnackbar = true
    this.businessIdentifier = null
    setTimeout(() => {
      this.highlightIndex = -1
    }, 4000)
  }

  showInvalidCodeModal (label: string) {
    this.showManageBusinessDialog = false
    this.dialogTitle = `Invalid ${label}`
    this.dialogText = `Unable to add the business. The provided ${label.toLowerCase()} is invalid.`
    this.$refs.errorDialog.open()
  }

  showEntityNotFoundModal () {
    this.showManageBusinessDialog = false
    this.dialogTitle = 'Business Not Found'
    this.dialogText = 'The specified business was not found.'
    this.$refs.errorDialog.open()
  }

  showBusinessAlreadyAdded (event: { name, identifier }) {
    this.showManageBusinessDialog = false
    this.dialogTitle = 'Business Already Added'
    const businessNameText = event.name ? `${event.name}` : ''
    this.dialogText = `The business ${businessNameText} with the business number ${event.identifier} is already in your Business Registry List.`
    this.$refs.errorDialog.open()
  }

  showNRNotFoundModal () {
    this.dialogTitle = 'Name Request Not Found'
    this.dialogText = 'The specified name request was not found.'
    this.$refs.errorDialog.open()
  }

  showNRErrorModal () {
    this.dialogTitle = 'Error Adding Name Request'
    this.dialogText =
    'We couldn\'t find a name request associated with the phone number or email address you entered. Please try again.'
    this.$refs.errorDialog.open()
  }

  showLinkExpiredModal (name: string) {
    this.dialogTitle = `Link Expired`
    this.dialogText = `Your authorization request to manage ${name} has expired. Please try again.`
    this.$refs.linkExpireErrorDialog.open()
  }

  showAuthorizationErrorModal () {
    this.dialogTitle = 'Unable to Manage Business'
    this.dialogText =
    'The account that requested authorisation does not match your current account. Please log in as the account that initiated the request.'
    this.$refs.errorDialog.open()
  }

  showCreateAffiliationInvitationErrorDialog () {
    this.dialogTitle = 'Error Sending Authorization Email'
    this.dialogText = 'An error occurred sending authorization email. Please try again.'
    this.$refs.errorDialog.open()
  }

  showMagicLinkErrorModal () {
    this.dialogTitle = 'Error Adding a Business to Your Account'
    this.dialogText =
    'An error occurred adding your business. Please try again.'
    this.$refs.errorDialog.open()
  }

  showPasscodeClaimedModal () {
    const contactNumber = this.$t('techSupportTollFree').toString()
    this.showManageBusinessDialog = false
    this.dialogTitle = 'Passcode Already Claimed'
    this.dialogText = `This passcode has already been claimed. If you have questions, please call ${contactNumber}`
    this.$refs.errorDialog.open()
  }

  showUnknownErrorModal (type: string) {
    if (type === 'business') {
      this.showManageBusinessDialog = false
      this.dialogTitle = 'Error Adding Existing Business'
      this.dialogText = 'An error occurred adding your business. Please try again.'
    } else if (type === 'nr') {
      this.dialogTitle = 'Error Adding Existing Name Request'
      this.dialogText = 'We couldn\'t find a name request associated with the phone number or email address you entered. Please try again.'
    } else {
      this.dialogTitle = 'Something Went Wrong'
      this.dialogText = 'An error occurred, please try again. If this error persists, please contact us.'
    }
    this.$refs.errorDialog.open()
  }

  showAddBusinessModal () {
    this.showManageBusinessDialog = true
  }

  async removeAffiliationInvitation () {
    await this.syncBusinessesAndToggleLoading()
  }

  showConfirmationOptionsModal (removeBusinessPayload: RemoveBusinessPayload) {
    this.removeBusinessPayload = removeBusinessPayload
    if (removeBusinessPayload.business.corpType.code === CorpTypes.NAME_REQUEST) {
      this.populateNRmodalValues()
      this.$refs.removalConfirmDialog.open()
    } else if (removeBusinessPayload.business.corpType.code === CorpTypes.INCORPORATION_APPLICATION) {
      this.populateIAmodalValues()
      this.$refs.removalConfirmDialog.open()
    } else if (removeBusinessPayload.business.corpType.code === CorpTypes.AMALGAMATION_APPLICATION) {
      this.populateAmalagmationModalValues()
      this.$refs.removalConfirmDialog.open()
    } else if (removeBusinessPayload.business.corpType.code === CorpTypes.CONTINUATION_IN) {
      this.populateContinuationInModalValues()
      this.$refs.removalConfirmDialog.open()
    } else if (removeBusinessPayload.business.corpType.code === CorpTypes.REGISTRATION) {
      this.populateRegistrationModalValues()
      this.$refs.removalConfirmDialog.open()
    } else if (
      removeBusinessPayload.business.corpType.code === CorpTypes.PARTNERSHIP ||
      removeBusinessPayload.business.corpType.code === CorpTypes.SOLE_PROP
    ) {
      this.populateFirmModalValues()
      this.$refs.removalConfirmDialog.open()
    } else {
      this.$refs.passcodeResetOptionsModal.open()
    }
  }

  showBusinessUnavailableModal (action: string) {
    this.dialogTitle = 'Business Unavailable'
    this.dialogText = 'You are not authorized to access the business'
    if (action === 'change name') {
      this.dialogText += ' to change its name'
    } else {
      this.dialogText += ' you wish to ' + action
    }
    this.dialogText += '. Please add this business to your table to continue.'
    this.$refs.businessUnavailableDialog.open()
  }

  populateNRmodalValues () {
    this.dialogTitle = this.$t('removeNRConfirmTitle').toString()
    this.dialogText = this.$t('removeNRConfirmText').toString()
    this.primaryBtnText = 'Remove Name Request'
    this.secondaryBtnText = 'Keep Name Request'
    this.primaryBtnHandler = this.confirmRemovalNr
    this.secondaryBtnHandler = this.cancelRemoval
  }

  populateIAmodalValues () {
    this.dialogTitle = this.$t('removeIAConfirmTitle').toString()
    this.dialogText = this.$t('removeIAConfirmText').toString()
    this.primaryBtnText = 'Delete Incorporation Application'
    this.secondaryBtnText = 'Keep Incorporation Application'
    this.primaryBtnHandler = this.confirmRemovalIA
    this.secondaryBtnHandler = this.cancelRemoval
  }

  populateAmalagmationModalValues () {
    this.dialogTitle = this.$t('removeAmalgamationConfirmTitle').toString()
    this.dialogText = this.$t('removeAmalgamationConfirmText').toString()
    this.primaryBtnText = 'Delete Amalgamation Application'
    this.secondaryBtnText = 'Keep Amalgamation Application'
    this.primaryBtnHandler = this.confirmRemovalAmalgamation
    this.secondaryBtnHandler = this.cancelRemoval
  }

  populateContinuationInModalValues () {
    this.dialogTitle = this.$t('removeContinuationInConfirmTitle').toString()
    this.dialogText = this.$t('removeContinuationInConfirmText').toString()
    this.primaryBtnText = 'Delete Continuation Application'
    this.secondaryBtnText = 'Keep Continuation Application'
    this.primaryBtnHandler = this.confirmRemovalContinuationIn
    this.secondaryBtnHandler = this.cancelRemoval
  }

  populateRegistrationModalValues () {
    this.dialogTitle = this.$t('removeRegistrationConfirmTitle').toString()
    this.dialogText = this.$t('removeRegistrationConfirmText').toString()
    this.primaryBtnText = 'Delete Registration'
    this.secondaryBtnText = 'Keep Registration'
    this.primaryBtnHandler = this.confirmRemovalRegistration
    this.secondaryBtnHandler = this.cancelRemoval
  }

  populateFirmModalValues () {
    this.dialogTitle = this.$t('removeFirmConfirmTitle').toString()
    this.dialogText = this.$t('removeFirmConfirmText').toString()
    this.primaryBtnText = 'Remove Registration'
    this.secondaryBtnText = 'Keep Registration'
    this.primaryBtnHandler = this.confirmRemovalFirm
    this.secondaryBtnHandler = this.cancelRemoval
  }

  cancelRemoval () {
    this.$refs.removalConfirmDialog.close()
  }

  confirmRemovalRegistration () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeRegistrationSuccessTitle', 'removeRegistrationSuccessText')
  }

  confirmRemovalIA () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeIASuccessTitle', 'removeIASuccessText')
  }

  confirmRemovalAmalgamation () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeAmalgamationSuccessTitle', 'removeAmalgamationSuccessText')
  }

  confirmRemovalContinuationIn () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeContinuationInSuccessTitle', 'removeContinuationInSuccessText')
  }

  confirmRemovalNr () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeNRSuccessTitle', 'removeNRSuccessText')
  }

  confirmRemovalFirm () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeFirmSuccessTitle', 'removeFirmSuccessText')
  }

  async remove (resetPasscodeEmail: string, resetPasscode = true, dialogTitleKey = 'removeBusiness', dialogTextKey = 'removedBusinessSuccessText') {
    try {
      this.removeBusinessPayload.passcodeResetEmail = resetPasscodeEmail
      this.removeBusinessPayload.resetPasscode = resetPasscode
      this.$refs.passcodeResetOptionsModal.close()
      await this.removeBusiness(this.removeBusinessPayload)
      this.dialogText = this.$t(dialogTextKey).toString()
      this.dialogTitle = this.$t(dialogTitleKey).toString()
      await this.syncBusinessesAndToggleLoading()
      this.$refs.removedBusinessSuccessDialog.open()
    } catch (ex) {
      this.showUnknownErrorModal(null)
      // eslint-disable-next-line no-console
      console.log('Error during remove organization affiliations event !')
    }
  }

  removedBusinessSuccessClose () {
    this.$refs.removedBusinessSuccessDialog.close()
  }

  close () {
    this.$refs.errorDialog.close()
  }

  closeLinkExpireErrorDialog () {
    this.$refs.linkExpireErrorDialog.close()
  }

  closeBusinessUnavailableDialog () {
    this.$refs.businessUnavailableDialog.close()
  }
}
</script>

<style lang="scss" scoped>
.v-icon.v-icon {
  color: $app-dk-blue;
}

.loading-container.grayed-out {
  // these are the same styles as dialog overlay:
  opacity: 0.46;
  background-color: rgb(33, 33, 33); // grey darken-4
  border-color: rgb(33, 33, 33); // grey darken-4
}

.v-tooltip__content {
  background-color: RGBA(73, 80, 87, 0.95) !important;
  color: white !important;
  border-radius: 4px;
  font-size: 12px !important;
  line-height: 18px !important;
  padding: 15px !important;
  letter-spacing: 0;
  max-width: 360px !important;
}

.v-tooltip__content:after {
  content: "" !important;
  position: absolute !important;
  top: 50% !important;
  right: 100% !important;
  margin-top: -10px !important;
  border-top: 10px solid transparent !important;
  border-bottom: 10px solid transparent !important;
  border-right: 8px solid RGBA(73, 80, 87, .95) !important;
}

.top-tooltip:after {
  top: 100% !important;
  left: 45% !important;
  margin-top: 0 !important;
  border-right: 10px solid transparent !important;
  border-left: 10px solid transparent !important;
  border-top: 8px solid RGBA(73, 80, 87, 0.95) !important;
}

.right-tooltip:after {
  top: 50% !important;
  right: 100% !important;
  margin-top: -10px !important;
  border-bottom: 10px solid transparent !important;
  border-left: 10px solid transparent !important;
  border-top: 10px solid transparent !important;
  border-right: 8px solid RGBA(73, 80, 87, 0.95) !important;
}

.view-header {
  justify-content: space-between;
  margin-bottom: 0.75rem;

  .subtitle {
    font-size: 1rem;
    color: $gray7;
    font-weight: normal;
  }

  .v-btn {
    font-weight: 700;
  }
}

.help-text {
  max-width: 75%;
  margin: 0 auto;
}

#add-existing-btn {
  box-shadow: none;
  background-color: $app-blue !important;
}

.add-existing-title {
  font-size: .875rem;
}

.add-existing-item {
  height: 40px !important;
  font-size: .875rem;
  color: $gray7;

  &:hover {
    background-color: $app-background-blue;
  }
}

// Vuetify Overrides
::v-deep {

  .v-data-table td {
    padding-top: 1rem;
    padding-bottom: 1rem;
    height: auto;
    vertical-align: top;
  }

  .v-list-item__title {
    display: block;
    font-weight: 700;
  }

  .theme--light.v-list-item:not(.v-list-item--active):not(.v-list-item--disabled):hover {
    color: $app-blue !important;
  }

  .v-list .v-list-item--active, .v-list .v-list-item--active {
    &:hover {
      background-color: $app-background-blue;
    }
  }

  .v-list-item {
    min-height: 0 !important;
    height: 32px;
  }

  .theme--light.v-list-item--active:before, .theme--light.v-list-item--active:hover:before,
  .theme--light.v-list-item:focus:before {
    opacity: 0 !important;
  }

  .v-list-item__action {
    margin-right: 20px !important;
  }

  .v-list-item .v-list-item__subtitle, .v-list-item .v-list-item__title {
    color: $gray7;
    &:hover {
      color: $app-blue !important;
    }
  }
}
</style>
