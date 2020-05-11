<template>
  <v-form ref="adress" lazy-validation>
    <fieldset v-if="address">
      <legend class="mb-4">Mailing Address</legend>
      <v-row>
        <v-col cols="12" class="py-0">
          <v-text-field
            filled
            req
            label="Street Address"
            :rules="rules.streetAddress"
            :disabled="disabled"
            v-model.trim="address.street"
            @change="emitAddress"
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
            @change="emitAddress"
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
            @change="emitAddress"
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
            @change="emitAddress"
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
            @change="emitAddress"
            @keydown="emitKeyDown"
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
