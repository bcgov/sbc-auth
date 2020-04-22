<template>
  <v-form ref="adress" lazy-validation>
    <h4 class="mb-2">Mailing Address</h4>
    <v-row>
      <v-col cols="12" class="py-0 mb-4">
        <v-text-field
                filled
                v-on:change="emitAddress()"
                label="Street Address"
                v-model.trim="address.line1"
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
                v-on:change="emitAddress()"
                v-model.trim="address.city"
                req
        >
        </v-text-field>
      </v-col>
      <v-col cols="4" class="py-0 mb-4">
        <v-text-field
                filled
                label="Province/Region/State"
                v-model.trim="address.province"
                v-on:change="emitAddress()"
                req
        >
        </v-text-field>
      </v-col>
      <v-col cols="4" class="py-0 mb-4">
        <v-text-field
                filled
                label="Postal Code"
                v-model.trim="address.postalCode"
                v-on:change="emitAddress()"
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
                v-on:change="emitAddress()"
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

  mounted () {
    if (this.inputAddress) {
      this.address = this.inputAddress
    }
  }

  @Emit('adress-update')
  emitAddress () {
    return this.address
  }
}
</script>

<style lang="scss" scoped>
</style>
