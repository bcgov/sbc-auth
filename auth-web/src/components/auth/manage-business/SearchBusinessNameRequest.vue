<template>
  <div>
    <v-row class="mx-0 mt-n4">
      Find an existing incorporated or registered business or Name Request to manage it:
    </v-row>
    <v-row class="mx-0 mt-n2">
      <v-radio-group
        v-model="searchType"
        row
      >
        <v-radio
          label="Incorporated or Registered business"
          value="Incorporated"
        />
        <v-radio
          label="Name Request"
          value="NameRequest"
        />
      </v-radio-group>
    </v-row>
    <v-row
      :key="clearSearch"
      class="mx-n4 mt-n12"
    >
      <v-col cols="6">
        <v-form
          v-if="searchType=='Incorporated'"
          ref="addBusinessForm"
          lazy-validation
          class="mt-6"
        >
          <!-- Search for business identifier or name -->
          <!-- NB: use v-if to re-mount component between instances -->
          <BusinessLookup
            :key="businessLookupKey"
            :lookupType="lookupType.BUSINESS"
            @business="businessEvent"
          />
        </v-form>
        <v-form
          v-else
          ref="addNameRequestForm"
          lazy-validation
          class="mt-6"
        >
          <BusinessLookup
            :key="businessLookupKey"
            :lookupType="lookupType.NR"
            @nameRequest="nameRequestEvent"
          />
        </v-form>
      </v-col>
    </v-row>

    <template v-if="isEnableBusinessNrSearch">
      <ManageBusinessDialog
        ref="manageBusinessDialog"
        :orgId="orgId"
        :businessLegalType="businessLegalType"
        :showBusinessDialog="showManageBusinessDialog"
        :initialBusinessIdentifier="businessIdentifier"
        :initialBusinessName="businessName"
        :isStaffOrSbcStaff="isGovStaffAccount"
        :userFirstName="userFirstName"
        :userLastName="userLastName"
        @add-success="showAddSuccessModal"
        @add-failed-invalid-code="showInvalidCodeModal($event)"
        @add-failed-no-entity="showEntityNotFoundModal()"
        @add-failed-passcode-claimed="showPasscodeClaimedModal()"
        @add-unknown-error="showUnknownErrorModal('business')"
        @on-cancel="cancelEvent"
        @on-business-identifier="businessIdentifier = $event"
        @on-authorization-email-sent-close="onAuthorizationEmailSentClose($event)"
      />
    </template>
    <!-- Add Name Request Dialog -->
    <template v-if="isEnableBusinessNrSearch">
      <ModalDialog
        ref="addNRDialog"
        :showNRDialog="showNRDialog"
        :is-persistent="true"
        title="Manage a Name Request"
        :show-icon="false"
        :show-actions="false"
        max-width="640"
        data-test-tag="add-name-request"
      >
        <template #text>
          <AddNameRequestForm
            :businessIdentifier="businessIdentifier"
            :requestNames="nrNames"
            @close-add-nr-modal="cancelAddNameRequest()"
            @add-success-nr="showAddSuccessModalNR"
            @add-failed-show-msg="showNRErrorModal()"
            @add-failed-no-nr="showNRNotFoundModal()"
            @add-unknown-error="showUnknownErrorModal('nr')"
          />
        </template>
      </ModalDialog>
    </template>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import AddNameRequestForm from '@/components/auth/manage-business/AddNameRequestForm.vue'
import BusinessLookup from './BusinessLookup.vue'
import { CreateNRAffiliationRequestBody } from '@/models/affiliation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { LoginPayload } from '@/models/business'
import { LookupType } from '@/models/business-nr-lookup'
import ManageBusinessDialog from '@/components/auth/manage-business/manage-business-dialog/ManageBusinessDialog.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { mapActions } from 'pinia'
import { useBusinessStore } from '@/stores'

@Component({
  components: {
    ManageBusinessDialog,
    AddNameRequestForm,
    BusinessLookup,
    HelpDialog,
    ModalDialog
  },
  methods: {
    ...mapActions(useBusinessStore, [
      'updateBusinessName',
      'updateFolioNumber'
    ])
  }
})
export default class SearchBusinessNameRequest extends Vue {
  @Prop({ default: '' }) readonly orgId: string
  @Prop({ default: false }) readonly isGovStaffAccount: boolean
  @Prop({ default: '' }) readonly userFirstName: string
  @Prop({ default: '' }) readonly userLastName: string

