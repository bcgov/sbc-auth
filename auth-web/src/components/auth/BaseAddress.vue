<template>
  <v-form ref="adress" lazy-validation>
    <h4 class="mb-2">Mailing Address</h4>
    <v-row>
      <v-col cols="12" class="py-0 mb-4">
        <v-text-field
                filled
                @change="emitAddress"
                label="Street Address"
                v-model.trim="address.line1"
                :rules="rules.streetAddress"
                req
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4" class="py-0 mb-4">
        <v-text-field
                filled
                label="City"
                @change="emitAddress"
                v-model.trim="address.city"
                :rules="rules.city"
                req
        >
        </v-text-field>
      </v-col>
      <v-col cols="4" class="py-0 mb-4">
        <v-text-field
                filled
                label="Province/Region/State"
                v-model.trim="address.province"
                @change="emitAddress"
                :rules="rules.province"
                req
        >
        </v-text-field>
      </v-col>
      <v-col cols="4" class="py-0 mb-4">
        <v-text-field
                filled
                label="Postal Code"
                v-model.trim="address.postalCode"
                @change="emitAddress"
                :rules="rules.postalCode"
                req
        >
        </v-text-field>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="4" class="py-0 mb-4">
        <v-text-field
                filled
                label="Country"
                v-model.trim="address.country"
                @change="emitAddress"
                :rules="rules.country"
                req
        >
        </v-text-field>
      </v-col>
    </v-row>
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
  private address:Address = { line1: '', city: '', country: 'Canada', postalCode: '', province: '', line2: '' } // TODO probably dont need this intialisation

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
}
</script>

<style lang="scss" scoped>
</style>
