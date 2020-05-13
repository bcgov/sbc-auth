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
          <v-btn large color="primary" @click="showAddBusinessModal()" data-test="add-business-button">
            <v-icon small>mdi-plus</v-icon>
            <span>Add Existing Business</span>
          </v-btn>
        </div>
      </div>

      <AffiliatedEntityList
        @add-business="showAddBusinessModal()"
        @remove-business="showConfirmRemoveModal($event)"
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
          <p>Add an existing business by entering the Incorporation Number <span class="wb">and associated Passcode.</span></p>
          <AddBusinessForm
            class="mt-9"
            @close-add-business-modal="closeAddBusinessModal()"
            @add-success="showAddSuccessModal()"
            @add-failed-invalid-code="showInvalidCodeModal()"
            @add-failed-no-entity="showEntityNotFoundModal()"
            @add-failed-passcode-claimed="showPasscodeClaimedModal()"
            @add-unknown-error="showUnknownErrorModal()"
            @cancel="cancelAddBusiness()"
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
        ref="confirmDeleteDialog"
        :title="dialogTitle"
        :text="dialogText"
        dialog-class="notify-dialog"
        max-width="640"
      >
        <template v-slot:icon>
          <v-icon large color="error">mdi-alert-circle-outline</v-icon>
        </template>
        <template v-slot:actions>
          <v-btn large color="primary" @click="remove()" data-test="dialog-remove-button">Remove</v-btn>
          <v-btn large color="default" @click="cancelConfirmDelete()" data-test="dialog-cancel-button">Cancel</v-btn>
        </template>
      </ModalDialog>
    </v-container>
  </div>
</template>

<script lang="ts">
import { Component, Mixins, Prop, Vue, Watch } from 'vue-property-decorator'
import { MembershipStatus, Organization, RemoveBusinessPayload } from '@/models/Organization'
import { Pages, SessionStorageKeys } from '@/util/constants'
import AccountChangeMixin from '@/components/auth/mixins/AccountChangeMixin.vue'
import { AccountSettings } from '@/models/account-settings'
import AddBusinessForm from '@/components/auth/AddBusinessForm.vue'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'
import { Business } from '@/models/business'
import BusinessModule from '@/store/modules/business'
import ConfigHelper from '@/util/config-helper'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import NextPageMixin from '@/components/auth/mixins/NextPageMixin.vue'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'
import i18n from '@/plugins/i18n'
import { mapActions } from 'vuex'

@Component({
  components: {
    AddBusinessForm,
    AffiliatedEntityList,
    ModalDialog
  },
  methods: {
    ...mapActions('business', ['syncBusinesses', 'removeBusiness', 'createNumberedBusiness'])
  }
})
export default class EntityManagement extends Mixins(AccountChangeMixin, NextPageMixin) {
  @Prop({ default: '' }) private orgId: string;
  private removeBusinessPayload = null
  private dialogTitle = ''
  private dialogText = ''
  private messageTextList = i18n.messages[i18n.locale]
  private isLoading = true

  protected readonly currentAccountSettings!: AccountSettings
  private readonly syncBusinesses!: () => Promise<Business[]>
  private readonly removeBusiness!: (removeBusinessPayload: RemoveBusinessPayload) => Promise<void>
  private readonly createNumberedBusiness!: (accountId: Number) => Number

  $refs: {
    successDialog: ModalDialog
    errorDialog: ModalDialog
    confirmDeleteDialog: ModalDialog
    addBusinessDialog: ModalDialog
  }

  private async mounted () {
    // If pending approval on current account, redirect away
    if (this.currentMembership?.membershipStatus !== MembershipStatus.Active) {
      this.$router.push(this.getNextPageUrl())
    } else {
      this.setAccountChangedHandler(this.setup)
      this.setup()
    }
  }

  private async setup () {
    this.isLoading = true
    this.$route.query.isNcRequest && await this.createNumberedBusiness(this.currentAccountSettings.id)
    await this.syncBusinesses()
    this.isLoading = false
  }

  async showAddSuccessModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Business Added'
    this.dialogText = 'You have successfully added a business'
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

  showPasscodeClaimedModal () {
    const contactNumber = (this.messageTextList && this.messageTextList.techSupportTollFree) ? this.messageTextList.techSupportTollFree : 'helpdesk'
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Passcode Already Claimed'
    this.dialogText = `This passcode has already been claimed. If you have questions, please call ${contactNumber}`
    this.$refs.errorDialog.open()
  }

  showUnknownErrorModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Error Adding Existing Business'
    this.dialogText = 'An error occurred adding your business. Please try again.'
    this.$refs.errorDialog.open()
  }

  showAddBusinessModal () {
    this.dialogTitle = 'Add Existing Business'
    this.$refs.addBusinessDialog.open()
  }

  showConfirmRemoveModal (removeBusinessPayload: RemoveBusinessPayload) {
    this.removeBusinessPayload = removeBusinessPayload
    this.dialogTitle = 'Confirm Remove Business'
    this.dialogText = 'Are you sure you wish to remove this business?'
    this.$refs.confirmDeleteDialog.open()
  }

  cancelConfirmDelete () {
    this.$refs.confirmDeleteDialog.close()
  }

  cancelAddBusiness () {
    this.$refs.addBusinessDialog.close()
  }

  async remove () {
    this.$refs.confirmDeleteDialog.close()
    await this.removeBusiness(this.removeBusinessPayload)
    await this.syncBusinesses()
  }

  close () {
    this.$refs.errorDialog.close()
  }

  private closeAddBusinessModal () {
    this.$refs.addBusinessDialog.close()
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
  }

</style>
