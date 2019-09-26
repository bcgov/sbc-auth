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
            @cancel="cancelModal()"
          >
          </AddBusinessForm>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Success/Fail Model -->
    <v-dialog content-class="notify-dialog text-center" v-model="isResultDialogVisible" persistent>
      
      <!-- Success -->
      <v-card v-show="addSuccess">
        <v-card-title class="pb-2">
          <v-icon x-large color="success" class="mt-3">check</v-icon>
          <span class="mt-5">Success</span> 
        </v-card-title>
        <v-card-text>
          You have successfully added a business.
        </v-card-text>
        <v-card-actions class="pb-8">
          <v-flex>
            <v-btn color="primary" @click="isResultDialogVisible = false">OK</v-btn>
          </v-flex>
        </v-card-actions>
      </v-card>

      <!-- Fail -->
      <v-card v-show="!addSuccess">
        <v-card-title class="pb-2">
          <v-icon x-large color="error" class="mt-3">error</v-icon>
          <span class="mt-5">Invalid Passcode</span> 
        </v-card-title>
        <v-card-text>
          <p class="mt-5">Unable to add the business. The provided Passcode is invalid or already in use.</p>
        </v-card-text>
        <v-card-actions class="pb-8">
          <v-btn large color="error" @click="isResultDialogVisible = false">OK</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Confirm delete modal -->
    <v-dialog v-model="isConfirmDeleteModalVisible" persistent max-width="400px">
      <v-card>
        <v-card-title>
          <h2>Confirm Remove Business</h2>
        </v-card-title>
        <v-card-text>Are you sure you wish to remove this business?</v-card-text>
        <v-card-actions>
          <v-flex class="text-xs-right">
            <v-btn color="secondary" @click="isConfirmDeleteModalVisible = false">Cancel</v-btn>
            <v-btn color="primary" @click="removeBusiness()">Remove</v-btn>
          </v-flex>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import AddBusinessForm from '@/components/auth/AddBusinessForm.vue'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'
import { getModule } from 'vuex-module-decorators'
import UserModule from '@/store/modules/user'
import businessServices from '@/services/business.services'
import BusinessModule from '@/store/modules/business'
import { RemoveBusinessPayload } from '@/models/Organization'

@Component({
  components: {
    AddBusinessForm,
    AffiliatedEntityList
  }
})
export default class EntityManagement extends Vue {
  private userStore = getModule(UserModule, this.$store)
  private businessStore = getModule(BusinessModule, this.$store)
  isBusinessModalVisible = false
  isResultDialogVisible = false
  isConfirmDeleteModalVisible = false
  addSuccess = false
  removeBusinessPayload = null

  showAddSuccessModal () {
    this.addSuccess = true
    this.isBusinessModalVisible = false
    this.isResultDialogVisible = true
  }

  showInvalidCodeModal () {
    this.addSuccess = false
    this.isBusinessModalVisible = false
    this.isResultDialogVisible = true
  }

  showAddBusinessModal () {
    this.isBusinessModalVisible = true
  }

  showConfirmRemoveModal (removeBusinessPayload: RemoveBusinessPayload) {
    this.removeBusinessPayload = removeBusinessPayload
    this.isConfirmDeleteModalVisible = true
  }

  cancelModal () {
    this.isBusinessModalVisible = false
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
