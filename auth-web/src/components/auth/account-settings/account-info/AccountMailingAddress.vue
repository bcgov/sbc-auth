<template>
  <v-card elevation="0">
    <div class="account-label" v-can:VIEW_ADDRESS.disable>
      <!-- template warpper is required here inorder to keep the placement of divs correctly(to resolve flickering issue when updating the address) -->
      <div class="nav-list-title font-weight-bold">Mailing Address</div>

      <template v-if="baseAddress">
        <div class="details">
          <div class="with-change-icon">
            <div class="mb-3">
              <base-address-form
                ref="mailingAddress"
                :editing="!viewOnly"
                :schema="baseAddressSchema"
                :address="baseAddress"
                @update:address="updateAddress"
                @valid="checkBaseAddressValidity"
              />
            </div>
            <div v-can:CHANGE_ADDRESS.disable v-if="viewOnly">
              <span
                class="primary--text cursor-pointer"
                @click="toggleEdit(false)"
                data-test="btn-edit"
              >
                <v-icon color="primary" size="20"> mdi-pencil</v-icon>
                Change
              </span>
            </div>
          </div>
          <v-card-actions class="pt-1 pr-0" v-if="!viewOnly">
            <v-spacer></v-spacer>
            <v-btn
              large
              class="save-btn px-9"
              color="primary"
              :loading="false"
              aria-label="Save Account Information"
              @click="saveAddressUpdate()"
            >
              <span class="save-btn__label">Save</span>
            </v-btn>
            <v-btn
              outlined
              large
              depressed
              class="ml-2 px-9"
              color="primary"
              aria-label="Cancel"
              @click="toggleEdit(true)"
              data-test="cancel-button"
              >Cancel</v-btn
            >
          </v-card-actions>
        </div>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import { addressSchema } from '@/schemas'

@Component({
  components: {
    BaseAddressForm
  }
})
export default class AccountMailingAddress extends Vue {
  @Prop({ default: null }) baseAddress: any
  public viewOnly = true
  public baseAddressSchema: {} = addressSchema

  $refs: {
    mailingAddress: HTMLFormElement
  }

  toggleEdit (value) {
    this.viewOnly = value
  }

  /** Emits an update message, so that we can sync with parent */
  @Emit('update:address')
  public updateAddress (address) {
    return address
  }

  @Emit('valid')
  public checkBaseAddressValidity (isValid) {
    return isValid
  }

  @Emit('update:updateDetails')
  public saveAddressUpdate () {}
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.view-container {
  padding: 0 !important;
}
</style>
