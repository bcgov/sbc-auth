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
  emits: ['valid', 'update:address'],
  setup (props, { emit }) {
    const inputaddress = ref<BaseAddressModel>({} as BaseAddressModel)
    let isUpdating = false

    function loadAddressIntoInputAddress () {
      // convert to address format to component
      if (!isUpdating) {
        inputaddress.value = CommonUtils.convertAddressForComponent(props.address)
      }
    }

    function addressesAreEqual(addr1: BaseAddressModel, addr2: BaseAddressModel): boolean {
      return Object.keys(addr1).every(key => {
        return (addr1 as any)[key] === (addr2 as any)[key]
      })
    }

    function emitUpdateAddress (iaddress: BaseAddressModel): Address {
      const newAddress = CommonUtils.convertAddressForAuth(iaddress)
      if (!isUpdating && !addressesAreEqual(iaddress, inputaddress.value)) {
        isUpdating = true
        emit('update:address', newAddress)
        isUpdating = false
      }
      return newAddress
    }

    function emitAddressValidity (isValid: boolean) {
      emit('valid', isValid)
      return isValid
    }

    watch(() => props.address, (newAddress, oldAddress) => {
      if (JSON.stringify(newAddress) !== JSON.stringify(oldAddress)) {
        loadAddressIntoInputAddress()
      }
    }, { deep: true })

    onMounted(() => {
      loadAddressIntoInputAddress()
    })

    watch(() => props.editing, () => {
      loadAddressIntoInputAddress()
    })

    return {
      inputaddress,
      emitUpdateAddress,
      emitAddressValidity
    }
  }
})
</script>

<style lang="scss" scoped></style>
