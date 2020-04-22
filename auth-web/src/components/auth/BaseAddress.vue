<template>
  <v-form ref="adress" lazy-validation>
    <h4 class="mb-2">Mailing Address</h4>
    <v-row>
      <v-col cols="12" class="py-0 mb-4">
        <v-text-field
                filled
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
                req
        >
        </v-text-field>
      </v-col>
      <v-col cols="4" class="py-0 mb-4">
        <v-text-field
                filled
                label="Postal Code"
                v-model.trim="address.postalCode"
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
                req
        >
        </v-text-field>
      </v-col>
    </v-row>
  </v-form>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { Address } from '@/models/address'

@Component({
  name: 'Address'
})
export default class BaseAddress extends Vue {
  private username = ''
  private password = ''
  private errorMessage: string = ''
  @Prop() address: Address
}
</script>

<style lang="scss" scoped>
</style>
