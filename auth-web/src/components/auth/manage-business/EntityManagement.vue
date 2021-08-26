<template>
  <div>
    <div>
      <v-fade-transition>
        <div class="loading-container" v-if="isLoading">
          <v-progress-circular size="50" width="5" color="primary" :indeterminate="isLoading"/>
        </div>
      </v-fade-transition>
    </div>
    <v-container class="view-container">
      <div class="view-header align-center">
        <h1 class="view-header__title">My Business Registry<br>
          <span class="subtitle">Start BC-based businesses and keep business records up to date.</span>
        </h1>
        <div class="view-header__actions">
          <v-btn
            id="add-name-request-btn"
            class="font-weight-regular"
            color="primary"
            outlined dark large
            @click="goToNameRequest()"
          >
            <span>Request a BC Business Name</span>
            <v-icon small class="ml-2">mdi-open-in-new</v-icon>
          </v-btn>
          <template v-if="!enableBusinessTable">
            <v-menu>
              <template v-slot:activator="{ on }">
                <v-btn
                    class="ml-3"
                    color="primary"
                    dark
                    large
                    v-on="on"
                >
                  <v-icon small>mdi-plus</v-icon>
                  <span>{{ $t('addExistingBtnLabel') }}</span>
                </v-btn>
              </template>
              <v-list>
                <v-list-item
                >
                  <v-list-item-title class="d-inline-flex">
                    <v-icon small>mdi-plus</v-icon>
                    <div class="ml-1">{{ $t('addExistingBtnLabel') }}</div>
                  </v-list-item-title>
                </v-list-item>
                <v-list-item
                    @click="showAddNRModal()"
                >
                  Name Request
                </v-list-item>
                <v-list-item
                    @click="showAddBusinessModal()"
                >
                  Business
                </v-list-item>
              </v-list>
            </v-menu>
          </template>
        </div>
      </div>

      <!-- Feature flagged future Dashboard table -->
      <template v-if="enableBusinessTable">
        <v-row no-gutters id="dashboard-actions" class="mb-n3 pl-4">
          <v-col cols="9">
            <!-- Add Existing Name Request or Business -->
            <v-menu>
              <template v-slot:activator="{ on }">
                <v-btn
                  class="mt-2"
                  color="primary"
                  dark
                  large
                  v-on="on"
                >
                  <v-icon small>mdi-plus</v-icon>
                  <span>Add an Existing Business or Name Request</span>
                </v-btn>
              </template>
              <v-list>
                <v-list-item>
                  <v-list-item-title class="d-inline-flex">
                    <v-icon>mdi-plus</v-icon>
                    <div class="ml-1 mt-1">Add an Existing...</div>
                  </v-list-item-title>
                </v-list-item>
                <v-list-item class="mt-4" @click="showAddBusinessModal()">Business</v-list-item>
                <v-list-item class="my-2" @click="showAddNRModal()">Name Request</v-list-item>
              </v-list>
            </v-menu>
          </v-col>
          <v-col class="mr-4">
            <v-select
              dense filled multiple
              class="column-selector"
              label="Columns to Show"
              v-model="selectedColumns"
              :items="columns"
              :menu-props="{ bottom: true, offsetY: true }"
            >
              <template v-slot:selection="{ item }"></template>
            </v-select>
          </v-col>
        </v-row>

        <AffiliatedEntityTable
          :selected-columns="selectedColumns"
          @remove-business="showConfirmationOptionsModal($event)"
        />
      </template>

      <template v-else>
        <AffiliatedEntityList
          @add-business="showAddBusinessModal()"
          @remove-business="showConfirmationOptionsModal($event)"
          @add-failed-show-msg="showNRErrorModal"
        />
      </template>

      <PasscodeResetOptionsModal
        ref="passcodeResetOptionsModal"
        data-test="dialog-passcode-reset-options"
        @confirm-passcode-reset-options="remove($event)"
      />

      <!-- Add Business Dialog -->
      <ModalDialog
        ref="addBusinessDialog"
        :is-persistent="true"
        :title="dialogTitle"
        :show-icon="false"
        :show-actions="false"
        max-width="640"
        data-test-tag="add-business"
      >
        <template v-slot:text>
          <p>
            Add an existing business by entering the Incorporation Number <span class="wb">and associated
            {{CommonUtils.isCooperativeNumber(businessIdentifier) ? 'Passcode' : 'Password'}}.</span>
          </p>
          <AddBusinessForm
            class="mt-9"
            @add-success="showAddSuccessModal()"
            @add-failed-invalid-code="showInvalidCodeModal()"
            @add-failed-no-entity="showEntityNotFoundModal()"
            @add-failed-passcode-claimed="showPasscodeClaimedModal()"
            @add-unknown-error="showUnknownErrorModal('business')"
            @on-cancel="cancelAddBusiness()"
            @on-business-identifier="businessIdentifier = $event"
          />
        </template>
      </ModalDialog>

      <!-- Add Name Request Dialog -->
      <ModalDialog
        ref="addNRDialog"
        :is-persistent="true"
        :title="dialogTitle"
        :show-icon="false"
        :show-actions="false"
        max-width="640"
        data-test-tag="add-name-request"
      >
        <template v-slot:text>
          <p>
            Enter the Name Request Number (e.g., NR 1234567) and either the applicant phone number
            OR applicant email that were used when the name was requested.
          </p>
          <AddNameRequestForm
            class="mt-9"
            @close-add-nr-modal="cancelAddNameRequest()"
            @add-success="showAddSuccessModalNR()"
            @add-failed-show-msg="showNRErrorModal"
            @add-failed-no-entity="showNRNotFoundModal()"
            @add-unknown-error="showUnknownErrorModal('nr')"
            @on-cancel="cancelAddNameRequest()"
          />
        </template>
      </ModalDialog>

      <!-- Success Dialog -->
      <ModalDialog
        ref="successDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="640"
      />

      <!-- NR/IA removal confirm Dialog/A generic one -->
      <ModalDialog
        ref="removalConfirmDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="640"
        data-test="remove-confirm-dialog"
      >
        <template v-slot:icon>
          <v-icon large color="error">mdi-alert-circle-outline</v-icon>
        </template>
        <template v-slot:actions>
          <v-btn large color="primary" @click="primaryBtnHandler()" data-test="dialog-ok-button">{{primaryBtnText}}</v-btn>
          <v-btn large @click="secondaryBtnHandler()" data-test="dialog-ok-button">{{ secondaryBtnText }}</v-btn>
        </template>
      </ModalDialog>

      <!-- Error Dialog -->
      <ModalDialog
        ref="errorDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="640"
      >
        <template v-slot:icon>
          <v-icon large color="error">mdi-alert-circle-outline</v-icon>
        </template>
        <template v-slot:actions>
          <v-btn large color="error" @click="close()" data-test="dialog-ok-button">OK</v-btn>
        </template>
      </ModalDialog>

      <!-- Dialog for confirming business removal -->
      <ModalDialog
        ref="removedBusinessSuccessDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="640"
        :isPersistent="true"
      >
        <template v-slot:icon>
          <v-icon large color="primary">mdi-check</v-icon>
        </template>
        <template v-slot:actions>
          <v-btn large color="primary" @click="removedBusinessSuccessClose()" data-test="removed-business-success-button">OK</v-btn>
        </template>
      </ModalDialog>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop } from 'vue-property-decorator'
