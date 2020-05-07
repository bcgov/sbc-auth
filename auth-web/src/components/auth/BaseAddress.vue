<template>
  <v-form ref="adress" lazy-validation>
    <fieldset v-if="address">
      <legend class="mb-4">Mailing Address</legend>
      <v-row>
        <v-col cols="12" class="py-0">
          <v-text-field
            :disabled="disabled"
            filled
            @change="emitAddress"
            @keydown="emitKeyDown"
            label="Street Address"
            v-model.trim="address.street"
            :rules="rules.streetAddress"
            req
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4" class="py-0">
          <v-text-field
            :disabled="disabled"
            filled
            label="City"
            @change="emitAddress"
            @keydown="emitKeyDown"
            v-model.trim="address.city"
            :rules="rules.city"
            req
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0">
          <v-text-field
            :disabled="disabled"
            filled
            label="Province/Region/State"
            v-model.trim="address.region"
            @change="emitAddress"
            @keydown="emitKeyDown"
            :rules="rules.province"
            req
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0">
          <v-text-field
            :disabled="disabled"
            filled
            label="Postal Code"
            v-model.trim="address.postalCode"
            @change="emitAddress"
            @keydown="emitKeyDown"
            :rules="rules.postalCode"
            req
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4" class="py-0">
          <v-text-field
            :disabled="disabled"
            filled
            label="Country"
            v-model.trim="address.country"
            @change="emitAddress"
            @keydown="emitKeyDown"
            :rules="rules.country"
            req
          >
          </v-text-field>
        </v-col>
      </v-row>
    </fieldset>
  </v-form>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { Address } from '@/models/address'

@Component({
  name: 'Address'
})
export default class BaseAddress extends Vue {
  private username = ''
  private password = ''
  private errorMessage: string = ''
  @Prop() inputAddress: Address
  @Prop() disabled = false
  private address: Address = {
    streetAdditional: '',
    city: '',
    country: 'Canada',
    postalCode: '',
    region: '',
    street: ''
  } // TODO probably dont need this intialisation

  private readonly rules = {
    streetAddress: [v => !!v || 'Street address is required'],
    city: [v => !!v || 'City is required'],
    province: [v => !!v || 'Province is required'],
    postalCode: [v => !!v || 'Postal Code is required'],
    country: [v => !!v || 'Country is required']
  }

  mounted () {
    if (this.inputAddress) {
      this.address = { ...this.inputAddress }
    }
  }

  @Emit('address-update')
  emitAddress () {
    return this.address
  }

  @Emit('key-down')
  emitKeyDown () {}
}
</script>

<style lang="scss" scoped></style>
