<template>
  <BaseAddress
    ref="baseAddress"
    :editing="editing"
    :schema="schema"
    :address="inputaddress"
    @update:address="emitUpdateAddress"
    @valid="emitAddressValidity"
  />
</template>

<script lang="ts">
import { Address, BaseAddressModel } from '@/models/address'
import { PropType, defineComponent, onMounted, ref, watch } from '@vue/composition-api'
import BaseAddress from '@bcrs-shared-components/base-address/BaseAddress.vue'
import CommonUtils from '@/util/common-util'

export default defineComponent({
  name: 'BaseAddressForm',
  components: {
    BaseAddress
  },
  props: {
    editing: {
      type: Boolean,
      default: true
    },
    schema: {
      type: Object,
      default: () => ({})
    },
    address: {
      type: Object as PropType<Address>,
      default: () => ({})
    }
  },
  emit: ['valid', 'update:address'],
  setup (props, { emit }) {
    const inputaddress = ref<BaseAddressModel>({} as BaseAddressModel)

    function loadAddressIntoInputAddress () {
      // convert to address format to component
      inputaddress.value = CommonUtils.convertAddressForComponent(props.address)
      emitUpdateAddress(inputaddress.value)
    }

    function emitUpdateAddress (iaddress: BaseAddressModel): Address {
      // convert back to Address
      const address = CommonUtils.convertAddressForAuth(iaddress)
      emit('update:address', address)
      return address
    }

    function emitAddressValidity (isValid: boolean) {
      emit('valid', isValid)
      return isValid
    }

    function watchEditing (editing: boolean) {
      if (!editing) {
        loadAddressIntoInputAddress()
      }
    }

    // Watch the editing prop
    watch(() => props.editing, watchEditing)

    // Watch the address prop
    watch(() => props.address, () => {
      loadAddressIntoInputAddress()
    })

    onMounted(() => {
      if (props.address) {
        loadAddressIntoInputAddress()
      }
    })

    return {
      inputaddress,
      loadAddressIntoInputAddress,
      emitUpdateAddress,
      emitAddressValidity
    }
  }
})
</script>

<style lang="scss" scoped></style>
