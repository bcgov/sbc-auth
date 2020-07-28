<template>
  <v-form ref="notaryInformationForm">
    <fieldset v-if="notaryInfo">
      <legend class="mb-4">Notary Information</legend>
      <v-row>
        <v-col cols="12" class="py-0">
          <v-text-field
            filled
            label="Name of Notary"
            :rules="rules.notaryName"
            :disabled="disabled"
            v-model.trim="notaryInfo.notaryName"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <base-address
        ref="notaryAddress"
        :editing="true"
        :schema="notaryAddressSchema"
        :address="notaryAddress"
        @update:address="updateNotaryAddress"
        @valid="notaryAddressValidity"
      />
    </fieldset>
  </v-form>
</template>

<script lang="ts">
import { Address, IAddress } from '@/models/address'
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import BaseAddress from 'sbc-common-components/src/components/BaseAddress.vue'
import { NotaryInformation } from '@/models/notary'
import { addressSchema } from '@/schemas'

@Component({
  components: {
    BaseAddress
  }
})
export default class NotaryInformationForm extends Vue {
  @Prop() inputNotaryInfo: NotaryInformation
  @Prop({ default: false }) disabled: boolean
  private notaryInfo: NotaryInformation = {}
  private isNotaryAddressValid: boolean = false

  private notaryAddress: IAddress = {} as IAddress
  private notaryAddressSchema: {} = addressSchema

  $refs: {
    notaryInformationForm: HTMLFormElement,
  }

  private readonly rules = {
    notaryName: [v => !!v || 'Name of Notary is required']
  }

  private updateNotaryAddress (val) {
    this.notaryInfo.address = { ...val }
    return this.emitNotaryInformation()
  }

  private notaryAddressValidity (isValid: boolean) {
    this.isNotaryAddressValid = isValid
    this.emitNotaryInformation()
  }

  mounted () {
    if (this.inputNotaryInfo) {
      Object.keys(this.inputNotaryInfo)
        .filter(key => key !== 'address')
        .forEach(key => {
          this.$set(this.notaryInfo, key, this.inputNotaryInfo?.[key])
        })
      this.notaryAddress = { ...this.inputNotaryInfo?.address }
    }
  }

  @Watch('notaryInfo', { deep: true })
  async updateNotary (val, oldVal) {
    this.emitNotaryInformation()
  }

  @Emit('notaryinfo-update')
  emitNotaryInformation () {
    this.isFormValid()
    return this.notaryInfo
  }

  @Emit('is-form-valid')
  isFormValid () {
    return this.$refs.notaryInformationForm?.validate() && this.isNotaryAddressValid
  }
}
</script>

<style lang="scss" scoped></style>
