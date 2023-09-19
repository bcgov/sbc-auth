<template>
  <div>
    <v-row class="mx-0 mt-n4">
      Retrieve an existing business or Name Request to manage:
    </v-row>
    <v-row
      :key="clearSearch"
      class="mx-n4 mt-n6"
    >
      <v-col cols="6">
        <v-form
          v-if="searchType=='Incorporated'"
          ref="addBusinessForm"
          lazy-validation
          class="mt-6"
        >
          <!-- Search for business identifier or name -->
          <BusinessLookup
            :key="businessLookupKey"
            :lookupType="lookupType.BUSINESS"
            @business="selectBusiness"
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
    <v-row class="mx-0 mt-n6">
      <v-radio-group
        v-model="searchType"
        row
      >
        <v-radio
          label="Existing business"
          value="Incorporated"
        />
        <v-radio
          label="Name Request"
          value="NameRequest"
        />
      </v-radio-group>
    </v-row>

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
      @unknown-error="showUnknownErrorModal('business')"
      @hide-manage-business-dialog="cancelEvent"
      @on-business-identifier="businessIdentifier = $event"
      @on-authorization-email-sent-close="onAuthorizationEmailSentClose($event)"
    />
    <!-- Add Name Request Dialog -->
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
          @close-add-nr-modal="cancelEvent"
          @add-success-nr="showAddSuccessModalNR"
          @add-failed-show-msg="showNRErrorModal()"
          @add-failed-no-nr="showNRNotFoundModal()"
          @unknown-error="showUnknownErrorModal('nr')"
        />
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import AddNameRequestForm from '@/components/auth/manage-business/AddNameRequestForm.vue'
import BusinessLookup from './BusinessLookup.vue'
import { CreateNRAffiliationRequestBody } from '@/models/affiliation'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
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
  @Prop({ default: false }) readonly showManageBusinessDialog: boolean

  // local variables
  searchType = 'Incorporated'
  businessName = ''
  nrNames = []
  businessIdentifier = '' // aka incorporation number or registration number
  businessLegalType = ''
  clearSearch = 0
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
    this.$emit('unknown-error', event)
  }
  showBusinessAlreadyAdded (event) {
    this.$emit('business-already-added', event)
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

  async selectBusiness (business: { name: string, identifier: string, legalType: string }) {
    this.businessName = business?.name || ''
    this.businessIdentifier = business?.identifier || ''
    this.businessLegalType = business?.legalType || ''
    if (this.isGovStaffAccount) {
      try {
        let businessData: LoginPayload = { businessIdentifier: this.businessIdentifier }
        await this.businessStore.addBusiness(businessData)
        this.$emit('add-success', this.businessIdentifier)
        this.$refs.manageBusinessDialog.resetForm(true)
      } catch (err) {
        this.$emit('unknown-error', 'business')
        // eslint-disable-next-line no-console
        console.error('Error adding business: ', err)
      }
    } else {
      this.$emit('show-manage-business-dialog', this.businessIdentifier)
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
        this.$emit('unknown-error', 'nr')
      }
    } catch (err) {
      this.$emit('unknown-error', 'nr')
      // eslint-disable-next-line no-console
      console.error('Error adding name request: ', err)
    }
  }

  cancelEvent () {
    this.$refs.addNRDialog.close()
    this.$emit('hide-manage-business-dialog')
    this.showNRDialog = false
    this.businessIdentifier = ''
    this.businessLegalType = ''
    this.businessName = ''
    // Force a re-render for our BusinessLookup component - to reset it's state.
    this.businessLookupKey++
  }

  onAuthorizationEmailSentClose (event) {
    this.$emit('hide-manage-business-dialog')
    this.showNRDialog = false
    this.businessIdentifier = ''
    this.businessLegalType = ''
    this.businessName = ''
    this.businessLookupKey++
    this.emitOnAuthorizationEmailSentClose(event)
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
