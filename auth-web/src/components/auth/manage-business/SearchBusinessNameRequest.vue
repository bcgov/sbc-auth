<template>
  <div>
    <v-row class="mx-0 mt-n4">Find an existing incorporated or registered business or Name Request to manage it:</v-row>
    <v-row class="mx-0 mt-n2">
      <v-radio-group v-model="searchType" row>
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
    <v-row class="mx-n4 mt-n12" :key="clearSearch">
      <v-col cols="6">
        <v-form v-if="searchType=='Incorporated'" ref="addBusinessForm" lazy-validation class="mt-6">
          <template>
            <!-- Search for business identifier or name -->
            <!-- NB: use v-if to re-mount component between instances -->
            <BusinessLookup
              @business="businessEvent"
              :key="businessLookupKey"
            />
          </template>
        </v-form>
        <v-form v-else ref="addNameRequestForm" lazy-validation class="mt-6">
          <template>
            <v-btn
              large
              color="primary"
              class="save-continue-button"
              @click="businessIdentifier = 'NR1234567'; showAddNRModal()"
              data-test="next-button"
            > Open Name Request
            </v-btn>
            <!-- TODO 16720: Search for name request to trigger showAddNRModal -->
            <!-- <name-request-lookup
              @business="requestNames = $event.name; businessIdentifier = $event.identifier"
              @name-request-selected="showAddNRModal()"
            /> -->
          </template>
        </v-form>
      </v-col>
    </v-row>

    <template v-if="isEnableBusinessNrSearch">
      <ManageBusinessDialog
        ref="manageBusinessDialog"
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
      />
    </template>
    <!-- Add Business Dialog -->
    <ModalDialog
      ref="addNRDialog"
      :is-persistent="true"
      title="Manage a Name Request"
      :show-icon="false"
      :show-actions="false"
      max-width="640"
      data-test-tag="add-name-request"
    >
      <template v-slot:text>
        <AddNameRequestForm
          class="mt-6"
          :businessIdentifier="businessIdentifier"
          :requestNames="requestNames"
          @close-add-nr-modal="cancelAddNameRequest()"
          @add-success="showAddSuccessModalNR"
          @add-failed-show-msg="showNRErrorModal()"
          @add-failed-no-nr="showNRNotFoundModal()"
          @add-unknown-error="showUnknownErrorModal('nr')"
        />
      </template>
    </ModalDialog>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import AddNameRequestForm from '@/components/auth/manage-business/AddNameRequestForm.vue'
import BusinessLookup from './BusinessLookup.vue'
import Certify from './Certify.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { LDFlags } from '@/util/constants'
import LaunchDarklyService from 'sbc-common-components/src/services/launchdarkly.services'
import { LoginPayload } from '@/models/business'
import ManageBusinessDialog from '@/components/auth/manage-business/ManageBusinessDialog.vue'
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { mapActions } from 'vuex'

@Component({
  components: {
    ManageBusinessDialog,
    AddNameRequestForm,
    BusinessLookup,
    Certify,
    HelpDialog,
    ModalDialog
  },
  methods: {
    ...mapActions('business', [
      'addBusiness',
      'updateBusinessName',
      'updateFolioNumber'
    ])
  }
})
export default class SearchBusinessNameRequest extends Vue {
  @Prop({ default: false }) readonly isGovStaffAccount: boolean
  @Prop({ default: '' }) readonly userFirstName: string
  @Prop({ default: '' }) readonly userLastName: string

  // local variables
  searchType = 'Incorporated'
  businessName = ''
  businessIdentifier = '' // aka incorporation number or registration number
  businessLegalType = ''
  clearSearch = 0
  requestNames = [{ 'name': 'Hello', 'state': 'REJECTED' }, { 'name': 'Hello2', 'state': 'APPROVED' }] // names in a name request
  showManageBusinessDialog = false
  businessLookupKey = 0 // force re-mount of BusinessLookup component

  $refs: {
    addNRDialog: InstanceType<typeof ModalDialog>
    manageBusinessDialog: InstanceType<typeof ManageBusinessDialog>
  }
  addBusinessToList = async (loginPayload: LoginPayload) => {
    return this.$store.dispatch('business/addBusiness', loginPayload)
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
  showAddSuccessModalNR () {
    this.$refs.addNRDialog.close()
    this.$emit('add-success-nr')
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

  async businessEvent (event: { name: string, identifier: string, legalType: string }) {
    this.businessName = event?.name || ''
    this.businessIdentifier = event?.identifier || ''
    this.businessLegalType = event?.legalType || ''
    if (this.isGovStaffAccount) {
      try {
        let businessData: LoginPayload = { businessIdentifier: this.businessIdentifier }
        await this.addBusinessToList(businessData)
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
  cancelEvent () {
    this.showManageBusinessDialog = false
    this.businessIdentifier = ''
    this.businessLegalType = ''
    this.businessName = ''
    // Force a re-render for our BusinessLookup component - to reset it's state.
    this.businessLookupKey++
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