import { CorpType, LDFlags, LoginSource, Pages } from '@/util/constants'
import { MembershipStatus, RemoveBusinessPayload } from '@/models/Organization'
import { mapActions, mapGetters, mapState } from 'vuex'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { AccountSettings } from '@/models/account-settings'
import AddBusinessForm from '@/components/auth/manage-business/AddBusinessForm.vue'
import AddNameRequestForm from '@/components/auth/manage-business/AddNameRequestForm.vue'
import { Address } from '@/models/address'
import AffiliatedEntityList from '@/components/auth/manage-business/AffiliatedEntityList.vue'
import AffiliatedEntityTable from '@/components/auth/manage-business/AffiliatedEntityTable.vue'
import { Business } from '@/models/business'
import CommonUtils from '@/util/common-util'
import ConfigHelper from '@/util/config-helper'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import PasscodeResetOptionsModal from '@/components/auth/manage-business/PasscodeResetOptionsModal.vue'

@Component({
  components: {
    AddBusinessForm,
    AddNameRequestForm,
    AffiliatedEntityList,
    AffiliatedEntityTable,
    ModalDialog,
    PasscodeResetOptionsModal
  },
  computed: {
    ...mapState('org', [
      'currentOrgAddress'
    ]),
    ...mapState('user', ['userProfile', 'currentUser']),
    ...mapGetters('org', ['isPremiumAccount'])
  },
  methods: {
    ...mapActions('business', ['syncBusinesses', 'removeBusiness', 'createNumberedBusiness']),
    ...mapActions('org', ['syncAddress'])
  }
})
export default class EntityManagement extends Mixins(AccountChangeMixin, NextPageMixin) {
  readonly CommonUtils = CommonUtils

