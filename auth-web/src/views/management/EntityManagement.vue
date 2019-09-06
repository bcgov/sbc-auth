<template>
  <div>
    <div class="header">
      <h2>Manage Businesses</h2>
      <v-btn class="add-business-btn" color="primary" @click="showAddBusinessModal()">
        Add Business
      </v-btn>
    </div>

    <AffiliatedEntityList
      @add-business="showAddBusinessModal()"
      @remove-business="showConfirmRemoveModal($event)"
    />

    <!-- Add Business Modal -->
    <v-dialog v-model="isBusinessModalVisible" persistent max-width="400px">
      <v-card>
        <v-card-title>
          <h2>Add Business</h2>
          <p>Please enter your incorporation number and passcode below.</p>
        </v-card-title>
        <v-card-text>
          <AddBusinessForm
            @add-success="showAddSuccessModal()"
            @add-failed-invalid-code="showInvalidCodeModal()"
            @cancel="cancelModal()"
          >
          </AddBusinessForm>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- Success/Fail Model -->
    <v-dialog v-model="isResultDialogVisible" persistent max-width="400px">
      <v-card>
        <v-card-title>
          <h2 v-show="addSuccess">Success</h2>
          <h2 v-show="!addSuccess">Invalid Passcode</h2>
        </v-card-title>
        <v-card-text v-show="addSuccess">You have successfully added a business</v-card-text>
        <v-card-text v-show="!addSuccess">The business was unable to be added due to the provided passcode being invalid or already in use</v-card-text>
        <v-card-actions>
          <v-flex class="text-xs-right">
            <v-btn color="primary" @click="isResultDialogVisible = false">Okay</v-btn>
          </v-flex>
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
  .header {
    display: flex;
    justify-content: space-between
  }

  .add-business-btn {
    margin-right: 1.5em
  }

  .okay-button {
    margin-left: auto
  }
</style>
