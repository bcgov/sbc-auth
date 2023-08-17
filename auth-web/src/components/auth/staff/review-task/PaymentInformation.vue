<template>
  <div>
    <h2 class="mb-5">
      {{ `${tabNumber !== null ? `${tabNumber}. ` : ''} ${title}` }}
    </h2>
    <section v-if="currentOrganizationGLInfo">
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">
          Client Code
        </v-col>
        <v-col
          class="py-2"
          data-test="payment-info-client"
        >
          {{ currentOrganizationGLInfo.client }}
        </v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">
          Responsibility Centre
        </v-col>
        <v-col
          class="py-2"
          data-test="payment-info-responsibilityCentre"
        >
          {{ currentOrganizationGLInfo.responsibilityCentre }}
        </v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">
          Account Number
        </v-col>
        <v-col
          class="py-2"
          data-test="payment-info-serviceLine"
        >
          {{ currentOrganizationGLInfo.serviceLine }}
        </v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">
          Standard Object
        </v-col>
        <v-col
          class="py-2"
          data-test="payment-info-stob"
        >
          {{ currentOrganizationGLInfo.stob }}
        </v-col>
      </v-row>
      <v-row>
        <v-col class="cols-12 col-sm-3 py-2">
          Project
        </v-col>
        <v-col
          class="py-2"
          data-test="payment-info-projectCode"
        >
          {{ currentOrganizationGLInfo.projectCode }}
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { GLInfo } from '@/models/Organization'

@Component({})
export default class PaymentInformation extends Vue {
    @Prop({ default: null }) tabNumber: number
    @Prop({ default: null }) currentOrganizationGLInfo: GLInfo
    @Prop({ default: 'Payment Information' }) title: string
}
</script>
