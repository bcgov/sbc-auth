<template>
  <v-card elevation="0">
    <div
      v-can:VIEW_ADDRESS.disable
      class="account-label"
    >
      <!-- template warpper is required here inorder to keep the placement of divs
            correctly(to resolve flickering issue when updating the address) -->
      <div
        class="nav-list-title font-weight-bold"
        data-test="title"
      >
        Mailing Address
      </div>

      <template v-if="baseAddress">
        <div class="details">
          <div class="with-change-icon">
            <div class="mb-3">
              <BaseAddressForm
                ref="mailingAddress"
                :editing="!viewOnlyMode"
                :schema="baseAddressSchema"
                :address="baseAddress"
                @update:address="updateAddress"
                @valid="checkBaseAddressValidity"
              />
            </div>
            <div
              v-if="viewOnlyMode"
              v-can:CHANGE_ADDRESS.hide
            >
              <span
                v-if="canChangeAddress"
                class="primary--text cursor-pointer"
                data-test="btn-edit"
                @click="$emit('update:viewOnlyMode', {component:'address',mode:false })"
              >
                <v-icon
                  color="primary"
                  size="20"
                > mdi-pencil</v-icon>
                Change
              </span>
            </div>
          </div>
          <v-card-actions
            v-if="!viewOnlyMode"
            class="pt-1 pr-0"
          >
            <v-spacer />
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
              data-test="cancel-button"

              @click="$emit('update:viewOnlyMode', {component:'address',mode:true }); $emit('update:resetAddress')"
            >
              Cancel
            </v-btn>
          </v-card-actions>
        </div>
      </template>
    </div>
  </v-card>
</template>

<script lang="ts">
import { Role } from '@/util/constants'
import { computed, defineComponent, ref } from '@vue/composition-api'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import { addressSchema } from '@/schemas'
import { useUserStore } from '@/stores/user'

export default defineComponent({
  name: 'AccountMailingAddress',
  components: {
    BaseAddressForm
  },
  props: {
    baseAddress: {
      type: Object,
      default: () => null
    },
    viewOnlyMode: {
      type: Boolean,
      default: true
    }
  },
  emit: ['valid', 'update:address'],
  setup (props, { emit }) {
    const { currentUser } = useUserStore()
    const baseAddressSchema = ref(addressSchema)

    const mailingAddress = ref<HTMLFormElement | null>(null)

    const canChangeAddress = computed(() => !currentUser?.roles?.includes(Role.ContactCentreStaff))

    function updateAddress (address) {
      emit('update:address', address)
    }

    function checkBaseAddressValidity (isValid) {
      emit('valid', isValid)
    }

    function triggerValidate (): boolean {
      // validate form fields and show error message for address component from sbc-common-component
      return mailingAddress.value?.$refs.baseAddress?.$refs.addressForm?.validate()
    }

    return {
      baseAddressSchema,
      mailingAddress,
      updateAddress,
      checkBaseAddressValidity,
      triggerValidate,
      canChangeAddress
    }
  }
})
</script>

<style lang="scss" scoped>
@import '$assets/scss/theme.scss';
.view-container {
  padding: 0 !important;
}
</style>
