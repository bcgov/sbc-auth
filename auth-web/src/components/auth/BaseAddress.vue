<template>
  <v-form ref="baseAddressForm" lazy-validation>
    <fieldset v-if="address" v-can:CHANGE_ADDRESS.hide>
      <v-row>
        <v-col cols="12" class="py-0">
          <v-text-field
            filled
            req
            label="Street Address"
            :rules="rules.streetAddress"
            :disabled="disabled"
            v-model.trim="address.street"
            @keydown="emitKeyDown"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            req
            label="City"
            :disabled="disabled"
            :rules="rules.city"
            v-model.trim="address.city"
            @keydown="emitKeyDown"
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            req
            label="Province"
            :disabled="disabled"
            :rules="rules.province"
            v-model.trim="address.region"
            @keydown="emitKeyDown"
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            req
            label="Postal Code"
            :disabled="disabled"
            :rules="rules.postalCode"
            v-model.trim="address.postalCode"
            @keydown="emitKeyDown"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            req
            label="Country"
            :disabled="disabled"
            :rules="rules.country"
            v-model.trim="address.country"
            @keydown="emitKeyDown"
          >
          </v-text-field>
        </v-col>
      </v-row>
    </fieldset>
    <div class="value value__title" aria-labelledby="mailingAddress" v-if="address" v-can:VIEW_ADDRESS.hide>
      <div>{{ address.street }}</div>
      <div v-if="address.streetAdditional">{{ address.streetAdditional }}</div>
      <div>{{ address.city }}, {{ address.region }}  {{ address.postalCode }}</div>
      <div>{{ address.country}}</div>
    </div>
  </v-form>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator'
import { Address } from '@/models/address'

@Component({
  name: 'Address'
})
export default class BaseAddress extends Vue {
  @Prop() inputAddress: Address
  @Prop({ default: false }) disabled: boolean
  private address: Address = {}

  $refs: {
    baseAddressForm: HTMLFormElement,
  }

  private readonly rules = {
    streetAddress: [v => !!v || 'Street address is required'],
    city: [v => !!v || 'City is required'],
    province: [v => !!v || 'Province is required'],
    postalCode: [v => !!v || 'Postal Code is required'],
    country: [v => !!v || 'Country is required']
  }

  mounted () {
    if (this.inputAddress && Object.keys(this.inputAddress).length !== 0) {
      // directly setting to address probelamatic bcoz of vues reactivity
      Object.keys(this.inputAddress).forEach(key => {
        this.$set(this.address, key, this.inputAddress?.[key])
      })
      // emit the address in the next tick to avoid validation function to execute correctly
      // while populating the component without user inputs
      this.$nextTick(() => {
        this.emitAddress()
      })
    }
  }

  @Watch('address', { deep: true })
  async updateAddress (val, oldVal) {
    this.emitAddress()
  }

  @Emit('address-update')
  emitAddress () {
    this.isFormValid()
    return this.address
  }

  @Emit('key-down')
  emitKeyDown () {
    this.isFormValid()
  }

  @Emit('is-form-valid')
  isFormValid () {
    return this.$refs.baseAddressForm?.validate()
  }
}
</script>

<style lang="scss" scoped></style>
