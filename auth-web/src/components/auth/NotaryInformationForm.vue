<template>
  <v-form ref="notaryInformationForm" lazy-validation>
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
            @change="emitNotaryInformation"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="py-0">
          <v-text-field
            filled
            label="Street Address"
            :rules="rules.streetAddress"
            :disabled="disabled"
            v-model.trim="notaryInfo.street"
            @change="emitNotaryInformation"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            label="City"
            :disabled="disabled"
            :rules="rules.city"
            v-model.trim="notaryInfo.city"
            @change="emitNotaryInformation"
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            label="Province"
            :disabled="disabled"
            :rules="rules.province"
            v-model.trim="notaryInfo.region"
            @change="emitNotaryInformation"
          >
          </v-text-field>
        </v-col>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            label="Postal Code"
            :disabled="disabled"
            :rules="rules.postalCode"
            v-model.trim="notaryInfo.postalCode"
            @change="emitNotaryInformation"
          >
          </v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="4" class="py-0">
          <v-text-field
            filled
            label="Country"
            :disabled="disabled"
            :rules="rules.country"
            v-model.trim="notaryInfo.country"
            @change="emitNotaryInformation"
          >
          </v-text-field>
        </v-col>
      </v-row>
    </fieldset>
  </v-form>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { NotaryInformation } from '@/models/notary'

@Component
export default class NotaryInformationForm extends Vue {
  @Prop() inputNotaryInfo: NotaryInformation
  @Prop({ default: false }) disabled: boolean
  private notaryInfo: NotaryInformation = {}

  $refs: {
    notaryInformationForm: HTMLFormElement,
  }

  private readonly rules = {
    notaryName: [v => !!v || 'Name of Notary is required'],
    streetAddress: [v => !!v || 'Street notaryInfo is required'],
    city: [v => !!v || 'City is required'],
    province: [v => !!v || 'Province is required'],
    postalCode: [v => !!v || 'Postal Code is required'],
    country: [v => !!v || 'Country is required']
  }

  mounted () {
    if (this.inputNotaryInfo) {
      Object.keys(this.inputNotaryInfo).forEach(key => {
        this.$set(this.notaryInfo, key, this.inputNotaryInfo?.[key])
      })
    }
  }

  @Emit('notaryinfo-update')
  emitNotaryInformation () {
    this.isFormValid()
    return this.notaryInfo
  }

  @Emit('is-form-valid')
  isFormValid () {
    return this.$refs.notaryInformationForm.validate()
  }
}
</script>

<style lang="scss" scoped></style>
