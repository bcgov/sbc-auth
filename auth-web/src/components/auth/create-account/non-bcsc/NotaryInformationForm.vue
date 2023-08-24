<template>
  <v-form ref="notaryInformationForm">
    <fieldset v-if="notaryInfo">
      <legend class="mb-4">
        Notary Information
      </legend>
      <v-row>
        <v-col
          cols="12"
          class="py-0"
        >
          <v-text-field
            v-model.trim="notaryInfo.notaryName"
            filled
            label="Name of Notary"
            :rules="rules.notaryName"
            :disabled="disabled"
          />
        </v-col>
      </v-row>
      <base-address-form
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
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Address } from '@/models/address'
import BaseAddressForm from '@/components/auth/common/BaseAddressForm.vue'
import { NotaryInformation } from '@/models/notary'
import { addressSchema } from '@/schemas'

@Component({
  components: {
    BaseAddressForm
  }
})
export default class NotaryInformationForm extends Vue {
  @Prop() inputNotaryInfo: NotaryInformation
  @Prop({ default: false }) disabled: boolean
  private notaryInfo: NotaryInformation = {}
  private isNotaryAddressValid: boolean = false

  private notaryAddress: Address = {} as Address
  private notaryAddressSchema = addressSchema

  $refs: {
    notaryInformationForm: HTMLFormElement,
  }

  private readonly rules = {
    notaryName: [v => !!v || 'Name of Notary is required']
  }

  private updateNotaryAddress (val: Address) {
    this.notaryInfo.address = { ...val }
    return this.emitNotaryInformation()
  }

  private notaryAddressValidity (isValid: boolean) {
    this.isNotaryAddressValid = isValid
    this.emitNotaryInformation()
  }

  beforeMount () {
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
  async updateNotary () {
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
