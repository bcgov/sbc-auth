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
            <business-lookup
              @business="businessName = $event.name; businessIdentifier = $event.identifier; manageBusinessDialog.show=true;"
            />
          </template>
        </v-form>
        <v-form v-else ref="addNameRequestForm" lazy-validation class="mt-6">
          <template>
            <div>
              Add Name search field
            </div>
            <!-- TODO 16720: Search for name request to trigger showAddNRModal -->
            <!-- <name-request-lookup
              @business="requestNames = $event.name; businessIdentifier = $event.identifier"
              @name-request-selected="showAddNRModal()"
            /> -->
          </template>
        </v-form>
      </v-col>
    </v-row>
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
import ModalDialog from '@/components/auth/common/ModalDialog.vue'
import { mapActions } from 'vuex'

@Component({
  components: {
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
  manageBusinessDialog = { show: false }
  searchType = 'Incorporated'
  businessName = ''
  businessIdentifier = '' // aka incorporation number or registration number
  clearSearch = 0
  manageNameRequestDialog = { show: false }
  requestNames = [] // names in a name request

  $refs: {
    addNRDialog: ModalDialog
  }

  showAddSuccessModal () {
    this.clearSearch++
    this.$emit('add-success')
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
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
::v-deep {
  .v-radio .v-icon {
    color: var(--v-primary-base);
  }
}

</style>