  // local variables
  searchType = 'Incorporated'
  businessName = ''
  nrNames = []
  businessIdentifier = '' // aka incorporation number or registration number
  businessLegalType = ''
  clearSearch = 0
  showManageBusinessDialog = false
  showNRDialog = false
  businessLookupKey = 0 // force re-mount of BusinessLookup component
  lookupType = LookupType
  businessStore = useBusinessStore()

  $refs: {
    addNRDialog: InstanceType<typeof ModalDialog>
    manageBusinessDialog: InstanceType<typeof ManageBusinessDialog>
  }

  showAddSuccessModal (event) {
    this.clearSearch++
    this.showManageBusinessDialog = false
    this.$emit('add-success', event)
  }
  showInvalidCodeModal (event) {
    this.$emit('add-failed-invalid-code', event)
  }
  showEntityNotFoundModal () {
    this.$emit('add-failed-no-entity')
  }
  showPasscodeClaimedModal () {
    this.$emit('add-failed-passcode-claimed')
  }
  showUnknownErrorModal (event) {
    this.$emit('add-unknown-error', event)
  }
  showBusinessAlreadyAdded (event) {
    this.$emit('business-already-added', event)
  }
  cancelAddBusiness () {
    this.$emit('on-cancel')
  }
  cancelAddNameRequest () {
    this.$refs.addNRDialog.close()
    this.$emit('on-cancel-nr')
  }
  showAddSuccessModalNR (event) {
    this.clearSearch++
    this.$refs.addNRDialog.close()
    this.$emit('add-success-nr', event)
  }
  showNRErrorModal () {
    this.$refs.addNRDialog.close()
    this.$emit('add-nr-error')
  }
  showNRNotFoundModal () {
    this.$refs.addNRDialog.close()
    this.$emit('add-failed-no-nr')
  }
  showAddNRModal () {
    this.$refs.addNRDialog.open()
  }
  emitOnAuthorizationEmailSentClose (event) {
    this.$emit('on-authorization-email-sent-close', event)
  }

  async businessEvent (event: { name: string, identifier: string, legalType: string }) {
    this.businessName = event?.name || ''
    this.businessIdentifier = event?.identifier || ''
    this.businessLegalType = event?.legalType || ''
    if (this.isGovStaffAccount) {
      try {
        let businessData: LoginPayload = { businessIdentifier: this.businessIdentifier }
        await this.businessStore.addBusiness(businessData)
        this.$emit('add-success', this.businessIdentifier)
        this.$refs.manageBusinessDialog.resetForm(true)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error('Error adding business: ', err)
      }
    } else {
      this.showManageBusinessDialog = true
    }
  }

  async nameRequestEvent (event: { names: string[], nrNum: string }) {
    this.nrNames = event?.names || []
    this.businessIdentifier = event?.nrNum || ''
    if (this.isGovStaffAccount) {
      await this.addNameRequestForStaffSilently()
    } else {
      this.showNRDialog = true
      this.showAddNRModal()
    }
  }

  private async addNameRequestForStaffSilently () {
    try {
      const requestBody: CreateNRAffiliationRequestBody = {
        businessIdentifier: this.businessIdentifier
      }
      const nrResponse = await this.businessStore.addNameRequest(requestBody)
      if (nrResponse?.status === 201) {
        // emit event to let parent know business added
        this.$emit('add-success-nr', this.businessIdentifier)
        this.$refs.manageBusinessDialog.resetForm(true)
      } else {
        this.$emit('add-unknown-error', 'nr')
      }
    } catch (err) {
      this.$emit('add-unknown-error', 'nr')
      // eslint-disable-next-line no-console
      console.error('Error adding name request: ', err)
    }
  }

  cancelEvent () {
    this.showManageBusinessDialog = false
    this.showNRDialog = false
    this.businessIdentifier = ''
    this.businessLegalType = ''
    this.businessName = ''
    // Force a re-render for our BusinessLookup component - to reset it's state.
    this.businessLookupKey++
  }

  onAuthorizationEmailSentClose (event) {
    this.showManageBusinessDialog = false
    this.showNRDialog = false
    this.businessIdentifier = ''
    this.businessLegalType = ''
    this.businessName = ''
    this.businessLookupKey++
    this.emitOnAuthorizationEmailSentClose(event)
  }

  get isEnableBusinessNrSearch (): boolean {
    return LaunchDarklyService.getFlag(LDFlags.EnableBusinessNrSearch) || false
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
::v-deep {
  .v-radio .v-icon {
    color: var(--v-primary-base);
  }
  // Radio button color, set it to blue
  .v-input--selection-controls__input:hover, .v-input--selection-controls__input:focus  {
    color: var(--v-primary-base) !important;
  }
}

</style>
