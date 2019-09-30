<template>
  <div class="entity-mgmt-view">
    <header class="view-header mt-1 mb-9">
      <h1>Manage Businesses</h1>
      <div class="view-header__actions">
        <v-btn outlined color="primary" @click="showAddBusinessModal()">
          <v-icon>add</v-icon>
          <span>Add Business</span>
        </v-btn>
      </div>
    </header>

    <AffiliatedEntityList
      @add-business="showAddBusinessModal()"
      @remove-business="showConfirmRemoveModal($event)"
    />

    <!-- Add Business Modal -->
    <v-dialog content-class="add-business-dialog" v-model="isBusinessModalVisible" persistent>
      <v-card>
        <v-card-title class="d-flex">
          Add Business
          <!-- TODO: We need to standardize how we are leveraging dialogs (See InviteUsersform.vue) -->
          <!--
          <v-btn large icon>
            <v-icon @click="cancel()">close</v-icon>
          </v-btn>
          -->
        </v-card-title>
        <v-card-text>
          <p>Enter your Incorporation Number and Passcode.</p>
          <AddBusinessForm class="mt-7"
            @add-success="showAddSuccessModal()"
            @add-failed-invalid-code="showInvalidCodeModal()"
            @add-failed-no-entity="showEntityNotFoundModal()"
            @cancel="cancelModal()"
          >
          </AddBusinessForm>
        </v-card-text>
      </v-card>
    </v-dialog>

  <!-- 200 - Dialog for home -->
  <ModalDialog
    ref="successDialog"
    :title="dialogTitle"
    :text="dialogText"
  />

  <!-- 401 - Dialog for code not valid -->
  <ModalDialog
    ref="invalidCodeDialog"
    :title="dialogTitle"
    :text="dialogText"
  >
    <template v-slot:icon>
      <v-icon large color="error">error</v-icon>
    </template>
  </ModalDialog>

  <!-- 404 - Dialog for entity not found -->
  <ModalDialog
    ref="entityNotFoundDialog"
    :title="dialogTitle"
    :text="dialogText"
  >
    <template v-slot:icon>
      <v-icon large color="error">error</v-icon>
    </template>
  </ModalDialog>

  <!-- Dialog for confirming business removal -->
  <ModalDialog
    ref="confirmDeleteDialog"
    :title="dialogTitle"
    :text="dialogText"
  >
    <template v-slot:icon>
      <v-icon large color="error">error</v-icon>
    </template>
    <template v-slot:actions>
      <v-btn large color="primary" @click="removeBusiness()">Remove</v-btn>
      <v-btn large color="default" @click="cancelConfirmDelete()">Cancel</v-btn>
    </template>
  </ModalDialog>

  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import AddBusinessForm from '@/components/auth/AddBusinessForm.vue'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'
import AlertDialogContent from '@/components/AlertDialogContent.vue'
import { getModule } from 'vuex-module-decorators'
import UserModule from '@/store/modules/user'
import businessServices from '@/services/business.services'
import BusinessModule from '@/store/modules/business'
import { RemoveBusinessPayload } from '@/models/Organization'
import ModalDialog from '@/components/auth/ModalDialog.vue'

@Component({
  components: {
    AddBusinessForm,
    AffiliatedEntityList,
    AlertDialogContent,
    ModalDialog
  }
})
export default class EntityManagement extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private businessStore = getModule(BusinessModule, this.$store)
  private isBusinessModalVisible = false
  private isResultDialogVisible = false
  private isConfirmDeleteModalVisible = false
  private addSuccess = false
  private invalidPassCode = false
  private entityNotFound = false
  private removeBusinessPayload = null

  private dialogTitle = ''
  private dialogText = ''

  $refs: {
    successDialog: ModalDialog
    invalidCodeDialog: ModalDialog
    entityNotFoundDialog: ModalDialog
    confirmDeleteDialog: ModalDialog
  }

  showAddSuccessModal () {
    this.isBusinessModalVisible = false
    this.dialogTitle = 'Business Added'
    this.dialogText = 'You have successfully added a business'
    this.$refs.successDialog.open()
  }

  showInvalidCodeModal () {
    this.isBusinessModalVisible = false
    this.dialogTitle = 'Invalid Passcode'
    this.dialogText = 'Unable to add the business. The provided Passcode is invalid or already in use.'
    this.$refs.invalidCodeDialog.open()
  }

  showEntityNotFoundModal () {
    this.isBusinessModalVisible = false
    this.dialogTitle = 'Business Not Found'
    this.dialogText = 'The specified business was not found.'
    this.$refs.entityNotFoundDialog.open()
  }

  showAddBusinessModal () {
    this.isBusinessModalVisible = true
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

  removeBusiness () {
    this.businessStore.removeBusiness(this.removeBusinessPayload)
    this.isConfirmDeleteModalVisible = false
  }
}
</script>

<style lang="scss">
  @import '../../assets/scss/theme.scss';

  .add-business-dialog {
    max-width: 40rem;
    width: 40rem;
  }

  // Notification Dialog (Success/Error)
  .notify-dialog {
    max-width: 30rem;

    .v-card__title {
      flex-direction: column;
    }

    .v-card__actions {
      justify-content: center;
    }
  }
</style>