  @Prop({ default: '' }) private orgId: string;
  private removeBusinessPayload = null
  private dialogTitle = ''
  private dialogText = ''
  private isLoading = true
  private resetPasscodeEmail: string = null
  businessIdentifier: string = null
  private primaryBtnText = ''
  private secondaryBtnText = ''
  private primaryBtnHandler: () => void = undefined
  private secondaryBtnHandler: () => void = undefined

  protected readonly currentAccountSettings!: AccountSettings
  private readonly isPremiumAccount!: boolean
  private readonly syncBusinesses!: () => Promise<Business[]>
  private readonly removeBusiness!: (removeBusinessPayload: RemoveBusinessPayload) => Promise<void>
  private readonly createNumberedBusiness!: (accountId: Number) => Promise<void>
  private readonly currentOrgAddress!: Address
  private readonly syncAddress!: () => Address
  private selectedColumns = ['Number', 'Type', 'Status', 'Last Modified', 'Modified By']
  private columns = ['Number', 'Type', 'Status', 'Last Modified', 'Modified By']

  $refs: {
    successDialog: ModalDialog
    errorDialog: ModalDialog
    addBusinessDialog: ModalDialog
    addNRDialog: ModalDialog
    passcodeResetOptionsModal: PasscodeResetOptionsModal,
    removedBusinessSuccessDialog: ModalDialog,
    removalConfirmDialog: ModalDialog

  }

  private async mounted () {
    // Apply the folio number for premium accounts.
    if (this.isPremiumAccount) this.applyFolio()

    if (this.currentMembership === undefined) {
      this.$router.push(`/${Pages.CREATE_ACCOUNT}`)
      return
    }
    // If pending approval on current account, redirect away
    if (this.currentMembership?.membershipStatus !== MembershipStatus.Active) {
      this.$router.push(this.getNextPageUrl())
      return
    }
    // check if address info is complete
    const isNotAnonUser = this.currentUser?.loginSource !== LoginSource.BCROS
    if (isNotAnonUser && this.enableMandatoryAddress) {
      // do it only if address is not already fetched.Or else try to fetch from DB
      if (!this.currentOrgAddress || Object.keys(this.currentOrgAddress).length === 0) {
        // sync and try again
        await this.syncAddress()
        if (!this.currentOrgAddress || Object.keys(this.currentOrgAddress).length === 0) {
          await this.$router.push(`/${Pages.MAIN}/${this.orgId}/settings/account-info`)
          return
        }
      }
    }

    this.setAccountChangedHandler(this.setup)
    this.setup()
  }

  private async setup () {
    this.isLoading = true
    this.$route.query.isNumberedCompanyRequest && await this.createNumberedBusiness(this.currentAccountSettings.id)
    await this.syncBusinesses()
    this.isLoading = false
  }

