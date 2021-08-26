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
        <h1 class="view-header__title">Manage Businesses</h1>
        <div class="view-header__actions">
          <v-btn
              id="add-name-request-btn"
              class="mr-3 font-weight-regular"
              color="primary"
              outlined dark large
              @click="goToNameRequest()"
          >
            <span>Request a BC Business Name</span>
            <v-icon small class="ml-2">mdi-open-in-new</v-icon>
          </v-btn>
          <v-menu>
            <template v-slot:activator="{ on }">
              <v-btn
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
        </div>
      </div>

      <!-- Feature flagged future Dashboard table -->
      <template v-if="enableBusinessTable">
        <v-row no-gutters>
          <v-col cols="9"></v-col>
          <v-col class="mr-4">
            <v-select
                v-model="selectedColumns"
                :items="columns"
                label="Columns to Show"
                class="column-selector"
                filled
                multiple
            >
              <template v-slot:selection="{ item, index }">
                <v-chip v-if="index === 0" class="mt-2">
                  <span>{{ item }}</span>
                </v-chip>
                <span v-if="index === 1" class="grey--text text-caption">
                (+{{ selectedColumns.length - 1 }} others)
              </span>
              </template>
            </v-select>
          </v-col>
        </v-row>

        <AffiliatedEntityTable
            :selected-columns="selectedColumns"
            @remove-business="showPasscodeResetOptionsModal($event)"
        />
      </template>

      <template v-else>
        <AffiliatedEntityList
            @add-business="showAddBusinessModal()"
            @remove-business="showPasscodeResetOptionsModal($event)"
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
      title="Remove Business"
      :text="$t('removedBusinessSuccessText')"
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
import { LDFlags, LoginSource, Pages } from '@/util/constants'
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
import i18n from '@/plugins/i18n'

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
  private messageTextList = i18n.messages[i18n.locale]
  private isLoading = true
  private resetPasscodeEmail: string = null
  businessIdentifier: string = null

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
    removedBusinessSuccessDialog: ModalDialog
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
    // disabling table manually for early stages of development.
    return false // LaunchDarklyService.getFlag(LDFlags.EnableBusinessTable) || false
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
    const contactNumber = (this.messageTextList && this.messageTextList.techSupportTollFree) ? this.messageTextList.techSupportTollFree : 'helpdesk'
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

  showPasscodeResetOptionsModal (removeBusinessPayload: RemoveBusinessPayload) {
    this.removeBusinessPayload = removeBusinessPayload
    this.$refs.passcodeResetOptionsModal.open()
  }

  cancelAddBusiness () {
    this.$refs.addBusinessDialog.close()
  }

  cancelAddNameRequest () {
    this.$refs.addNRDialog.close()
  }

  async remove (resetPasscodeEmail: string) {
    try {
      this.removeBusinessPayload.passcodeResetEmail = resetPasscodeEmail
      this.removeBusinessPayload.resetPasscode = true
      this.$refs.passcodeResetOptionsModal.close()
      await this.removeBusiness(this.removeBusinessPayload)
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
      margin-bottom: 0;
    }

    .v-btn {
      font-weight: 700;
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
