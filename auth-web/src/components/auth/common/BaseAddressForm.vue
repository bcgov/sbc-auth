<template>
  <base-address
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
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import BaseAddress from 'sbc-common-components/src/components/BaseAddress.vue'
import CommonUtils from '@/util/common-util'

@Component({
  components: {
    BaseAddress
  }
})
export default class BaseAddressForm extends Vue {
  @Prop({ default: true }) editing: boolean
  @Prop({ default: {} }) schema: any
  @Prop({ default: () => ({} as Address) }) address: Address
  private inputaddress: BaseAddressModel = {} as BaseAddressModel

  mounted () {
    if (this.address) {
      this.loadAddressIntoInputAddress()
    }
  }

  @Watch('editing')
  private watchEditing (editing) {
    if (!editing) {
      this.loadAddressIntoInputAddress()
    }
  }

  @Emit('update:address')
  private emitUpdateAddress (iaddress): Address {
    // convert back to Address
    const address = CommonUtils.convertAddressForAuth(iaddress)
    return address
  }

  @Emit('valid')
  emitAddressValidity (isValid) {
    return isValid
  }

  loadAddressIntoInputAddress () {
    // convert to address format to component
    this.inputaddress = CommonUtils.convertAddressForComponent(this.address)
    this.emitUpdateAddress(this.inputaddress)
  }
}
</script>

<style lang="scss" scoped></style>
