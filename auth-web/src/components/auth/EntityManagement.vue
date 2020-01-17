<template>
  <v-container class="view-container">
    <div class="view-header align-center">
      <h1 class="view-header__title">Manage Businesses</h1>
      <div class="view-header__actions">
        <v-btn color="primary" @click="showAddBusinessModal()" data-test="add-business-button">
          <v-icon small>mdi-plus</v-icon>
          <span>Add Business</span>
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
      >
      <template v-slot:text>
        <p>Enter your Incorporation Number and Passcode.</p>
        <AddBusinessForm
          class="mt-7"
          @close-add-business-modal="closeAddBusinessModal()"
          @add-success="showAddSuccessModal()"
          @add-failed-invalid-code="showInvalidCodeModal()"
          @add-failed-no-entity="showEntityNotFoundModal()"
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
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Organization, RemoveBusinessPayload } from '@/models/Organization'
import AddBusinessForm from '@/components/auth/AddBusinessForm.vue'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'
import { Business } from '@/models/business'
import BusinessModule from '@/store/modules/business'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import UserModule from '@/store/modules/user'
import { getModule } from 'vuex-module-decorators'
import { mapActions } from 'vuex'

@Component({
  components: {
    AddBusinessForm,
    AffiliatedEntityList,
    ModalDialog
  },
  methods: {
    ...mapActions('business', ['syncBusinesses', 'removeBusiness'])
  }
})
export default class EntityManagement extends Vue {
  private businessStore = getModule(BusinessModule, this.$store)
  private removeBusinessPayload = null
  private dialogTitle = ''
  private dialogText = ''

  private readonly syncBusinesses!: (organization?: Organization) => Promise<Business[]>
  private readonly removeBusiness!: (removeBusinessPayload: RemoveBusinessPayload) => Promise<void>

  $refs: {
    successDialog: ModalDialog
    errorDialog: ModalDialog
    confirmDeleteDialog: ModalDialog
    addBusinessDialog: ModalDialog
  }

  async mounted () {
    await this.syncBusinesses()
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
    this.dialogText = 'Unable to add the business. The provided Passcode is invalid or already in use.'
    this.$refs.errorDialog.open()
  }

  showEntityNotFoundModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Business Not Found'
    this.dialogText = 'The specified business was not found.'
    this.$refs.errorDialog.open()
  }

  showUnknownErrorModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Error Adding Business'
    this.dialogText = 'An error occurred adding your business. Please try again.'
    this.$refs.errorDialog.open()
  }

  showAddBusinessModal () {
    this.dialogTitle = 'Add Business'
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
