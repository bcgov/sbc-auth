<template>
    <section v-if="currentOrganizationGLInfo && canSelect">
        <h2 class="mb-5">{{`${tabNumber !== null ?  `${tabNumber}. ` : ''} ${title}`}}</h2>

        <v-row>
            <v-col class="cols-12 col-sm-3 py-2">Client Code</v-col>
            <v-col class="py-2" data-test='payment-info-client'>{{ currentOrganizationGLInfo.client }}</v-col>
        </v-row>
        <v-row>
            <v-col class="cols-12 col-sm-3 py-2">Responsibility Centre</v-col>
            <v-col class="py-2" data-test='payment-info-responsibilityCentre'>{{ currentOrganizationGLInfo.responsibilityCentre }}</v-col>
        </v-row>
        <v-row>
            <v-col class="cols-12 col-sm-3 py-2">Account Number</v-col>
            <v-col class="py-2" data-test='payment-info-serviceLine'>{{ currentOrganizationGLInfo.serviceLine }}</v-col>
        </v-row>
        <v-row>
            <v-col class="cols-12 col-sm-3 py-2">Standard Object</v-col>
            <v-col class="py-2" data-test='payment-info-stob'>{{ currentOrganizationGLInfo.stob }}</v-col>
        </v-row>
        <v-row>
            <v-col class="cols-12 col-sm-3 py-2">Project</v-col>
            <v-col class="py-2" data-test='payment-info-projectCode'>{{ currentOrganizationGLInfo.projectCode }}</v-col>
        </v-row>
    </section>
    <section v-else-if="currentOrganizationGLInfo">
        <v-row>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Client Code"
              v-model="currentOrganizationGLInfo.client"
              :disabled= "!canSelect"
            ></v-text-field>
          </v-col>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Responsibility Center"
              v-model="currentOrganizationGLInfo.responsibilityCentre"
              :disabled= "!canSelect"
            ></v-text-field>
          </v-col>
            <v-col cols="4" class="py-0">
            <v-text-field
              label="Account Number"
              v-model="currentOrganizationGLInfo.serviceLine"
              :disabled= "!canSelect"
            ></v-text-field>
          </v-col>
          <v-col cols="4" class="py-0">
            <v-text-field
              label="Standard Object"
              v-model="currentOrganizationGLInfo.stob"
              :disabled= "!canSelect"
              >
            ></v-text-field>
          </v-col>
            <v-col cols="8" class="py-0">
            <v-text-field
              label="Project"
              v-model="currentOrganizationGLInfo.projectCode"
              :disabled= "!canSelect"
              >
            ></v-text-field>
          </v-col>
        </v-row>
    </section>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import { GLInfo } from '@/models/Organization'

@Component({})
export default class PaymentInformation extends Vue {
    @Prop({ default: null }) private tabNumber: number
    @Prop({ default: null }) private currentOrganizationGLInfo: GLInfo
    @Prop({ default: 'Payment Information' }) private title: string
    @Prop({ default: false }) private canSelect: boolean
}
</script>
