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
            <!-- TODO 16720: Name Request search lookup -->
            <div>
              Add Name search field
            </div>
          </template>
        </v-form>
      </v-col>
    </v-row>

  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import BusinessLookup from './BusinessLookup.vue'
import Certify from './Certify.vue'
import HelpDialog from '@/components/auth/common/HelpDialog.vue'
import { mapActions } from 'vuex'

@Component({
  components: {
    BusinessLookup,
    Certify,
    HelpDialog
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