  private get enableMandatoryAddress (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableMandatoryAddress) || false
  }

  private get enableBusinessTable (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableBusinessTable) || false // Default to false
  }

  // open Name Request
  private goToNameRequest (): void {
    window.location.href = ConfigHelper.getNameRequestUrl()
  }

  async showAddSuccessModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Business Added'
    this.dialogText = 'You have successfully added a business'
    await this.syncBusinesses()
    this.$refs.successDialog.open()
  }

  async showAddSuccessModalNR () {
    this.$refs.addNRDialog.close()
    this.dialogTitle = 'Name Request Added'
    this.dialogText = 'You have successfully added a name request'
    await this.syncBusinesses()
    this.$refs.successDialog.open()
  }

  showInvalidCodeModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Invalid Passcode'
    this.dialogText = 'Unable to add the business. The provided Passcode is invalid.'
    this.$refs.errorDialog.open()
  }

  showEntityNotFoundModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Business Not Found'
    this.dialogText = 'The specified business was not found.'
    this.$refs.errorDialog.open()
  }

  showNRNotFoundModal () {
    this.$refs.addNRDialog.close()
    this.dialogTitle = 'Name Request Not Found'
    this.dialogText = 'The specified name request was not found.'
    this.$refs.errorDialog.open()
  }

  showNRErrorModal (msg) {
    this.$refs.addNRDialog.close()
    this.dialogTitle = 'Error Adding Name Request'
    this.dialogText = msg
    this.$refs.errorDialog.open()
  }

  showPasscodeClaimedModal () {
    const contactNumber = this.$t('techSupportTollFree').toString()
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Passcode Already Claimed'
    this.dialogText = `This passcode has already been claimed. If you have questions, please call ${contactNumber}`
    this.$refs.errorDialog.open()
  }

  showUnknownErrorModal (type: string) {
    if (type === 'business') {
      this.$refs.addBusinessDialog.close()
      this.dialogTitle = 'Error Adding Existing Business'
      this.dialogText = 'An error occurred adding your business. Please try again.'
    } else if (type === 'nr') {
      this.$refs.addNRDialog.close()
      this.dialogTitle = 'Error Adding Existing Name Request'
      this.dialogText = 'An error occurred adding your name request. Please try again.'
    }
    this.$refs.errorDialog.open()
  }

  showAddBusinessModal () {
    this.dialogTitle = 'Add an Existing Business'
    this.$refs.addBusinessDialog.open()
  }

  showAddNRModal () {
    this.dialogTitle = 'Add an Existing Name Request'
    this.$refs.addNRDialog.open()
  }

  showConfirmationOptionsModal (removeBusinessPayload: RemoveBusinessPayload) {
    this.removeBusinessPayload = removeBusinessPayload
    if (removeBusinessPayload.business.corpType.code === CorpType.NAME_REQUEST) {
      this.populateNRmodalValues()
      this.$refs.removalConfirmDialog.open()
    } else if (removeBusinessPayload.business.corpType.code === CorpType.NEW_BUSINESS) {
      this.populateIAmodalValues()
      this.$refs.removalConfirmDialog.open()
    } else {
      this.$refs.passcodeResetOptionsModal.open()
    }
  }

  private populateNRmodalValues () {
    this.dialogTitle = this.$t('removeNRConfirmTitle').toString()
    this.dialogText = this.$t('removeNRConfirmText').toString()
    this.primaryBtnText = 'Remove Name Request'
    this.secondaryBtnText = 'Keep Name Request'
    this.primaryBtnHandler = this.confirmRemovalNr
    this.secondaryBtnHandler = this.cancelRemoval
  }

  private populateIAmodalValues () {
    this.dialogTitle = this.$t('removeIAConfirmTitle').toString()
    this.dialogText = this.$t('removeIAConfirmText').toString()
    this.primaryBtnText = 'Delete Incorporation Application'
    this.secondaryBtnText = 'Keep Incorporation Application'
    this.primaryBtnHandler = this.confirmRemovalIA
    this.secondaryBtnHandler = this.cancelRemoval
  }

  cancelRemoval () {
    this.$refs.removalConfirmDialog.close()
  }

  confirmRemovalIA () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeIASuccessTitle', 'removeIASuccessText')
  }

  confirmRemovalNr () {
    this.$refs.removalConfirmDialog.close()
    this.remove('', false, 'removeNRSuccessTitle', 'removeNRSuccessText')
  }

  cancelAddBusiness () {
    this.$refs.addBusinessDialog.close()
  }

  cancelAddNameRequest () {
    this.$refs.addNRDialog.close()
  }

  async remove (resetPasscodeEmail: string, resetPasscode = true, dialogTitleKey = 'removeBusiness', dialogTextKey = 'removedBusinessSuccessText') {
    try {
      this.removeBusinessPayload.passcodeResetEmail = resetPasscodeEmail
      this.removeBusinessPayload.resetPasscode = resetPasscode
      this.$refs.passcodeResetOptionsModal.close()
      await this.removeBusiness(this.removeBusinessPayload)
      this.dialogText = this.$t(dialogTextKey).toString()
      this.dialogTitle = this.$t(dialogTitleKey).toString()
      await this.syncBusinesses()
      this.$refs.removedBusinessSuccessDialog.open()
    } catch (ex) {
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

  private applyFolio (): void {
    this.selectedColumns.splice(3, 0, 'Folio')
    this.columns.splice(3, 0, 'Folio')
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  .view-header {
    justify-content: space-between;

    h1 {
      margin-bottom: -10px;
    }

    .subtitle {
      font-size: 1rem;
      color: $gray7;
      font-weight: normal;
    }

    .v-btn {
      font-weight: 700;
    }
  }

  .column-selector {
    float: right;
    width: 200px
  }

  // Vuetify Overrides
  ::v-deep {

    #dashboard-actions {
      .v-input .v-label {
        top: 30px;
        color: $gray7;
      }
    }

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

    .v-list-item {
      min-height: 0 !important;
      height: 32px !important;
    }

    .theme--light.v-list-item--active:before, .theme--light.v-list-item--active:hover:before,
    .theme--light.v-list-item:focus:before {
      opacity: 0 !important;
    }

    .theme--light.v-text-field--filled>.v-input__control>.v-input__slot {
      background-color: white;
    }

    .v-list-item__action {
      margin-right: 20px !important;
    }
    .v-list-item .v-list-item__subtitle, .v-list-item .v-list-item__title {
      color: $gray7;
    }
  }
</style>
