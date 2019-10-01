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

    <!-- Add Business Dialog -->
    <ModalDialog
      ref="addBusinessDialog"
      :is-persistent="true"
      :title="dialogTitle"
      :show-icon=false
      :show-actions=false
    >
      <template v-slot:text>
        <p>Enter your Incorporation Number and Passcode.</p>
        <AddBusinessForm class="mt-7"
          @add-success="showAddSuccessModal()"
          @add-failed-invalid-code="showInvalidCodeModal()"
          @add-failed-no-entity="showEntityNotFoundModal()"
          @cancel="cancelAddBusiness()"
        />
      </template>
    </ModalDialog>

    <!-- Success Dialog -->
    <ModalDialog
      ref="successDialog"
      :title="dialogTitle"
      :text="dialogText"
    />

    <!-- Error Dialog -->
    <ModalDialog
      ref="errorDialog"
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
        <v-btn large color="primary" @click="remove()">Remove</v-btn>
        <v-btn large color="default" @click="cancelConfirmDelete()">Cancel</v-btn>
      </template>
    </ModalDialog>

  </div>
</template>

<script lang="ts">
import { Vue, Component } from 'vue-property-decorator'
import AddBusinessForm from '@/components/auth/AddBusinessForm.vue'
import AffiliatedEntityList from '@/components/auth/AffiliatedEntityList.vue'
import UserModule from '@/store/modules/user'
import BusinessModule from '@/store/modules/business'
import { RemoveBusinessPayload } from '@/models/Organization'
import ModalDialog from '@/components/auth/ModalDialog.vue'
import { mapActions } from 'vuex'
import { getModule } from 'vuex-module-decorators'

@Component({
  components: {
    AddBusinessForm,
    AffiliatedEntityList,
    ModalDialog
  },
  methods: {
    ...mapActions('business', ['removeBusiness'])
  }
})
export default class EntityManagement extends Vue {
  private businessStore = getModule(BusinessModule, this.$store)
  private removeBusinessPayload = null
  private dialogTitle = ''
  private dialogText = ''

  private readonly removeBusiness!: (removeBusinessPayload: RemoveBusinessPayload) => void

  $refs: {
    successDialog: ModalDialog
    errorDialog: ModalDialog
    confirmDeleteDialog: ModalDialog
    addBusinessDialog: ModalDialog
  }

  showAddSuccessModal () {
    this.$refs.addBusinessDialog.close()
    this.dialogTitle = 'Business Added'
    this.dialogText = 'You have successfully added a business'
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

  remove () {
    this.removeBusiness(this.removeBusinessPayload)
    this.$refs.confirmDeleteDialog.close()
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
