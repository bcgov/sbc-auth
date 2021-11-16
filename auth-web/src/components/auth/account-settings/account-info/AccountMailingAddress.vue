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
                :editing="!viewOnlyMode"
                :schema="baseAddressSchema"
                :address="baseAddress"
                @update:address="updateAddress"
                @valid="checkBaseAddressValidity"
                :key="baseAddress.postalCode"
              />
            </div>
            <div v-can:CHANGE_ADDRESS.disable v-if="viewOnlyMode">
              <span
                class="primary--text cursor-pointer"
                @click="$emit('update:viewOnlyMode', {component:'address',mode:false })"
                data-test="btn-edit"
              >
                <v-icon color="primary" size="20"> mdi-pencil</v-icon>
                Change
              </span>
            </div>
          </div>
          <v-card-actions class="pt-1 pr-0" v-if="!viewOnlyMode">
            <v-spacer></v-spacer>
            <v-btn
              large
              class="save-btn px-9"
              color="primary"
              :loading="false"
              aria-label="Save Account Information"
              @click="$emit('update:updateDetails')"
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
              @click="$emit('update:viewOnlyMode', {component:'address',mode:true })"

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
  @Prop({ default: true }) viewOnlyMode: boolean

  public baseAddressSchema: {} = addressSchema

  $refs: {
    mailingAddress: HTMLFormElement
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

  triggerValidate (): boolean {
    // validate form fields and show error message for address component from sbc-common-component
    return this.$refs.mailingAddress?.$refs.baseAddress?.$refs.addressForm?.validate()
  }
}
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.view-container {
  padding: 0 !important;
}
</style>
